from flask import Blueprint, request, current_app, jsonify, render_template
import requests
from flask_login import login_required, current_user
from apps.alert.models import Alert
from apps.models import Currency
from apps import db


notification_bp = Blueprint('notification', __name__)

# @notification_bp.route('/create', methods=['POST'])
# @login_required
# def view_notifications():



