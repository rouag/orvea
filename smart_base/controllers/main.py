import json
import openerp
import openerp.http as http
from openerp.http import request
import openerp.addons.web.controllers.main as webmain
import json
from datetime import datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT

class BaseNotification(http.Controller):


    @http.route('/notification/notify', type='json', auth="none")
    def notify(self):
        notification_obj = request.env['base.notification']
        now = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")
        notifications = notification_obj.search([('user_id', '=', request.session.uid), ('to_read', '=', 'True'), ('show_date', '>=', now)])
        all_notif = []
        for notification in notifications:
            all_notif.append({
                'event_id': 1,
                'title': notification.title,
                'message': notification.message,
                'timer': 3600,
                'notify_at': notification.show_date
                }
                             )


        return all_notif

    @http.route('/notification/notify_stop', type='json', auth="none")
    def notify_stop(self):
        return  True
