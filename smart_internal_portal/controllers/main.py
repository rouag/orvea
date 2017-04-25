# -*- encoding: utf-8 -*-


import openerp
import openerp.modules.registry

from openerp import http
from openerp.http import request
import werkzeug.utils
import json


class Home(http.Controller):

    @http.route('/portal', type='http', auth="public", website=True)
    def index(self, **kw):
        request.uid = request.session.uid
        user = request.registry.get('res.users').browse(request.cr, request.uid, request.uid)
        #hr_root
        menu_xml_id = request.env.ref('smart_hr.hr_root')
        return request.render('smart_internal_portal.index_page',
                              qcontext={'db_info': json.dumps(openerp.addons.web.controllers.main.db_info()),
                                        'user': user,
                                        'hr_root': menu_xml_id.id
                                        }
                              )

    @http.route('/portal/login', type='http', auth="none")
    def web_login(self, redirect=None, **kw):
        openerp.addons.web.controllers.main.ensure_db()
        request.params['login_success'] = False
        if request.httprequest.method == 'GET' and redirect and request.session.uid:
            return http.redirect_with_hash(redirect)

        if not request.uid:
            request.uid = openerp.SUPERUSER_ID

        values = request.params.copy()
        try:
            values['databases'] = http.db_list()
        except openerp.exceptions.AccessDenied:
            values['databases'] = None

        if request.httprequest.method == 'POST':
            old_uid = request.uid
            uid = request.session.authenticate(request.session.db, request.params['login'], request.params['password'])
            if uid is not False:
                request.params['login_success'] = True
                if not redirect:
                    redirect = '/portal'
                return http.redirect_with_hash(redirect)
            request.uid = old_uid
            values['error'] = "تسجيل الدخول خاطئ "
        return request.render('smart_internal_portal.login_page', values)