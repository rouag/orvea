# -*- encoding: utf-8 -*-


import openerp
import openerp.modules.registry

from openerp import http
from openerp.http import request
import werkzeug.utils
import json
from operator import itemgetter
from openerp.addons.smart_base.util.umalqurra import *
from umalqurra.hijri_date import HijriDate
from umalqurra.hijri import Umalqurra
from openerp import fields


class Home(http.Controller):

    @http.route('/portal/json/attendances', auth='user', type='json', website=True)
    def attendances_json(self):
        today = fields.Date.from_string(fields.Date.today())
        hijri_month = get_hijri_month_by_date(HijriDate, Umalqurra, today)
        hijri_year = get_hijri_year_by_date(HijriDate, Umalqurra, today)
        date_start = get_hijri_month_start_by_year(HijriDate, Umalqurra, hijri_year, hijri_month)
        date_stop = get_hijri_month_end__by_year(HijriDate, Umalqurra, hijri_year, hijri_month)
        employee_id = request.env['hr.employee'].search([('user_id', '=', request.uid)], limit=1)
        attendances = request.env['hr.attendance.summary'].search([('employee_id', '=', employee_id.id),
                                                                   ('date', '>=', str(date_start)),
                                                                   ('date', '<=', str(date_stop))])
        print '---date_start---', date_start
        print '---date_stop---', date_stop
        print '------attendances-----', attendances
        tot_abscence = 0.0
        tot_presence = 0.0
        tot_delay = 0.0
        for line in attendances:
            tot_abscence += line.retard + line.leave
            absence = 0
            if line.absence == 1.0:
                absence = 7
                tot_presence += absence
            tot_delay += 7 - (line.retard + line.leave + absence)
        tot = tot_delay + tot_abscence + tot_presence
        if tot == 0.0:
            tot = 1
        return json.dumps({'tot_delay': tot_delay / tot, 'tot_abscence': tot_abscence / tot, 'tot_presence': tot_presence / tot})

    def get_home_page_contents(self):
        """
        @return: array of dict for homepage's content
        """
        page_content = {}
        smart_button = {'normal_holidays_solde': 0, 'requests': 0, 'missions': 0, 'net_salary': 0.0}
        user = request.registry.get('res.users').browse(request.cr, request.uid, request.uid)
        employee_id = request.env['hr.employee'].search([('user_id', '=', user.id)], limit=1)
        # رصيد اجازاتي
        stock_line = request.env['hr.employee.holidays.stock'].search([('holiday_status_id', '=', request.env.ref('smart_hr.data_hr_holiday_status_normal').id),
                                                                       ('employee_id', '=', employee_id.id)
                                                                       ], limit=1)
        if stock_line:
            smart_button['normal_holidays_solde'] = int(stock_line.holidays_available_stock)
        # طلباتي
        requests = request.env['hr.holidays'].search_count([('state', 'not in', ('done', 'cancel', 'cutoff', 'refuse')),
                                                            ('employee_id', '=', employee_id.id)])
        requests += request.env['hr.deputation'].search_count([('state', 'not in', ('done', 'finish', 'refuse')),
                                                               ('employee_id', '=', employee_id.id)])
        requests += request.env['hr.scholarship'].search_count([('state', 'not in', ('done', 'finished', 'cancel', 'cutoff')),
                                                               ('employee_id', '=', employee_id.id)])
        requests += request.env['hr.promotion.employee.demande'].search_count([('state', 'not in', ('done', 'cancel')),
                                                                               ('employee_id', '=', employee_id.id)])
        requests += request.env['hr.employee.transfert'].search_count([('state', 'not in', ('done', 'refused', 'cancelled')),
                                                                       ('employee_id', '=', employee_id.id)])
        requests += request.env['hr.employee.lend'].search_count([('state', 'not in', ('done', 'sectioned')),
                                                                  ('employee_id', '=', employee_id.id)])
        requests += request.env['hr.employee.commissioning'].search_count([('state', 'not in', ('done', 'refused')),
                                                                           ('employee_id', '=', employee_id.id)])
        requests += request.env['hr.holidays.cancellation'].search_count([('state', 'not in', ('done', 'refuse')),
                                                                          ('employee_id', '=', employee_id.id)])
        requests += request.env['hr.candidates'].search_count([('state', 'not in', ('done', 'cancel')),
                                                               ('employee_id', '=', employee_id.id)])
        requests += request.env['hr.employee.absence.days'].search_count([('request_id.state', 'not in', ('done', 'refuse')),
                                                                          ('employee_id', '=', employee_id.id)])
        requests += request.env['hr.employee.delay.hours'].search_count([('request_id.state', 'not in', ('done', 'refuse')),
                                                                         ('employee_id', '=', employee_id.id)])
        smart_button['requests'] = requests
        # مهامي
        missions = request.env['hr.employee.task'].search_count([('state', '!=', 'done'),
                                                                 ('employee_id', '=', employee_id.id)])
        smart_button['missions'] = missions
        # صافي الراتب
        grid_id, basic_salary = employee_id.get_salary_grid_id(False)
        if grid_id:
            smart_button['net_salary'] = grid_id.net_salary

        # get employee in same department
        dep_employee_ids = request.env['hr.employee'].search([('employee_state', '=', 'employee'),
                                                              ('department_id', '=', employee_id.department_id.id)], limit=8)

        # معاملاتي
        actions = []
        records_ids = request.env['hr.holidays'].search([('employee_id', '=', employee_id.id)])
        for rec in records_ids:
            actions.append({'name': u'طلب اجازة', 'date': rec.create_date})
        records_ids = request.env['hr.deputation'].search([('employee_id', '=', employee_id.id)])
        for rec in records_ids:
            actions.append({'name': u'طلب إنتداب', 'date': rec.create_date})
        records_ids = request.env['hr.scholarship'].search([('employee_id', '=', employee_id.id)])
        for rec in records_ids:
            actions.append({'name': u'طلب ابتعاث', 'date': rec.create_date})
        records_ids = request.env['hr.promotion.employee.demande'].search([('employee_id', '=', employee_id.id)])
        for rec in records_ids:
            actions.append({'name': u'طلب ترقية', 'date': rec.create_date})
        records_ids = request.env['hr.employee.transfert'].search([('employee_id', '=', employee_id.id)])
        for rec in records_ids:
            actions.append({'name': u'طلب نقل', 'date': rec.create_date})
        records_ids = request.env['hr.employee.lend'].search([('employee_id', '=', employee_id.id)])
        for rec in records_ids:
            actions.append({'name': u'طلب إعارة', 'date': rec.create_date})
        records_ids = request.env['hr.employee.commissioning'].search([('employee_id', '=', employee_id.id)])
        for rec in records_ids:
            actions.append({'name': u'طلب تكليف', 'date': rec.create_date})
        records_ids = request.env['hr.holidays.cancellation'].search([('employee_id', '=', employee_id.id)])
        for rec in records_ids:
            actions.append({'name': u'طلب إلغاء أو قطع', 'date': rec.create_date})
        records_ids = request.env['hr.candidates'].search([('employee_id', '=', employee_id.id)])
        for rec in records_ids:
            actions.append({'name': u'طلب دورة تدربية', 'date': rec.create_date})
        records_ids = request.env['hr.employee.absence.days'].search([('employee_id', '=', employee_id.id)])
        for rec in records_ids:
            actions.append({'name': u'طلب تحويل ايام الغياب بدون عذر', 'date': rec.create_date})
        records_ids = request.env['hr.employee.delay.hours'].search([('employee_id', '=', employee_id.id)])
        for rec in records_ids:
            actions.append({'name': u'طلب تحويل ساعات التأخير', 'date': rec.create_date})
        # sort actions by date
        actions = sorted(actions, key=itemgetter('date'), reverse=True)
        # fill page_content
        page_content['smart_button'] = smart_button
        page_content['employee'] = employee_id
        page_content['dep_employee_ids'] = dep_employee_ids
        page_content['actions'] = actions[:7]
        return page_content

    @http.route('/portal', type='http', auth="user", website=True)
    def index(self, **kw):
        request.uid = request.session.uid
        user = request.registry.get('res.users').browse(request.cr, request.uid, request.uid)
        #hr_root
        menu_xml_id = request.env.ref('smart_hr.hr_root')
        # get homepage_content
        page_content = self.get_home_page_contents()
        smart_button = page_content['smart_button']
        employee = page_content['employee']
        dep_employee_ids = page_content['dep_employee_ids']
        actions = page_content['actions']
        return request.render('smart_internal_portal.index_page',
                              qcontext={'db_info': json.dumps(openerp.addons.web.controllers.main.db_info()),
                                        'user': user,
                                        'hr_root': menu_xml_id.id,
                                        'smart_button': smart_button,
                                        'employee': employee,
                                        'dep_employee_ids': dep_employee_ids,
                                        'actions': actions
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