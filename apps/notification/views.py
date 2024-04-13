from flask import Blueprint, request, current_app, jsonify, render_template
import requests
from flask_login import login_required, current_user
from apps.alert.models import Alert
from apps.models import Currency
from apps.notification.models import Notification
from apps.database import db


notification_bp = Blueprint('notification', __name__)

@notification_bp.route('/get-all', methods=['GET'])
@login_required
def get_notifications():
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_time.desc())
    unread_count = Notification.query.filter_by(user_id=current_user.id, has_read=False).count()

    notification_list = []
    for notification in notifications:
        notification_data = {
            'id': notification.id,
            'created_time': notification.created_time.strftime('%Y-%m-%d %H:%M:%S'),
            'title': notification.title,
            'text': notification.text,
            'has_read': notification.has_read,
            'alert_id': notification.alert_id
        }
        notification_list.append(notification_data)
    response_data = {
        'notifications': notification_list,
        'unread_count': unread_count
    }
    return jsonify(response_data)

@notification_bp.route('/read-all', methods=['PUT'])
@login_required
def read_notifications():
    request_json = request.get_json()
    print(request_json)
    notification_ids = request_json.get('ids')
    try:
        for notification_id in notification_ids:
            notification = Notification.query.get(notification_id)
            notification.has_read= True
        db.session.commit()
        return jsonify({'message': 'Read notifications successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400




