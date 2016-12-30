import json
import openerp
import openerp.http as http
from openerp.http import request
import openerp.addons.web.controllers.main as webmain
import json
from datetime import datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT

class meeting_invitation(http.Controller):


    @http.route('/notification/notify', type='json', auth="none")
    def notify(self):
        return {}
#         return {
#                 'event_id': 1,
#                 'title': 'test0002',
#                 'message': 'message',
#                 'timer': 3600,
#                 'notify_at': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
#             }

    @http.route('/notification/notify_stop', type='json', auth="none")
    def notify_stop(self):
        return  True