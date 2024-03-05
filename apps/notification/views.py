from flask import Blueprint, request, current_app, jsonify, render_template
import requests
from flask_login import login_required, current_user
from apps.notification.models import Notification

notification_bp = Blueprint('notification', __name__,  template_folder='templates')

@notification_bp.route('/view', methods=['GET'])
@login_required
def view_notifications():
    notifications = Notification.query.filter_by(user_id=current_user.id)
    return render_template('view_notifications.html', notifications = notifications)

# @notification_bp.route('/exchange-rate/create', methods=['POST'])
# def create_exchange_rate():
#     data = request.json
#     if data is None:
#         return jsonify({'error': 'Invalid JSON payload'}), 400


