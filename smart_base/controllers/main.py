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
        notifications = notification_obj.search([('user_id', '=', request.session.uid), ('to_read', '=', 'True')])
        all_notif = []
        for notification in notifications:
            if not notification.res_action:
                res_action = 'smart_base.action_base_notification'
                res_id = notification.id
            else:
                res_action = notification.res_action
                res_id = notification.res_id
            all_notif.append({
                'notif_id': notification.id,
                'title': notification.title,
                'message': notification.message,
                'res_action': res_action,
                'timer': 5,
                'res_id': res_id,
                'notify_at': notification.show_date
                }
                             )
        return all_notif
#         print datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
#         return [{
#                 'notif_id': 1,
#                 'title': 'resultresultresult',
#                 'message': 'azeazeaze',
#                 'timer': 10,
#                 'notify_at': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
#                 }]

    @http.route('/notification/validate', type='json', auth="user")
    def notify_validate(self, notif_id):
        notification_obj = request.env['base.notification']
        notification = notification_obj.search([('id', '=', int(notif_id))])
        notification.write({'to_read': False})
        return True

