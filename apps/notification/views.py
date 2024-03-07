from flask import Blueprint, request, current_app, jsonify, render_template
import requests
from flask_login import login_required, current_user
from apps.notification.models import Notification
from apps import db
from .exceptions import DataMissingException

notification_bp = Blueprint('notification', __name__,  template_folder='templates')

@notification_bp.route('/create', methods=['POST'])
@login_required
def create_notifications():
    try:
        from_cur = request.form.get('from_cur')
        to_cur = request.form.get('to_cur')
        alert_type = request.form.get('alert_type')
        period = request.form.get('period')
        condition = request.form.get('condition')
        rate = request.form.get('rate')
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
            rate = 0
            condition = None

        elif alert_type == 'conditionally':
            period = None
            if rate is None or rate=='':
                raise DataMissingException('Input exchange rate to proceed')
        
        new_notification = Notification(user_id = current_user.id, from_cur_code = from_cur, to_cur_code = to_cur, alert_type = alert_type, period = period, condition = condition, rate = rate, notify_in_app = notify_in_app, notify_email =  notify_email, notes = notes, is_enabled = True ) 
        db.session.add(new_notification)
        db.session.commit()
        return jsonify({'message': 'Notification has been set successfully'}), 200

    except DataMissingException as e:
        print(str(e))
        return jsonify({'error': str(e)}), 400

    except Exception as e:
        print(str(e))
        return jsonify({'error': str(e)}), 400


@notification_bp.route('/view', methods=['GET'])
@login_required
def view_notifications():
    notifications = Notification.query.filter_by(user_id=current_user.id)
    return render_template('view_notifications.html', notifications = notifications)

@notification_bp.route('/delete/<id>', methods=['DELETE'])
@login_required
def delete_notifications(id):
    notification = Notification.query.get(id)
    if notification:
        if notification.user_id != current_user.id:
            return jsonify({'error': 'Not authorized to delete this notification'}), 403
        db.session.delete(notification)
        db.session.commit()
        return jsonify({'message': 'Notification deleted successfully'}), 200
    
    else:
        return jsonify({'error': 'Notification not found'}), 404

@notification_bp.route('/toggle/<id>', methods=['PUT'])
@login_required
def toggle_notifications(id):
    notification = Notification.query.get(id)
    if notification:
        if notification.user_id != current_user.id:
            return jsonify({'error': 'Not authorized to delete this notification'}), 403
        notification.is_enabled = not notification.is_enabled
        db.session.commit()
        if notification.is_enabled:
            return jsonify({'message': 'Notification enabled successfully'}), 200
        else:
            return jsonify({'message': 'Notification disabled successfully'}), 200
    
    else:
        return jsonify({'error': 'Notification not found'}), 404

@notification_bp.route('/edit/<id>', methods=['PUT'])
@login_required
def edit_notifications(id):
    notification = Notification.query.get(id)
    if notification:
        if notification.user_id != current_user.id:
            return jsonify({'error': 'Not authorized to delete this notification'}), 403
        
        db.session.commit()
        return jsonify({'message': 'Notification disabled successfully'}), 200
    
    else:
        return jsonify({'error': 'Notification not found'}), 404

@notification_bp.route('/edit-notes/<id>', methods=['PUT'])
@login_required
def edit_notes(id):
    notification = Notification.query.get(id)
    if notification:
        if notification.user_id != current_user.id:
            return jsonify({'error': 'Not authorized to delete this notification'}), 403
        notes = request.json.get('notes')
        notification.notes = notes  
        db.session.commit()
        return jsonify({'message': 'Notes updated successfully'}), 200
    
    else:
        return jsonify({'error': 'Notification not found'}), 404




# @notification_bp.route('/exchange-rate/create', methods=['POST'])
# def create_exchange_rate():
#     data = request.json
#     if data is None:
#         return jsonify({'error': 'Invalid JSON payload'}), 400


