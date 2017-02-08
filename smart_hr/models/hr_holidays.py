# -*- coding: utf-8 -*-

from openerp import fields, models, api, _
from openerp.tools import SUPERUSER_ID
from openerp.exceptions import ValidationError
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT


class HrHolidays(models.Model):
    _inherit = 'hr.holidays'
    _description = 'hr holidays Request'
    _order = 'id desc'

    def _check_date(self, cr, uid, ids, context=None):
        for holiday in self.browse(cr, uid, ids, context=context):
            domain = [
                ('date_from', '<=', holiday.date_to),
                ('date_to', '>=', holiday.date_from),
                ('employee_id', '=', holiday.employee_id.id),
                ('id', '!=', holiday.id),
                ('state', 'not in', ['cancel', 'refuse']),
            ]
            x = self.search(cr, uid, domain, context=context)

            nholidays = self.search_count(cr, uid, domain, context=context)
            if holiday.compensation_type == 'money':
                return True
            if nholidays:
                return False
        return True

    @api.multi
    def _set_external_autoritie(self):
        self.ensure_one()
        search_external_authoritie = self.env["external.authorities"].search([('holiday_status', '=', self.holiday_status_id.id)])
        if search_external_authoritie:
            self.external_authoritie = search_external_authoritie[0]

    name = fields.Char(string=u'رقم القرار', advanced_search=True)
    date = fields.Date(string=u'تاريخ الطلب', default=fields.Datetime.now())
    employee_id = fields.Many2one('hr.employee', string=u'الموظف', default=lambda self: self.env['hr.employee'].search([('user_id', '=', self._uid)], limit=1), advanced_search=True)
    raison = fields.Selection([('other', u'سبب أخر'), ('husband', u'مرافقة الزوج'),
                               ('wife', u'مرافقة الزوجة'), ('legit', u'مرافقة كمحرم شرعي')],
                               default="other", string=u'السبب ')
    date_from = fields.Date(string=u'التاريخ من ', default=fields.Datetime.now())
    date_to = fields.Date(string=u'التاريخ الى' , compute='_compute_date_to', store=True)
    duration = fields.Integer(string=u'الأيام' , required=1)
    holiday_status_id = fields.Many2one('hr.holidays.status', string=u'نوع الأجازة', default=lambda self: self.env.ref('smart_hr.data_hr_holiday_status_normal'), advanced_search=True)
    state = fields.Selection([
        ('draft', u'طلب'),
        ('dm', u'مدير المباشر'),
        ('audit', u'تدقيق'),
        ('hrm', u'مدير شؤون الموظفين'),
        ('external_audit', u'جهة خارجية'),
        ('revision', u'مراجعة الخطاب'),
        ('revision_response', u'تسجيل رد الجهة'),
        ('done', u'اعتمدت'),
        ('refuse', u'رفض'),
        ('cancel', u'ملغاة'),
        ('cutoff', u'مقطوعة'),
        ('confirm', 'To Approve'),
        ('refuse', 'Refused'),
        ('validate1', 'Second Approval'),
        ('validate', 'Approved')], string=u'حالة', default='draft', advanced_search=True)

    is_current_user = fields.Boolean(string='Is Current User', compute='_is_current_user')
    is_direct_manager = fields.Boolean(string='Is Direct Manager', compute='_is_direct_manager')
    is_delayed = fields.Boolean(string='is_delayed', default=False)
    num_outspeech = fields.Char(string=u'رقم الخطاب الصادر')
    date_outspeech = fields.Date(string=u'تاريخ الخطاب الصادر')
    outspeech_file = fields.Binary(string=u'الخطاب الصادر')
    outspeech_file_name = fields.Char(string=u'file name')

    num_inspeech = fields.Char(string=u'رقم الخطاب الوارد')
    date_inspeech = fields.Date(string=u'تاريخ الخطاب الوارد')
    inspeech_file = fields.Binary(string=u'الخطاب الوارد')
    inspeech_file_name = fields.Char(string=u'الخطاب الوارد name')
    # Cancellation
    is_cancelled = fields.Boolean(string=u'ملغاة', compute='_is_cancelled')
    is_started = fields.Boolean(string=u'بدأت', compute='_compute_is_started')
    holiday_cancellation = fields.Many2one('hr.holidays.cancellation')    
    # Extension
    is_extension = fields.Boolean(string=u'تمديد إجازة')
    is_extended = fields.Boolean(string=u'ممددة', compute='_is_extended')
    extended_holiday_id = fields.Many2one('hr.holidays', string=u'الإجازة الممددة')
    parent_id = fields.Many2one('hr.holidays', string=u'Parent')
    extension_holidays_ids = fields.One2many('hr.holidays', 'parent_id', string=u'التمديدات')
    is_extensible = fields.Integer(string=u'يمكن تمديدها', related='holiday_status_id.extension_number')
    # decision
    need_decision = fields.Boolean('status_id need decision', related='holiday_status_id.need_decision')
    num_decision = fields.Char(string=u'رقم القرار')
    date_decision = fields.Date(string=u'تاريخ القرار')
    childbirth_date = fields.Date(string=u'تاريخ ولادة الطفل')
    birth_certificate = fields.Binary(string=u'شهادة الميلاد')
    extension_period = fields.Integer(string=u'مدة التمديد', default=0)
    external_authoritie = fields.Many2one('external.authorities', string=u'الجهة الخارجية', compute="_set_external_autoritie")
    entitlement_type = fields.Many2one('hr.holidays.entitlement.config', string=u'خاصيّة الإجازة')
    death_person = fields.Char(string=u'المتوفي')
    medical_certification = fields.Binary(string=u'الشهادة الطبية')
    compensation_type = fields.Selection([
        ('holiday', u'إجازة'),
        ('money', u' مقابل ‫مادي‬ ‬ ')], string=u'نوع التعويض')
    accompaniment_type = fields.Selection([
        ('Relatives', u'أحد الأقارب '),
        ('child', u' ‫طفل‬‬')], string=u'نوع المرافقة')
    accompanied_child_age = fields.Integer(string=u'عمر الطفل')
    open_period = fields.Many2one('hr.holidays.periode', string=u'periode')
    medical_report = fields.Binary(string=u'التقرير الطبي')
    prove_exam_duration = fields.Binary(string=u'إثبات اداء الامتحان ومدته')
    study_subject = fields.Char(string=u'موضوع‬ ‫الدِّراسة')
    out_speech_file_name = fields.Char(string=u'مسمى صورة الخطاب الصادر')
    in_speech_file_name = fields.Char(string=u'مسمى صورة الخطاب الوارد')
    birth_certificate_file_name = fields.Char(string=u'مسمى شهادة الميلا')
    medical_certification_file_name = fields.Char(string=u'الشهادة الطبيةا')
    medical_report_file_name = fields.Char(string=u'التقرير الطبي')
    prove_exam_duration_name = fields.Char(string=u'إثبات اداء الامتحان ومدته مسمى')
    medical_report_number = fields.Char(string=u'رقم التقرير الطبي')
    medical_report_date = fields.Date(string=u'تاريخ التقرير الطبي')
    courses_city = fields.Char(string=u'المدينة')
    courses_country = fields.Char(string=u'الدولة')
    current_holiday_stock = fields.Char(string=u'الرصيد الحالي',compute='_compute_current_holiday_stock')
    sport_participation_topic = fields.Char(string=u'موضوع المشاركة')
    birth_certificate_child_birth_dad = fields.Binary(string=u'شهادة الميلاد')
    birth_certificate_file_name_file_name= fields.Char(string=u'شهادة الميلاد')
    speech_source = fields.Char(string=u'مصدر الخطابات')
    
    _constraints = [
        (_check_date, 'You can not have 2 leaves that overlaps on same day!', ['date_from', 'date_to']),
    ]

    @api.multi
    @api.depends("holiday_status_id", "entitlement_type")
    def _compute_current_holiday_stock(self):
        current_stock = 0
        if self.holiday_status_id and self.entitlement_type and self.holiday_status_id.id != self.env.ref('smart_hr.data_hr_holiday_compensation').id:
            stock_line = self.env['hr.employee.holidays.stock'].search([('employee_id', '=', self.employee_id.id),('holiday_status_id', '=', self.holiday_status_id.id),
                                                               ('entitlement_id.entitlment_category.id', '=', self.entitlement_type.id)])
            entitlement_line = self.env['hr.holidays.status.entitlement'].search([('leave_type', '=', self.holiday_status_id.id),
                                                               ('entitlment_category.id', '=', self.entitlement_type.id)])
            if stock_line:
                current_stock = stock_line.holidays_available_stock
            elif entitlement_line and entitlement_line.periode:
                current_stock = entitlement_line.holiday_stock_default
            elif entitlement_line and not entitlement_line.periode:
                if entitlement_line.holiday_stock_default > 0:
                    current_stock = entitlement_line.holiday_stock_default
                else:
                    current_stock = str("لا تحتاج رصيد")

        elif not self.entitlement_type and self.holiday_status_id.id != self.env.ref('smart_hr.data_hr_holiday_compensation').id:
            not_all_entitlement_line = self.env['hr.holidays.status.entitlement'].search_count([('leave_type', '=', self.holiday_status_id.id),
                ('entitlment_category.id', '!=', self.env.ref('smart_hr.data_hr_holiday_entitlement_all').id)
                ])
            if not_all_entitlement_line == 0:
                    entitlement_line = self.env['hr.holidays.status.entitlement'].search([('leave_type', '=', self.holiday_status_id.id),
                                                               ('entitlment_category.id', '=',self.env.ref('smart_hr.data_hr_holiday_entitlement_all').id)])

                    if entitlement_line and  entitlement_line.periode == 100:
                        stock_line =  self.env['hr.employee.holidays.stock'].search([('employee_id', '=', self.employee_id.id),
                                                               ('holiday_status_id', '=', self.holiday_status_id.id),('entitlement_id.entitlment_category.id', '=', self.env.ref('smart_hr.data_hr_holiday_entitlement_all').id)
                                                                ])
                        if stock_line:
                            current_stock = stock_line.holidays_available_stock
                        else:
                            if entitlement_line.holiday_stock_default==0:
                                current_stock = str("لا تحتاج رصيد")
                            else:
                                current_stock = entitlement_line.holiday_stock_default
        if self.holiday_status_id.id == self.env.ref('smart_hr.data_hr_holiday_compensation').id:
            current_stock = self.employee_id.compensation_stock
        self.current_holiday_stock = current_stock


    @api.one
    @api.depends('date_from')
    def _compute_is_started(self):
        if self.date_from <= datetime.today().strftime('%Y-%m-%d'):
            self.is_started = True



    @api.onchange('holiday_status_id')
    def onchange_holiday_status_id(self):
        res = {}
        if self.holiday_status_id == self.env.ref('smart_hr.data_hr_holiday_status_illness'):
            res['domain'] = {'entitlement_type': [('code', '=', 'illness')]}
        if self.holiday_status_id == self.env.ref('smart_hr.data_hr_holiday_death'):
            res['domain'] = {'entitlement_type': [('code', '=', 'death')]}
        if self.holiday_status_id == self.env.ref('smart_hr.data_hr_holiday_accompaniment_exceptional'):
            res['domain'] = {'entitlement_type': [('code', '=', 'accompaniment_exceptional')]}
        if self.holiday_status_id == self.env.ref('smart_hr.data_hr_holiday_status_sport'):
            res['domain'] = {'entitlement_type': [('code', '=', 'sport')]}
        return res

    @api.multi
    def _init_balance(self, employee_id):
        holiday_obj = self.env['hr.holidays']
        holidays_status = self.env['hr.holidays.status'].search([])
        # compute solde of holidays
        for holiday_status_id in holidays_status:
            # recompute balance of the holiday_status_id
            # check if there is entitlements in holiday_status_id
            if holiday_status_id.entitlements:
                # loop under entitlements
                for en in holiday_status_id.entitlements:
                 # calculate the balance of the employee for all holiday status having entitlements
                    # check if the type existe in holidays_balance of the employee
                    balance_line = self.env['hr.employee.holidays.stock'].search([('employee_id', '=', employee_id.id),
                                                                                  ('holiday_status_id', '=', holiday_status_id.id),
                                                                                  ('entitlement_id.id', '=', en.id),
                                                                                  ])
                    if not balance_line:
                        if holiday_status_id.id == self.env.ref('smart_hr.data_hr_holiday_status_normal').id:
                            balance_line = self.env['hr.employee.holidays.stock'].create({'holidays_available_stock': 0,
                                                                                    'employee_id': employee_id.id,
                                                                                    'holiday_status_id': holiday_status_id.id,
                                                                                    'token_holidays_sum': 0,
                                                                                    'periode': en.periode,
                                                                                    'entitlement_id':en.id})
                            open_period = self.create_holiday_periode(employee_id, holiday_status_id, en)
#
#                         else:
#                             if holiday_status_id.id in [self.env.ref('smart_hr.data_hr_holiday_status_illness').id,self.env.ref('smart_hr.data_hr_holiday_status_contractor').id]:
#                                 balance_line = self.env['hr.employee.holidays.stock'].create({'holidays_available_stock': en.holiday_stock_default,
#                                                                                     'employee_id': employee_id.id,
#                                                                                     'holiday_status_id': holiday_status_id.id,
#                                                                                     'token_holidays_sum': 0,
#                                                                                     'periode': en.periode,
#                                                                                     'entitlement_id':en.id})

    @api.multi
    def smart_action_done(self):
        right_entitlement = False
        if not self.entitlement_type:
            entitlement_type = self.env.ref('smart_hr.data_hr_holiday_entitlement_all')
        else:
            entitlement_type = self.entitlement_type
        for en in self.holiday_status_id.entitlements:
            if en.entitlment_category.id == entitlement_type.id:
                right_entitlement = en
                break

        open_period = False
        init_stock_line = False

        if right_entitlement.periode and right_entitlement.periode != 100 and self.holiday_status_id.id != self.env.ref('smart_hr.data_hr_holiday_compensation').id:
            periodes = self.env['hr.holidays.periode'].search([('employee_id', '=', self.employee_id.id),
                                                           ('holiday_status_id', '=', self.holiday_status_id.id),
                                                           ('entitlement_id', '=', en.id),
                                                           ('active', '=', True),
                                                           ])

            stock_line = self.env['hr.employee.holidays.stock'].search([('employee_id', '=', self.employee_id.id),
                                                                         ('holiday_status_id', '=', self.holiday_status_id.id),
                                                                         ('entitlement_id.id', '=', right_entitlement.id),
                                                                         ])
            if periodes:
                for periode in periodes:
                    if fields.Datetime.from_string(periode.date_to) > fields.Datetime.from_string(self.date_to) and fields.Datetime.from_string(periode.date_from) < fields.Datetime.from_string(self.date_from):
                        open_period = periode
                    else:
                        periode.active = False
 

            if not open_period:
                open_period = self.create_holiday_periode(self.employee_id, self.holiday_status_id, right_entitlement)
                open_period.active = True
                init_stock_line = True

            if not stock_line:
                stock_line = self.env['hr.employee.holidays.stock'].create({'holidays_available_stock': open_period.holiday_stock,
                                                                                    'employee_id': self.employee_id.id,
                                                                                    'holiday_status_id': self.holiday_status_id.id,
                                                                                    'token_holidays_sum': 0,
                                                                                    'periode': right_entitlement.periode,
                                                                                    'entitlement_id':en.id,
                                                                                    })            
            open_period.holiday_stock -= self.duration
            self.open_period = open_period.id
            if init_stock_line:
                stock_line.holidays_available_stock = open_period.holiday_stock
                stock_line.token_holidays_sum = self.duration
            else:
                stock_line.holidays_available_stock -= self.duration
                stock_line.token_holidays_sum += self.duration

        elif self.holiday_status_id.id != self.env.ref('smart_hr.data_hr_holiday_compensation').id:

            stock_line = self.env['hr.employee.holidays.stock'].search([('employee_id', '=', self.employee_id.id),
                                                                         ('holiday_status_id', '=', self.holiday_status_id.id),
                                                                         ('entitlement_id.id', '=', right_entitlement.id),
                                                                         ])
            if stock_line:
                if right_entitlement.periode == 100:
                    stock_line.holidays_available_stock -= self.duration
                    stock_line.token_holidays_sum += self.duration
                else:
                    if right_entitlement.holiday_stock_default > 0:
                        stock_line.holidays_available_stock += right_entitlement.holiday_stock_default - self.duration
                        stock_line.token_holidays_sum += self.duration 
                    else:
                        stock_line.token_holidays_sum += self.duration
            else:
                if right_entitlement.holiday_stock_default > 0:
                    holiday_stock_default = right_entitlement.holiday_stock_default - self.duration
                else:
                    holiday_stock_default = right_entitlement.holiday_stock_default

                stock_line = self.env['hr.employee.holidays.stock'].create({'holidays_available_stock': holiday_stock_default,
                                                                                    'employee_id': self.employee_id.id,
                                                                                    'holiday_status_id': self.holiday_status_id.id,
                                                                                    'token_holidays_sum': self.duration,
                                                                                    'periode': right_entitlement.periode,
                                                                                    'entitlement_id':en.id,
                                                                                    })
        else:
            if self.compensation_type == 'holiday':
                self.employee_id.compensation_stock -= self.duration
            if self.compensation_type == 'money':
                self.employee_id.compensation_stock = 0
#                 مدة الترقية
        if self.holiday_status_id.promotion_deductible:
            self.env['hr.employee.promotion.history'].decrement_promotion_duration(self.employee_id,self.duration)

        if self.holiday_status_id.deductible_duration_service:
            self.employee_id.service_duration -= self.duration


#             create history_line
        type = " منح"+" " +self.holiday_status_id.name.encode('utf-8')
        self.env['hr.employee.history'].sudo().add_action_line(self.employee_id, self.name, self.date, type)

        if self.holiday_status_id == self.env.ref('smart_hr.data_hr_holiday_status_study'):
            self.env['courses.followup'].create({'employee_id':self.employee_id.id, 'state':'progress',
                                                 'holiday_id':self.id, 'name':self.study_subject,
                                                 })

        self.state = 'done'
        self.env['base.notification'].create({'title': u'إشعار بقبول إجازة',
                                              'message': u'لقد تم قبول الإجازة',
                                              'user_id': self.employee_id.user_id.id,
                                              'show_date': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                              'notif': True,
                                              'res_id': self.id,
                                             'res_action': 'smart_hr.action_hr_holidays_form'})
    @api.model
    def update_normal_holidays_stock(self):
        right_entitlement = False
        for en in self.env.ref('smart_hr.data_hr_holiday_status_normal').entitlements:
            if self.env.ref('smart_hr.data_hr_holiday_entitlement_all') == en.entitlment_category:
                right_entitlement = en
                break
        for employee in self.env['hr.employee'].search([('employee_state', '=', 'employee')]):    
            todayDate = datetime.now()
            first_day_date = todayDate.replace(day=1, month=1)      
            open_periode = self.env['hr.holidays.periode'].search([('employee_id', '=', employee.id),
                                                           ('holiday_status_id', '=', self.env.ref('smart_hr.data_hr_holiday_status_normal').id),
                                                           ('entitlement_id', '=', right_entitlement.id),
                                                           ('active', '=', True),
                                                            ('date_from', '=', first_day_date.strftime(DEFAULT_SERVER_DATE_FORMAT))])
            holiday_balance = self.env['hr.employee.holidays.stock'].search ([('employee_id', '=', employee.id),
                                                           ('holiday_status_id', '=', self.env.ref('smart_hr.data_hr_holiday_status_normal').id),
                                                                         ('entitlement_id.id', '=', right_entitlement.id),
                                                                         ])
            uncounted_days = 0
            employee_solde = right_entitlement.holiday_stock_default
            periode = right_entitlement.periode
            current_normal_holiday_stock = open_periode.holiday_stock
            today = date.today()
            d = today - relativedelta(months=1)
            previous_month_first_day = date(d.year, d.month, 1)
            previous_month_last_day = date(today.year, today.month, 1) - relativedelta(days=1)
#                    مدّة الإجازة الاستثنائية و الدراسية 

            holiday_uncounted_days = 0
            for holiday in self.env['hr.holidays'].search([]):
                if holiday.state == 'done' and holiday.employee_id == employee.id and  \
                    holiday.holiday_status_id in [self.env.ref('smart_hr.data_hr_holiday_accompaniment_exceptional').id,
                                                       self.env.ref('smart_hr.data_hr_holiday_status_exceptional').id,
                                                        self.env.ref('smart_hr.data_hr_holiday_status_study').id]:
                    if holiday.date_from < previous_month_first_day :
                        if holiday.date_to >= previous_month_first_day:
                            holiday_uncounted_days += (today - previous_month_first_day).days
                        else:
                            holiday_uncounted_days += holiday.date_to - previous_month_first_day
                    else:
                        if holiday.date_to > previous_month_last_day:
                            holiday_uncounted_days += previous_month_last_day - holiday.date_from
                        else:
                            holiday_uncounted_days += holiday.date_to - holiday.date_from 

#                    مدّة كف اليد todo

#                    مدّة الاعارة todo

            uncounted_days += holiday_uncounted_days
            # مدّة غياب‬ ‫الموظف بدون‬ سند‬ ‫ن
            uncounted_absence_days = self.env['hr.attendance.report_day'].search_count([('employee_id', '=', employee.id), ('action', '=', 'absence'),
                                                                            ('date', '>=', previous_month_first_day), ('date', '<=', previous_month_last_day)])

            uncounted_days += uncounted_absence_days

#                     
            # مدّةالتدريب
            search_domain = [
                        ('employee_id', '=', employee.id),
                        ('state', '=', 'done'),
                        ]
            formation_uncounted_days = 0
            candidate_obj = self.env['hr.candidates']
            for rec in candidate_obj.search(search_domain):
                dateto = fields.Date.from_string(rec.date_to)
                datefrom = fields.Date.from_string(rec.date_from)
                res = relativedelta(dateto, datefrom)
                months = (dateto.year - datefrom.year) * 12 + (dateto.month - datefrom.month)
                days = res.days
                if rec.date_from < previous_month_first_day < previous_month_last_day or rec.date_from < previous_month_last_day < rec.date_to:
                    if (months >= 1):
                        if rec.date_from < previous_month_first_day:
                            if rec.date_to > previous_month_last_day:
                                formation_uncounted_days += (today - previous_month_first_day).days
                            else:
                                formation_uncounted_days += rec.date_to - previous_month_first_day
                        else:
                            if rec.date_to > previous_month_last_day:
                                formation_uncounted_days += previous_month_last_day - rec.date_from
                            else:
                                formation_uncounted_days += rec.date_to - rec.date_from            
                                        
            uncounted_days += formation_uncounted_days
            init_solde = (employee_solde / (periode * 12))
            balance = init_solde - (uncounted_days / 30) * init_solde

            holiday_balance.write({'holidays_available_stock': current_normal_holiday_stock + balance})
            open_periode.write({'holiday_stock': open_periode.holiday_stock + balance})

                    
                    
    @api.multi
    def button_extend(self):
        # check if its possible to extend this holiday
        extensions_number = self.env['hr.holidays'].search_count([('extended_holiday_id', '=', self.id), ('extended_holiday_id', '!=', False), ('state', '=', 'done')])

                
        if extensions_number >= self.holiday_status_id.extension_number and self.holiday_status_id.extension_number > 0:
            raise ValidationError(u"لا يمكن تمديد هذا النوع من الاجازة أكثر من%s " % str(self.holiday_status_id.extension_number))

        view_id = self.env.ref('smart_hr.hr_holidays_form').id
        context = self._context.copy()
        default_date_from = fields.Date.to_string(fields.Date.from_string(self.date_to) + timedelta(days=1))
        context.update({
            u'default_is_extension': True,
            u'default_extended_holiday_id': self.id,
            u'default_date_from': default_date_from,
            u'readonly_by_pass': True,
        u'default_holiday_status_id': self.holiday_status_id.id,

        })
        return {
            'name': 'تمديد الإجازة',
            'view_type': 'form',
            'view_mode': 'tree',
            'views': [(view_id, 'form')],
            'res_model': 'hr.holidays',
            'view_id': view_id,
            'type': 'ir.actions.act_window',
            'res_id': False,
            'target': 'current',
            'context': context,
        }
        
    @api.multi
    def button_cancel(self):
        # Objects
        holidays_cancellation_obj = self.env['hr.holidays.cancellation']
        # Variables
        user = self.env['res.users'].browse(self._uid)
        employee = self.env['hr.employee'].search([('user_id', '=', user.id)], limit=1)
        # Create leave cancellation request
        vals = {
                'employee_id': employee.id,
                'holidays': [(4, self.id)],
                'note': '   ',
            }
        holiday_cancellation_id = holidays_cancellation_obj.create(vals)
        # Add to log
        self.message_post(u"تم ارسال طلب إلغاء من قبل '" + unicode(user.name) + u"'")
        return {
                    'name': u'طلب إلغاء',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'hr.holidays.cancellation',
                    'view_id': self.env.ref('smart_hr.hr_holidays_cancellation_mine_form').id,
                    'type': 'ir.actions.act_window',
                    'res_id': holiday_cancellation_id.id,
                }
    @api.multi
    def button_cut(self):
        # Objects
        holidays_cancellation_obj = self.env['hr.holidays.cancellation']
        # Variables
        user = self.env['res.users'].browse(self._uid)
        employee = self.env['hr.employee'].search([('user_id', '=', user.id)], limit=1)
        # Create leave cancellation request
        vals = {
                'employee_id': employee.id,
                'holidays': [(4, self.id)],
                'note': '   ',
            }
        holiday_cancellation_id = holidays_cancellation_obj.create(vals)
        # Add to log
        self.message_post(u"تم ارسال طلب القطع من قبل '" + unicode(user.name) + u"'")
        return {
                    'name': u'طلب قطع',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'hr.holidays.cancellation',
                    'view_id': self.env.ref('smart_hr.hr_holidays_cancellation_mine_form').id,
                    'type': 'ir.actions.act_window',
                    'res_id': holiday_cancellation_id.id,
                }
        
    @api.one
    @api.depends('extension_holidays_ids')
    def _is_extended(self):
        # Check if the holiday have a pending or completed extension leave
        is_extended = False
        for ext in self.extension_holidays_ids:
            if ext.state != 'refuse':
                is_extended = True
                break
        self.is_extended = is_extended
        
    @api.one
    @api.depends('holiday_cancellation')
    def _is_cancelled(self):
        # Check if the holidays have a pending or completed holidays cancellation
        is_cancelled = False
        if self.holiday_cancellation and self.holiday_cancellation.state != 'refuse': 
            is_cancelled = True
        self.is_cancelled = is_cancelled

    holiday_cancellation = fields.Many2one('hr.holidays.cancellation')    
    # Extension
    is_extension = fields.Boolean(string=u'تمديد إجازة')
    is_extended = fields.Boolean(string=u'ممددة', compute='_is_extended')
    extended_holiday_id = fields.Many2one('hr.holidays', string=u'الإجازة الممددة')
    parent_id = fields.Many2one('hr.holidays', string=u'Parent')
    extension_holidays_ids = fields.One2many('hr.holidays', 'parent_id', string=u'التمديدات')


    @api.model
    def _check_state_access_right(self, vals):
        # override this method to be always returning true to avoid checking state access right
        return True
    
    @api.one
    @api.depends('employee_id')
    def _is_current_user(self):
        if self.employee_id.user_id.id == self._uid:
            self.is_current_user = True
                
    @api.one
    @api.depends('employee_id')
    def _is_direct_manager(self):
            # System Admin Bypass
        if self.env['res.users'].browse(self._uid).has_group('smart_hr.group_sys_manager'):
            self.is_direct_manager = True
        elif self.employee_id.user_id.id != self._uid and self.state == 'dm':
            depth = self._get_dm_depth(self._uid, self.employee_id)
            if self.state_dm == depth:
                self.is_direct_manager = True

    @api.one
    @api.depends('date_from', 'duration')
    def _compute_date_to(self):
        if self.date_from and self.duration:
            new_date_to = fields.Date.from_string(self.date_from) + timedelta(days=self.duration)
            self.date_to = new_date_to
        elif self.date_from:
                self.date_to = self.date_from

    @api.multi
    def send_holiday_request(self):
        self.ensure_one()
        user = self.env['res.users'].browse(self._uid)
        self.check_constraintes()
            # check if the holiday status is supposed to be confirmed by direct manager
        if self.holiday_status_id.direct_director_decision:
            self.message_post(u"تم إرسال الطلب من قبل '" + unicode(user.name) + u"' إلى المدير المباشر")
            self.env['base.notification'].create({'title': u'إشعار بوجود طلب اجازة',
                                              'message': u"لقد تم تقديم  طلب اجازة من طرف الموظف"+unicode(self.employee_id.user_id.id),
                                              'user_id': self.employee_id.parent_id.user_id.id,
                                              'show_date': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                              'notif': True,
                                              'res_id': self.id,
                                             'res_action': 'smart_hr.action_hr_holidays_form'})
            self.state = 'dm'
        elif self.holiday_status_id.audit:
            self.message_post(u"تم إرسال الطلب من قبل '" + unicode(user.name) + u"' إلى مرحلة التدقيق")
            self.state = 'audit'
        elif self.holiday_status_id.employees_director_decision:
            self.message_post(u"تم إرسال الطلب من قبل '" + unicode(user.name) + u"' إلى مرحلة مدير شؤون الموظفين")
            self.state = 'hrm'
        elif self.holiday_status_id.external_decision:
            self.message_post(u"تم إرسال الطلب من قبل '" + unicode(user.name) + u" إلى مرحلة جهة خارجية ")
            self.state = 'external_audit'
        else:
            self.smart_action_done()

    @api.multi
    def button_accept_dm(self):
        self.ensure_one()
        # send notification for the employee who is requesting a holiday
        self.env['base.notification'].create({'title': u'إشعار بقبول إجازة',
                                              'message': u'لقد تم قبول الإجازة من طرف المدير المباشر',
                                              'user_id': self.employee_id.user_id.id,
                                              'show_date': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                              'notif': True,
                                              'res_id': self.id,
                                             'res_action': 'smart_hr.action_hr_holidays_form'})
        
        if self.holiday_status_id.audit:
            self.state = 'audit'
        elif self.holiday_status_id.employees_director_decision:
            self.state = 'hrm'
        elif self.holiday_status_id.external_decision:
            self.state = 'external_audit'
        else:
            self.smart_action_done()
            
    @api.multi
    def action_delay_holiday(self):
        
        self.ensure_one()
        context = {};
        context['holiday_id'] = self.id
        return {
              'name': u'حجز الوظيفة',
              'view_type': 'form',
              "view_mode": 'form',
              'res_model': 'hr.delay.holiday',
              'type': 'ir.actions.act_window',
              'context': context,
              'target': 'new',
              }
        
    @api.multi
    def button_delay_dm(self):
        self.ensure_one()
        self.env['base.notification'].create({'title': u'إشعار برفض إجازة',
                                              'message': u'لقد تم رفض الإجازة من طرف المدير المباشر',
                                              'user_id': self.employee_id.user_id.id,
                                              'show_date': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                              'notif': True,
                                              'res_id': self.id,
                                             'res_action': 'smart_hr.action_hr_holidays_form'})
        self.state = 'draft'
        
    @api.multi
    def button_accept_audit(self):
        self.ensure_one()
        self.env['base.notification'].create({'title': u'إشعار بقبول إجازة',
                                              'message': u'لقد تم قبول الإجازة من طرف مدقق الاجازات',
                                              'user_id': self.employee_id.user_id.id,
                                              'show_date': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                              'notif': True,
                                              'res_id': self.id,
                                             'res_action': 'smart_hr.action_hr_holidays_form'})
        if self.holiday_status_id.need_decision:
            if not self.num_decision:
                raise ValidationError(u"الرجاء تعبئة رقم القرار.")
            if not self.date_decision:
                raise ValidationError(u"الرجاء تعبئة تاريخ القرار.")
        if self.holiday_status_id.employees_director_decision:
            self.state = 'hrm'
        elif self.holiday_status_id.external_decision:
            self.state = 'external_audit'
        else:
            self.smart_action_done()

    @api.multi
    def button_refuse_audit(self):
        self.ensure_one()
        self.env['base.notification'].create({'title': u'إشعار برفض إجازة',
                                              'message': u'لقد تم رفض الإجازة من طرف مدقق الاجازات',
                                              'user_id': self.employee_id.user_id.id,
                                              'show_date': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                              'notif': True,
                                              'res_id': self.id,
                                             'res_action': 'smart_hr.action_hr_holidays_form'})
        if self.holiday_status_id.direct_director_decision:
            self.state = 'dm'
        else:
            self.state = 'draft'

    @api.multi
    def button_accept_hrm(self):
        self.ensure_one()
        if not self.holiday_status_id.external_decision:
            # send notification for the employee who is requesting a holiday
            self.smart_action_done()

            self.env['base.notification'].create({'title': u'إشعار بقبول إجازة',
                                              'message': u'لقد تم قبول الإجازة من طرف مدير شؤون الموظفين',
                                              'user_id': self.employee_id.user_id.id,
                                              'show_date': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                              'res_id': self.id,
                                              'res_action': 'smart_hr.action_hr_holidays_form',
                                              'notif': True})
        if self.holiday_status_id.external_decision and not self.employee_id.external_decision:
            raise ValidationError(u"الموظف يحتاج إلى موافقة جهة خارجية.")
        if self.holiday_status_id.external_decision and self.employee_id.external_decision:
            self.state = 'external_audit'

    @api.multi
    def button_delay_hrm(self):
        self.ensure_one()
        self.env['base.notification'].create({'title': u'إشعار برفض إجازة',
                                              'message': u'لقد تم رفض الإجازة من طرف مدير شؤون الموظفين',
                                              'user_id': self.employee_id.user_id.id,
                                              'show_date': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                              'res_id': self.id,
                                              'res_action': 'smart_hr.action_hr_holidays_form',
                                              'notif': True})
        if self.holiday_status_id.audit:
            self.state = 'audit'
        elif self.holiday_status_id.direct_director_decision:
            self.state = 'dm'
        else:
            self.state = 'draft'

    @api.multi
    def button_accept_external_audit(self):
        self.ensure_one()
        if not self.num_outspeech:
            raise ValidationError(u"الرجاء تعبئة رقم الخطاب الصادر.")
        if not self.date_outspeech:
            raise ValidationError(u"الرجاء تعبئة تاريخ الخطاب الصادر.")
        if not self.outspeech_file:
            raise ValidationError(u"الرجاء إرفاق الخطاب.")

        if self.holiday_status_id.external_decision:
            self.state = 'revision'
            
    @api.multi
    def button_refuse_external_audit(self):
        self.ensure_one()
        if self.holiday_status_id.employees_director_decision:
            self.state = 'hrm'
        elif self.holiday_status_id.audit:
            self.state = 'audit'
        elif self.holiday_status_id.direct_director_decision:
            self.state = 'dm'
        else:
            self.state = 'draft'
            
    @api.multi
    def button_accept_revision(self):
        self.ensure_one()
        self.state = 'revision_response'
            
    @api.multi
    def button_refuse_revision(self):
        self.ensure_one()
        self.state = 'external_audit'

    def create_holiday_periode(self, employee_id, holiday_status_id, entitlement):
        """
        return: an open periode
        """
        holidays_periode_obj = self.env['hr.holidays.periode']
        if holiday_status_id.id == self.env.ref('smart_hr.data_hr_holiday_status_exceptional').id:
            decision_appoint_ids = self.env['hr.decision.appoint'].sudo().search([('employee_id.id', '=', self.employee_id.id), ('state_appoint', '=', 'active')], limit=1)
            if decision_appoint_ids:
                direct_action_date = decision_appoint_ids[0].date_direct_action
                for decision_appoint in decision_appoint_ids:
                    if fields.Date.from_string(decision_appoint.date_direct_action) < fields.Date.from_string(direct_action_date):
                        direct_action_date = decision_appoint.date_direct_action
                date_direct_action = fields.Date.from_string(direct_action_date)
                date_to = fields.Date.from_string(self.date_to)
                diff = relativedelta(date_to, date_direct_action).years
                years = (diff // entitlement.periode) * entitlement.periode
                date_from = date_direct_action + relativedelta(years=years)
                open_periode = self.env['hr.holidays.periode'].sudo().create({'holiday_status_id': self.env.ref('smart_hr.data_hr_holiday_status_exceptional').id,
                                                                              'employee_id': employee_id.id,
                                                                              'date_to': date_from + relativedelta(years=entitlement.periode),
                                                                              'date_from': date_from,
                                                                              'entitlement_id': entitlement.id,
                                                                              'holiday_stock': entitlement.holiday_stock_default,
                                                                              'active': True
                                                                              })
            else:
                raise ValidationError(u"لا يوجد تعيين مفعل للموظف.")
        elif holiday_status_id.id == self.env.ref('smart_hr.data_hr_holiday_status_illness').id and \
            entitlement.entitlment_category.id in [self.env.ref('smart_hr.data_entitlement_illness_normal').id, self.env.ref('smart_hr.data_entitlement_illness_serious').id]:
            previous_normal_illnes_holidays_ids = holidays_periode_obj.search([('employee_id', '=', employee_id.id), ('holiday_status_id', '=', holiday_status_id.id), ('entitlement_id', '=', entitlement.id), ]).ids
            if previous_normal_illnes_holidays_ids:
                first_id = previous_normal_illnes_holidays_ids and min(previous_normal_illnes_holidays_ids)
                first_date_from = fields.Date.from_string(self.env['hr.holidays.periode'].browse(first_id).date_from)
                date_to = fields.Date.from_string(self.date_to)
                diff = relativedelta(date_to, first_date_from).years
                years = (diff // entitlement.periode) * entitlement.periode
                date_from = first_date_from + relativedelta(years=years)
            else:
                date_from = date.today()

            open_periode = self.env['hr.holidays.periode'].sudo().create({'holiday_status_id': holiday_status_id.id,
                                                           'employee_id': employee_id.id,
                                                            'date_to': date_from + relativedelta(years=entitlement.periode),
                                                            'date_from': date_from,
                                                            'entitlement_id':entitlement.id,
                                                            'holiday_stock':entitlement.holiday_stock_default,
                                                            'active':True
                                                            })
        elif holiday_status_id.id == self.env.ref('smart_hr.data_hr_holiday_accompaniment_exceptional').id and \
            entitlement.entitlment_category.id in [self.env.ref('smart_hr.data_entitlement_accompaniment_exceptional_illness_normal').id, self.env.ref('smart_hr.data_entitlement_accompaniment_exceptional_illness_serious').id]:
            previous_accompaniment_exceptional_holidays_ids = holidays_periode_obj.search([('employee_id', '=', employee_id.id), ('holiday_status_id', '=', holiday_status_id.id), ('entitlement_id', '=', entitlement.id), ]).ids
            if previous_accompaniment_exceptional_holidays_ids:
                first_id = previous_accompaniment_exceptional_holidays_ids and min(previous_accompaniment_exceptional_holidays_ids)
                first_date_from = fields.Date.from_string(self.env['hr.holidays.periode'].browse(first_id).date_from)
                date_to = fields.Date.from_string(self.date_to)
                diff = relativedelta(date_to, first_date_from).years
                years = (diff // entitlement.periode) * entitlement.periode
                date_from = first_date_from + relativedelta(years=years)
            else:
                date_from = date.today()

            open_periode = self.env['hr.holidays.periode'].sudo().create({'holiday_status_id': holiday_status_id.id,
                                                           'employee_id': employee_id.id,
                                                            'date_to': date_from + relativedelta(years=entitlement.periode),
                                                            'date_from': date_from,
                                                            'entitlement_id':entitlement.id,
                                                            'holiday_stock':entitlement.holiday_stock_default,
                                                            'active':True
                                                            })    
        else:
            if holiday_status_id.id == self.env.ref('smart_hr.data_hr_holiday_status_normal').id:
               holiday_stock = 0
            else:
                holiday_stock = entitlement.holiday_stock_default
            date_from = date(date.today().year, 1, 1)
            open_periode = self.env['hr.holidays.periode'].sudo().create({'holiday_status_id': holiday_status_id.id,
                                                           'employee_id': employee_id.id,
                                                            'date_to': date_from + relativedelta(years=entitlement.periode),
                                                            'date_from': date_from,
                                                            'entitlement_id':entitlement.id,
                                                            'holiday_stock':holiday_stock,
                                                            'active':True
                                                            })
        return open_periode
    
    @api.one
    def button_accept_revision_response(self):
        if not self.num_inspeech:
            raise ValidationError(u"الرجاء تعبئة رقم الخطاب الوارد.")
        if not self.date_inspeech:
            raise ValidationError(u"الرجاء تعبئة تاريخ الخطاب الوارد.")
        if not self.inspeech_file:
            raise ValidationError(u"الرجاء إرفاق الخطاب.")
        self.smart_action_done()
        # send notification for the employee who is requesting a holiday
        self.env['base.notification'].create({'title': u'إشعار بقبول إجازة',
                                              'message': u'لقد تم قبول الإجازة من طرف مدقق الاجازات',
                                              'user_id': self.employee_id.user_id.id,
                                              'show_date': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                              'notif': True,
                                              'res_id': self.id,
                                              'res_action': 'smart_hr.action_hr_holidays_form'})
        # check illness holiday periode
#         self.check_holiday_periode_existance(self.employee_id,self.holiday_status_id)
        # update holidays balance
    @api.one
    def button_refuse_revision_response(self):
        self.state = 'refuse'
        # send notification for the employee who is requesting a holiday
        self.env['base.notification'].create({'title': u'إشعار برفض إجازة',
                                              'message': u'لقد تم رفض الإجازة من طرف مدقق الاجازات',
                                              'user_id': self.employee_id.user_id.id,
                                              'show_date': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                             'notif': True,
                                              'res_id': self.id,
                                             'res_action': 'smart_hr.action_hr_holidays_form'})
    

    @api.one
    @api.constrains('date_from', 'date_to')
    def check_dates_periode(self):
        # Objects
        holiday_obj = self.env['hr.holidays']
        candidate_obj = self.env['hr.candidates']
        deput_obj = self.env['hr.deputation']
         
            # Date validation

        if self.date_from > self.date_to:
            raise ValidationError(u"تاريخ من يجب ان يكون أصغر من تاريخ الى")
            # check minimum request validation
        if self.holiday_status_id.minimum != 0 and self.duration < self.holiday_status_id.minimum:
            raise ValidationError(u"أقل فترة يمكن طلبها من نوع إجازة " + self.holiday_status_id.name + u" " + str(self.holiday_status_id.minimum) + u" أيام")
             
            # check maximum request validation
        if self.holiday_status_id.maximum != 0 and self.duration > self.holiday_status_id.maximum:
            raise ValidationError(u"أكثر فترة يمكن طلبها من نوع إجازة " + self.holiday_status_id.name + u" " + str(self.holiday_status_id.maximum) + u" أيام")
    
            # التدريب
        search_domain = [
                ('employee_id', '=', self.employee_id.id),
                ('state', '=', 'done'),
            ]
 
        for rec in candidate_obj.search(search_domain):
            dateto = fields.Date.from_string(rec.date_to)
            datefrom = fields.Date.from_string(rec.date_from)
            res = relativedelta(dateto, datefrom)
            months = res.months
            days = res.days
                # for none normal holidays test
            if self.holiday_status_id != self.env.ref('smart_hr.data_hr_holiday_status_normal') and  self.holiday_status_id != self.env.ref('smart_hr.data_hr_holiday_compensation'):
                if rec.date_from <= self.date_from <= rec.date_to or \
                        rec.date_from <= self.date_to <= rec.date_to or \
                        self.date_from <= rec.date_from <= self.date_to or \
                        self.date_from <= rec.date_to <= self.date_to:
                    raise ValidationError(u"هناك تداخل في التواريخ مع قرار سابق في التدريب")
 
                # for normal holidays test
            else:
                if rec.date_from < self.date_from < rec.date_to and rec.date_from < self.date_to < rec.date_to:
                    if (months < 1) or (months == 1 and days == 0):
                        raise ValidationError(u"الإجازة يتخللها تدريب مدته أقل من شهر.")
                if self.date_from <= rec.date_from <= self.date_to or \
                        self.date_from <= rec.date_to <= self.date_to:
                    raise ValidationError(u"هناك تداخل في التواريخ مع قرار سابق في التدريب")

            # الإنتتبات
        search_domain = [
                ('employee_id', '=', self.employee_id.id),
                ('state', '!=', 'refuse'),
            ]
        for rec in deput_obj.search(search_domain):
            if rec.date_from <= self.date_from <= rec.date_to or \
                    rec.date_from <= self.date_to <= rec.date_to or \
                    self.date_from <= rec.date_from <= self.date_to or \
                    self.date_from <= rec.date_to <= self.date_to:
                raise ValidationError(u"هناك تداخل في التواريخ مع قرار سابق في الإنتداب")
 
            """
 
            TODO: check dates with :أوقات خارج الدوام ... 
 
            """
        hr_public_holiday_obj = self.env['hr.public.holiday']
        if fields.Date.from_string(self.date_from).weekday() in [4, 5] and not self.is_extension:
            raise ValidationError(u"هناك تداخل في تاريخ البدء مع عطلة نهاية الاسبوع  ")
        if fields.Date.from_string(self.date_to).weekday() in [4, 5]:
            raise ValidationError(u"هناك تداخل في تاريخ الإنتهاء مع عطلة نهاية الاسبوع")
        for public_holiday in hr_public_holiday_obj.search([('state', '=', 'done')]):
            if not self.is_extension:
                if public_holiday.date_from <= self.date_from <= public_holiday.date_to or \
                    public_holiday.date_from <= self.date_to <= public_holiday.date_to or \
                    self.date_from <= public_holiday.date_from <= self.date_to or \
                    self.date_from <= public_holiday.date_to <= self.date_to :
                    raise ValidationError(u"هناك تداخل فى التواريخ مع اعياد و عطل رسمية")
                
            # خارج الدوام
        if self.holiday_status_id != self.env.ref('smart_hr.data_hr_holiday_status_compelling'):
            search_domain = [
                ('employee_id', '=', self.employee_id.id),
                ('overtime_id.state', '=', 'done'),
                ]
            overtime_line_obj = self.env['hr.overtime.line']

            for rec in overtime_line_obj.search(search_domain):
                if rec.date_from <= self.date_from <= rec.date_to or \
                        rec.date_from <= self.date_to <= rec.date_to or \
                        self.date_from <= rec.date_from <= self.date_to or \
                        self.date_from <= rec.date_to <= self.date_to:
                    raise ValidationError(u"هناك تداخل في التواريخ مع قرار سابق في تكليف")
                                      
    @api.multi
    def check_constraintes(self):
        """
        check constraintes beside date and periode ones
        """
        right_entitlement = False
        if not self.entitlement_type:
            entitlement_type = self.env.ref('smart_hr.data_hr_holiday_entitlement_all')
        else:
            entitlement_type = self.entitlement_type
        for en in self.holiday_status_id.entitlements:
            if en.entitlment_category.id == entitlement_type.id:
                right_entitlement = en
                break
        if not right_entitlement:
            raise ValidationError(u" الرجاء مراجعة الإستحقاقات في إعدادات الإجازة")

        date_from = fields.Date.from_string(self.date_from)

        # check if there is another undone request for the same status of holiday
        if self.holiday_status_id in [self.env.ref('smart_hr.data_hr_holiday_status_normal'), self.env.ref('smart_hr.data_hr_holiday_status_exceptional'), self.env.ref('smart_hr.data_hr_holiday_status_compelling')]:
            # check if there is another undone request for the same status of holiday
            domain_search = [
                ('state', 'not in', ['done', 'refuse', 'cancel']),
                ('employee_id.id', '=', self.employee_id.id),
                ('holiday_status_id.id', '=', self.holiday_status_id.id),
                ('id', '!=', self.id)]
            if self.search_count(domain_search) > 0:
                raise ValidationError(u"لديك طلب قيد الإجراء من نفس هذا النوع من الإجازة.")

        # Constraintes for employee's nationnality
        if self.holiday_status_id.for_saudi and not self.holiday_status_id.for_other:
            # check the nationnality of the employee if it is saudi
            if self.employee_id.country_id != self.env.ref('base.sa'):
                raise ValidationError(u"هذا النوع من الإجازة ينطبق فقط على السعوديين.")

        # Constraintes for studyinglevel
        if self.holiday_status_id.educ_lvl_req:
            # check education level
            if self.employee_id.education_level not in self.holiday_status_id.education_levels:
                raise ValidationError(u"لم تتحصل على المستوى الدراسي المطلوب.")
            
        # Constraintes for service years required
        if self.holiday_status_id.service_years_required*364>self.employee_id.service_duration:
            # check education level
                raise ValidationError(u" ليس لديك"+ str(self.holiday_status_id.service_years_required)+u"سنوات خدمة  ")
            
         # Constraintes for evaluation_required
        if self.holiday_status_id.evaluation_condition:
            employee_evaluation_id = self.env['hr.employee.evaluation.level'].search([('employee_id', '=', self.employee_id.id),('year', '=',date_from.year-1)], limit=1)
            if employee_evaluation_id:
                if employee_evaluation_id.degree_id.id not in self.holiday_status_id.evaluation_required.ids:
                    raise ValidationError(u"لم تتحصل على تقييم أدائ وظيفي‬ المطلوب.")
            else:
                raise ValidationError(u"لا يوجد تقييم وظيفي خاص بالموظف للسنة الفارطة")
            
            
        holiday_status_normal_stock = self.env['hr.employee.holidays.stock'].search([('employee_id', '=', self.employee_id.id), ('holiday_status_id', '=', self.env.ref('smart_hr.data_hr_holiday_status_normal').id)]).holidays_available_stock

        # Constraintes for maximum_days_by_year
        for holidays_balance in self.employee_id.holidays_balance:
            if holidays_balance.holiday_status_id == self.holiday_status_id:
                taken_holidays_days_by_year = holidays_balance.token_holidays_sum
                if taken_holidays_days_by_year + self.duration >= self.holiday_status_id.maximum_days_by_year and self.holiday_status_id.maximum_days_by_year != 0:
                    raise ValidationError(u"الحد الأقصى للتمتع بهذا النّوع من الإجازات خلال السنة" + str(self.holiday_status_id.maximum_days_by_year) + u"يوما")
        # demand_number_max
        if self.holiday_status_id.demand_number_max > 0:
            past_demand_number = self.env['hr.holidays'].search_count([('state', '=', 'done'), ('employee_id', '=', self.employee_id.id),
                                                                   ('holiday_status_id', '=', self.holiday_status_id.id), ('date_from', '>=', date(date_from.year, 1, 1))])
            if self.holiday_status_id.demand_number_max <= past_demand_number :
                raise ValidationError(u" لا يمكن تجزئة هذا النوع من الإجازات على أكثر من %s مرّة " % self.holiday_status_id.demand_number_max)
                  
                    
                # Constraintes for Compelling holidays  اجازة مرافقة استثنائية+ اضطرارية
        if self.holiday_status_id in [self.env.ref('smart_hr.data_hr_holiday_status_compelling'), self.env.ref('smart_hr.data_hr_holiday_accompaniment_exceptional')]:
            if holiday_status_normal_stock > 0:
                raise ValidationError(u"يوجد رصيد في الإجازات العاديّة")
        
                    # Constraintes for childbirth holidays وضع
        if self.holiday_status_id == self.env.ref('smart_hr.data_hr_holiday_status_childbirth'):
            if self.employee_id.gender != 'female':
                raise ValidationError(u"لا يتمتّع بإجازة الوضع إلّا النساء")
            date_from = fields.Date.from_string(self.date_from)
            date_birth = fields.Date.from_string(self.childbirth_date)
            if (date_from - date_birth).days > 14:
                raise ValidationError(u" لا يمكن لتاريخ بداية إجازة الوضع ان يتجاوز تاريخ الوضع بأسبوعين")
            print 'الوضع'

                        # Constraintes for maternity الامومة
        if self.holiday_status_id == self.env.ref('smart_hr.data_hr_holiday_status_maternity'):
            if self.employee_id.gender != 'female':
                raise ValidationError(u"لا يتمتّع بإجازة الامومة إلّا النساء")
            date_from = fields.Date.from_string(self.date_from)
            date_birth = fields.Date.from_string(self.childbirth_date)
            if (date_from - date_birth).days > 1095:
                raise ValidationError(u"لا يمكن التمتع باجازة الامومة بعد اكثر من ثلاث سنوات من الوضع")

        # Constraintes for adoption الحضانة
        if self.holiday_status_id == self.env.ref('smart_hr.data_hr_holiday_status_adoption'):
            if self.employee_id.gender != 'female':
                raise ValidationError(u"لا يتمتّع بإجازة الحضانة إلّا النساء")

        # Constraintes for child_birth_dad المولود
        if self.holiday_status_id == self.env.ref('smart_hr.data_hr_holiday_child_birth_dad'):
            if self.employee_id.gender != 'male':
                raise ValidationError(u"لا يتمتّع بإجازة المولود إلّا الرجال")
            date_birth = fields.Date.from_string(self.childbirth_date)
            date_from = fields.Date.from_string(self.date_from)
            if (date_from - date_birth).days > 7:
                raise ValidationError(u"لا يمكن لتاريخ بداية إجازة المولود ان يتجاوز تاريخ الوضع بأسبوع")            
 



        # Constraintes for accompaniment_exceptional اجازة مرافقة استثنائية
        if self.holiday_status_id == self.env.ref('smart_hr.data_hr_holiday_accompaniment_exceptional'):
            if self.accompaniment_type == "child" and self.employee_id.gender != 'female':
                raise ValidationError(u"لا يتمتّع بإجازة مرافقة طفل  إلّا النساء")
            if self.accompaniment_type == "child" and self.accompanied_child_age > 7:
                raise ValidationError(u"يجب أن يكون عمر الطفل أقل من 7 سنوات")
                    
                      
        # الرصيد الكافي
        if right_entitlement.periode and right_entitlement.periode != 100 and self.holiday_status_id.id != self.env.ref('smart_hr.data_hr_holiday_compensation').id:
            periodes = self.env['hr.holidays.periode'].search([('employee_id', '=', self.employee_id.id),
                                                           ('holiday_status_id', '=', self.holiday_status_id.id),
                                                           ('entitlement_id', '=', right_entitlement.id),
                                                           ('active', '=', True),
                                                           ])
            open_periode = False
            if periodes:
                for periode in periodes:
                    if fields.Datetime.from_string(periode.date_to) > fields.Datetime.from_string(self.date_to) and fields.Datetime.from_string(periode.date_from) < fields.Datetime.from_string(self.date_from):
                        open_periode = periode
                        if self.duration > open_periode.holiday_stock:
                            raise ValidationError(u"ليس لديك الرصيد الكافي")
                        else:
                            if fields.Datetime.from_string(periode.date_to) < fields.Datetime.from_string(self.date_from):
                                raise ValidationError(u"ليس لديك فترة اجازة مفتوحة")
                        break
                    else:
                        periode.active = False
            else:
                if right_entitlement.holiday_stock_default < self.duration:
                    raise ValidationError(u"ليس لديك الرصيد الكافي")
                else:
                    if self.holiday_status_id.id == self.env.ref('smart_hr.data_hr_holiday_status_exceptional').id:
                        date_direct_action_ids = self.env['hr.decision.appoint'].sudo().search([ ('employee_id', '=', self.employee_id.id), ('state', '=', 'done')])
                        if date_direct_action_ids:
                            first_id = date_direct_action_ids.ids and max(date_direct_action_ids).ids
                            direct_action_date = self.env['hr.decision.appoint'].sudo().browse(first_id).date_direct_action
                            date_direct_action = fields.Date.from_string(direct_action_date)
                            h_date_to = fields.Date.from_string(self.date_to)
                            diff = relativedelta(h_date_to, date_direct_action).years
                            years = (diff // right_entitlement.periode) * right_entitlement.periode
                            date_from = date_direct_action + relativedelta(years=years)
                        else:
                            raise ValidationError(u"لا يوجد تعيين مفعل للموظف.")
                    else:
                        date_from = date(date.today().year, 1, 1)
                    date_to = date_from + relativedelta(years=right_entitlement.periode)
                    if fields.Date.from_string(self.date_to) > date_to:
                        raise ValidationError(u"لا يمكن حجز اجازة من هذا النوع خارج السنة الجارية")
        else:
            if right_entitlement.periode == 100:
                stock_line = self.env['hr.employee.holidays.stock'].search ([('employee_id', '=', self.employee_id.id),
                                                                         ('holiday_status_id', '=', self.holiday_status_id.id),
                                                                         ('entitlement_id.id', '=', right_entitlement.id),
                                                                         ])
                if stock_line:
                    if stock_line.holidays_available_stock < self.duration:
                        raise ValidationError(u"ليس لديك الرصيد الكافي")
                else:
                    if right_entitlement.holiday_stock_default < self.duration:
                        raise ValidationError(u"ليس لديك الرصيد الكافي")
            else:
                if right_entitlement.holiday_stock_default < self.duration and right_entitlement.holiday_stock_default > 0:
                    raise ValidationError(u"ليس لديك الرصيد الكافي") 
        
        if self.holiday_status_id.id == self.env.ref('smart_hr.data_hr_holiday_compensation').id and self.duration > self.employee_id.compensation_stock:
            raise ValidationError(u"ليس لديك الرصيد الكافي") 


    @api.model
    def create(self, vals):
        res = super(HrHolidays, self).create(vals)
        res.check_constraintes()
        # Sequence
        vals = {}
        vals['state'] = 'draft'
        vals['name'] = self.env['ir.sequence'].get('hr.holidays.seq')
        res.write(vals)
        return res

class HrHolidaysPeriode(models.Model):

    _name = 'hr.holidays.periode'
    _description = 'فترات الاجازة'
    
    employee_id = fields.Many2one('hr.employee')
    date_from = fields.Datetime(string=u'التاريخ من', default=fields.Datetime.now())
    date_to = fields.Datetime(string=u'التاريخ الى')
    holiday_status_id = fields.Many2one('hr.holidays.status', string=u'نوع الإجازة')
    entitlement_id = fields.Many2one('hr.holidays.status.entitlement', string=u'نوع الاستحقاق')
    holiday_stock = fields.Integer(string=u'الرصيد (يوم)')
    active = fields.Boolean(string=u'active')
    
    @api.model
    def update_holidays_periodes(self):
        for periode in self.search([('active', '=', True)]):
            if fields.Date.from_string(periode.date_to) < fields.Date.from_string(fields.Date.today()):
                periode.active = False

    
    
    
    
class HrDelayHoliday(models.Model):
    _name = 'hr.delay.holiday'  
    _description = u'تأجيل إجازة'
    
    date_from = fields.Date(string=u'التاريخ من', default=lambda self: self.env['hr.holidays'].search([('id', '=', self._context['holiday_id'])], limit=1).date_from)
    date_to = fields.Date(string=u'التاريخ الى', readonly=1, default=lambda self: self.env['hr.holidays'].search([('id', '=', self._context['holiday_id'])], limit=1).date_to)
    delay_days = fields.Integer(string=u'عدد أيام التأجيل', compute='_compute_delay_days')

    @api.depends('date_from', 'date_to')
    def _compute_delay_days(self):
        holiday = self.env['hr.holidays'].search([('id', '=', self._context['holiday_id'])])
        for holidayDelay in self:
            if holidayDelay.date_from and holidayDelay.date_to:
                start_date = fields.Date.from_string(holiday.date_from)
                new_start_date = fields.Date.from_string(holidayDelay.date_from)
                if new_start_date < start_date:
                    raise ValidationError(u"الرجاء التأكد من تاريخ بد الإجازة.")
                delay_days = (new_start_date - start_date).days 
                holidayDelay.delay_days = delay_days
                holidayDelay.date_to = fields.Date.from_string(holiday.date_to) + timedelta(days=self.delay_days)
    
    
    @api.multi
    def action_delay_holiday_confirm(self):
        holiday = self.env['hr.holidays'].search([('id', '=', self._context['holiday_id'])])
        if holiday.holiday_status_id.postponement_period > 0:
            if self.delay_days > 0 and self.delay_days <= holiday.holiday_status_id.postponement_period:
                # add delay_days to date_from and date_to of the holiday
                new_date_from = fields.Date.from_string(holiday.date_from) + timedelta(days=self.delay_days)
                new_date_to = fields.Date.from_string(holiday.date_to) + timedelta(days=self.delay_days)
                holiday.write({'date_from': new_date_from, 'date_to': new_date_to, 'state': 'draft'})
    
            if self.delay_days > 0 and self.delay_days > holiday.holiday_status_id.postponement_period:
                raise ValidationError(u"لا يمكن تأجيل هذا النوع من الاجازة أكثر من " + str(holiday.holiday_status_id.postponement_period) + u"يوماً.")
        else:
            raise ValidationError(u"لا يمكن تأجيل هذا النوع من الاجازة. ")

class HrHolidaysStatus(models.Model):
    _name = 'hr.holidays.status'
    _inherit = 'hr.holidays.status'
    _description = 'holidays status'

    name = fields.Char(string=u'نوع الاجازة')
    minimum = fields.Integer(string=u'الحد الأدنى في المرة الواحدة')
    maximum = fields.Integer(string=u'الحد الأقصى في المرة الواحدة')
    postponement_period = fields.Integer(string=u'مدة التأجيل')
    extension_number = fields.Integer(string=u'عدد مرات تمديد', default=-1)
    deductible_normal_leave = fields.Boolean(string=u'تخصم مدتها من رصيد الاجازة العادية')
    deductible_duration_service = fields.Boolean(string=u'تخصم مدتها من فترة الخدمة')
    educ_lvl_req = fields.Boolean(string=u'يطبق شرط المستوى التعليمي')
    need_decision = fields.Boolean(string=u' تحتاج إلى قرار')
    direct_decision = fields.Boolean(string=u'تحتاج إلى قرار مباشرة')
    direct_director_decision = fields.Boolean(string=u'موافقة مدير مباشر', default=True)
    external_decision = fields.Boolean(string=u'موافقة خارجية', default=False)
    salary_spending = fields.Boolean(string=u'يجوز صرف راتبها')
    employees_director_decision = fields.Boolean(string=u'موافقة مدير شؤون الموظفين', default=True)
    can_be_cancelled = fields.Boolean(string=u'يمكن الغاؤها', default=True)
    evaluation_condition = fields.Boolean(string=u'يطبق شرط تقييم الأداء')
    education_levels = fields.One2many('hr.employee.education.level', 'leave_type', string=u'المستويات التعليمية')
    entitlements = fields.One2many('hr.holidays.status.entitlement', 'leave_type', string=u'أنواع الاستحقاقات')
    evaluation_required = fields.Many2many('hr.evaluation.result.foctionality', string=u'التقييمات المطلوبة')
    percentages = fields.One2many('hr.holidays.status.salary.percentage', 'holiday_status', string=u'نسب الراتب المحتسبة')
    for_saudi = fields.Boolean(string=u'تنطبق على السعوديين', default=True)
    for_other = fields.Boolean(string=u'تنطبق على غير السعوديين', default=True)
    promotion_deductible = fields.Boolean(string=u'تخصم مدتها من رصيد الترقية', default=False)
    min_amount = fields.Float(string=u'المبلغ الادنى') 
    pension_percent = fields.Float(string=u' (%)نسبة راتب التقاعد') 
    demand_number_max = fields.Integer(string=u'عدد مرات الطلب', default='-1')
    traveling_ticket = fields.Boolean(string=u'تذكرة سفر', default=False)
    traveling_family_ticket = fields.Boolean(string=u'تذكرة سفر عائليّة', default=False)
    
    transport_allowance = fields.Boolean(string=u'صرف بدل النقل', default=False)
    maximum_days_by_year = fields.Integer(string=u'الحد الأقصى لأيّامات الإجازات في السّنة')
    audit = fields.Boolean(string=u'تدقيق', default=False)
    service_years_required = fields.Integer(string=u'سنوات الخدمة المطلوبة', default=0)

    @api.onchange('deductible_duration_service')
    def onchange_deductible_duration_service(self):
        if self.deductible_duration_service:
            self.promotion_deductible = True

    @api.one
    @api.constrains('pension_percent')
    def check_pension_percent(self):
        if self.pension_percent < 0 or self.pension_percent > 100:
            raise ValidationError(u"نسبة راتب التقاعد خاطئة ")
                
class HrHolidaysStatusEntitlement(models.Model):
    _name = 'hr.holidays.status.entitlement'
    _description = u'أنواع الاستحقاقات'
    entitlment_category = fields.Many2one('hr.holidays.entitlement.config', string=u'خاصيّة الإجازة')
    holiday_stock_default = fields.Integer(string=u'الرصيد (يوم)')
    conditionnal = fields.Boolean(string=u'مشروط')
    periode = fields.Selection([
        (1, u'سنة'),
        (2, u'سنتين'),
        (3, u'ثلاث سنوات'),
        (4, u'أربع سنوات'),
        (5, u'خمس سنوات'),
        (6, u'ستة سنوات'),
        (7, u'سبعة سنوات'),
        (8, u'ثمانية سنوات'),
        (9, u'تسعة سنوات'),
        (10, u'عشرة سنوات'),
        (100, u'طوال مدة الخدمة الوظيفيّة'),
        ], string=u'مدّة الصّلاحِيّة', default=1)
    leave_type = fields.Many2one('hr.holidays.status', string='leave type')
#     holiday_stock_open = fields.Boolean(string=u'الرصيد مفتوح')
    extension_period = fields.Integer(string=u'مدة تمديد الرصيد(سنة)', default=0)
    
class HrHolidaysStatusSalaryPercentage(models.Model):
    _name = 'hr.holidays.status.salary.percentage'
    _description = u'نسب الراتب المحتسبة'

    sequence = fields.Integer(string=u'الأولوية')
    periode = fields.Integer(string=u'عدد الأشهر')
    salary_proportion = fields.Float(string=u'نسبة الراتب (%)', default=100) 
    holiday_status = fields.Many2one('hr.holidays.status', string='holiday status')

class EntitlementConfig(models.Model):
    _name = 'hr.holidays.entitlement.config'
    _description = u' اصناف الاستحقاقات'

    name = fields.Char(string=u'المسمّى')
    code = fields.Char(string='code')



