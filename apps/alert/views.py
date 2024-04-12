from flask import Blueprint, request, current_app, jsonify, render_template
import requests
from flask_login import login_required, current_user
from apps.alert.models import Alert
from apps.models import Currency
from apps import db
from .exceptions import DataMissingException

alert_bp = Blueprint('alert', __name__,  template_folder='templates')

@alert_bp.route('/create', methods=['POST'])
@login_required
def create_alert():
    try:
        from_cur = request.form.get('from_cur')
        to_cur = request.form.get('to_cur')
        indicator = request.form.get('indicator')
        alert_type = request.form.get('alert_type')
        period = request.form.get('period')
        condition = request.form.get('condition')
        rate = request.form.get('rate')
        rsi_val = request.form.get('rsi_val')
        notify_in_app = request.form.get('notify_in_app')=="on"
        notify_email = request.form.get('notify_email')=="on"
        notes = request.form.get('notes')

        if from_cur is None:
            raise DataMissingException('Select currency to proceed')
        if to_cur is None:
            raise DataMissingException('Select currency to proceed')
        if not (notify_in_app or notify_email):
            raise DataMissingException('Please check at least one notification method.')
        
        if alert_type == 'periodically':
            rate = None
            rsi_val = None
            condition = None

        elif alert_type == 'conditionally':
            period = None
            if indicator == 'exrate':
                rsi_val = None
                if rate is None or rate=='':
                    raise DataMissingException('Input exchange rate to proceed')
            elif indicator == 'rsi': 
                rate = None
                if rsi_val is None or rsi_val=='':
                    raise DataMissingException('Input rsi value to proceed')
            
        
        new_alert = Alert(user_id = current_user.id, from_cur_code = from_cur, to_cur_code = to_cur, alert_type = alert_type, period = period, condition = condition, rate = rate, notify_in_app = notify_in_app, notify_email =  notify_email, notes = notes, is_enabled = True, rsi_val = rsi_val, indicator = indicator ) 
        db.session.add(new_alert)
        db.session.commit()
        return jsonify({'message': 'Alert has been set successfully'}), 200

    except DataMissingException as e:
        print(str(e))
        return jsonify({'error': str(e)}), 400

    except Exception as e:
        print(str(e))
        return jsonify({'error': str(e)}), 400


@alert_bp.route('/view', methods=['GET'])
@login_required
def view_alerts():
    alerts = Alert.query.filter_by(user_id=current_user.id)
    currencies = Currency.query.all()
    return render_template('view_alerts.html', alerts = alerts, currencies = currencies)

@alert_bp.route('/delete/<id>', methods=['DELETE'])
@login_required
def delete_alert(id):
    alert = Alert.query.get(id)
    if alert:
        if alert.user_id != current_user.id:
            return jsonify({'error': 'Not authorized to delete this alert'}), 403
        db.session.delete(alert)
        db.session.commit()
        return jsonify({'message': 'Alert deleted successfully'}), 200
    
    else:
        return jsonify({'error': 'Alert not found'}), 404

@alert_bp.route('/toggle/<id>', methods=['PUT'])
@login_required
def toggle_alert(id):
    alert = Alert.query.get(id)
    if alert:
        if alert.user_id != current_user.id:
            return jsonify({'error': 'Not authorized to delete this alert'}), 403
        alert.is_enabled = not alert.is_enabled
        db.session.commit()
        if alert.is_enabled:
            return jsonify({'message': 'Alert enabled successfully'}), 200
        else:
            return jsonify({'message': 'Alert disabled successfully'}), 200
    
    else:
        return jsonify({'error': 'Alert not found'}), 404

@alert_bp.route('/edit/<id>', methods=['PUT'])
@login_required
def edit_alert(id):
    alert = Alert.query.get(id)
    if alert:
        if alert.user_id != current_user.id:
            return jsonify({'error': 'Not authorized to edit this alert'}), 403
        
        if alert.alert_type=="periodically":
            period = request.json.get('period')
            alert.period = period
        else:
            condition = request.json.get('condition')
            alert.condition = condition
            if alert.indicator=="exrate":
                rate = request.json.get('value')
                alert.rate = rate

            elif alert.indicator=="rsi":
                rsi_val = request.json.get('value')
                alert.rsi_val = rsi_val

        db.session.commit()
        return jsonify({'message': 'Alert edited successfully'}), 200
    
    else:
        return jsonify({'error': 'Alert not found'}), 404

@alert_bp.route('/edit-notes/<id>', methods=['PUT'])
@login_required
def edit_notes(id):
    alert = Alert.query.get(id)
    if alert:
        if alert.user_id != current_user.id:
            return jsonify({'error': 'Not authorized to delete this alert'}), 403
        notes = request.json.get('notes')
        alert.notes = notes  
        db.session.commit()
        return jsonify({'message': 'Notes updated successfully'}), 200
    
    else:
        return jsonify({'error': 'Alert not found'}), 404




# @alert_bp.route('/exchange-rate/create', methods=['POST'])
# def create_exchange_rate():
#     data = request.json
#     if data is None:
#         return jsonify({'error': 'Invalid JSON payload'}), 400


