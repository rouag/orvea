import json
import openerp
import openerp.http as http
from openerp.http import request
import openerp.addons.web.controllers.main as webmain
import json
from datetime import datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime, date
import time
DT_FMT = '%Y-%m-%d %H:%M:%S'

class BaseNotification(http.Controller):


    @http.route('/notification/notify', type='json', auth="none")
    def notify(self):
        notification_obj = request.env['base.notification']
        now = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")
        notifications = notification_obj.search([('user_id', '=', request.session.uid), ('to_read', '=', True)])
        all_notif = []
        for notification in notifications:
            if not notification.res_action:
                res_action = 'smart_notification.action_base_notification'
                res_id = notification.id
            else:
                res_action = notification.res_action
                res_id = notification.res_id
            date_start = datetime.strptime(notification.show_date, DT_FMT)
            date_now = datetime.now().strftime(DT_FMT)
            date_now = datetime.strptime(date_now, DT_FMT)
            d1_ts = time.mktime(date_start.timetuple())
            d2_ts = time.mktime(date_now.timetuple())
            daysDiff = (d1_ts - d2_ts) / 60
            if int(daysDiff) <= 0 and notification.notif is True:
                all_notif.append({
                        'notif_id': notification.id,
                        'title': notification.title,
                        'message': notification.message,
                        'res_action': res_action,
                        'timer': 1,
                        'res_id': res_id,
                        'notify_at': notification.show_date
                        })
            
            if int(daysDiff) <= 0 and notification.email and notification.first_notif is True and notification.template_id:
                request.env['mail.template'].sudo().browse(notification.template_id.id).send_mail(notification.id)
        return all_notif

    @http.route('/notification/validate', type='json', auth="user")
    def notify_validate(self, notif_id):
        notification_obj = request.env['base.notification']
        notification = notification_obj.search([('id', '=', notif_id)])
        notification.write({'to_read': False, 'first_notif': False})
        return True
    
    @http.route('/notification/snooze', type='json', auth="user")
    def notify_snooze(self, notif_id):
        notification_obj = request.env['base.notification']
        notification = notification_obj.search([('id', '=', notif_id)])
        date_now = datetime.now().strftime(DT_FMT)
        dt_now = datetime.strptime(date_now, "%Y-%m-%d %H:%M:%S")
        next_show_date = (dt_now + timedelta(minutes=notification.interval_between_notif)).strftime(DEFAULT_SERVER_DATETIME_FORMAT),
        notification.write({'show_date': next_show_date, 'first_notif': False})
        return True
