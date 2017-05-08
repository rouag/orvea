# -*- encoding: utf-8 -*-


import openerp
import openerp.modules.registry

from openerp import http
from openerp.http import request
from openerp.addons.web.controllers.main import Home
import werkzeug.utils
import json



#----------------------------------------------------------
# OpenERP Web web Controllers
#----------------------------------------------------------
class Home(Home):

    @http.route('/', type='http', auth="public", website=True)
    def index(self, **kw):
        request.uid = request.session.uid
        
        user = request.registry.get('res.users').browse(request.cr, request.uid,request.uid)
        
        #hr_root
        menu_xml_id = request.env.ref('smart_hr.hr_root')
        return request.render('web.login',
                               qcontext={'db_info': json.dumps(openerp.addons.web.controllers.main.db_info()),
                                         'user': user,
                                         'hr_root': menu_xml_id.id
                                         }
                               
                               )
        
    # ideally, this route should be `auth="user"` but that don't work in non-monodb mode.
    @http.route('/web', type='http', auth="none")
    def web_client(self, s_action=None, **kw):
        openerp.addons.web.controllers.main.ensure_db()
        if not request.session.uid:
            return werkzeug.utils.redirect('/web/login', 303)
        if kw.get('redirect'):
            return werkzeug.utils.redirect(kw.get('redirect'), 303)

        request.uid = request.session.uid
        return request.render('web.webclient_bootstrap', qcontext={'db_info': json.dumps(openerp.addons.web.controllers.main.db_info())})

    @http.route('/home', type='http', auth="none")
    def web_client2(self, s_action=None, **kw):
        openerp.addons.web.controllers.main.ensure_db()
        if not request.session.uid:
            return werkzeug.utils.redirect('/web/login', 303)
        if kw.get('redirect'):
            return werkzeug.utils.redirect(kw.get('redirect'), 303)

        request.uid = request.session.uid
        
        user = request.registry.get('res.users').browse(request.cr, request.uid,request.uid)
        
        #hr_root
        menu_xml_id = request.env.ref('smart_hr.hr_root')
        
        return request.render('smart_theme.webclient_home',
                               qcontext={'db_info': json.dumps(openerp.addons.web.controllers.main.db_info()),
                                         'user': user,
                                         'hr_root': menu_xml_id.id
                                         }
                               
                               )
    

    @http.route('/web/login', type='http', auth="none")
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
                    redirect = '/home'
                return http.redirect_with_hash(redirect)
            request.uid = old_uid
            values['error'] = "تسجيل الدخول خاطئ "
        return request.render('web.login', values)