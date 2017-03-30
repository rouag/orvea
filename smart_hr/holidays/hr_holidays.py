# -*- coding: utf-8 -*-

from openerp import fields, models, api, _
from openerp.tools import SUPERUSER_ID
from openerp.exceptions import ValidationError
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
import datetime as dt


class HrHolidays(models.Model):
    _inherit = 'hr.holidays'
    _description = 'hr holidays Request'
    _order = 'id desc'

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        #inherit read_group to count holidays type deductible_normal_leave with normal holidays
        res = super(HrHolidays, self).read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)
        if 'holiday_status_id' in groupby:
            for line in res:
                normal_holiday_status_id = self.env.ref('smart_hr.data_hr_holiday_status_normal').id
                domain = line['__domain']
                if '__domain' in line and domain == [('holiday_status_id', '=', normal_holiday_status_id)]:
                    lines = self.search(['|', ('holiday_status_id', '=', normal_holiday_status_id), ('holiday_status_id.deductible_normal_leave', '=', True)])
                    hol_count = 0.0
                    for line2 in lines:
                        hol_count += line2.duration
                    line['duration'] = hol_count
        return res

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
        for holiday in self:
            search_external_authoritie = self.env["external.authorities"].search([('holiday_status', '=', holiday.holiday_status_id.id)])
            if search_external_authoritie:
                holiday.external_authoritie = search_external_authoritie[0]

    name = fields.Char(string=u'رقم القرار',)
    date = fields.Date(string=u'تاريخ الطلب', default=fields.Datetime.now)
    employee_id = fields.Many2one('hr.employee', string=u'الموظف', domain=[('emp_state', 'not in', ['suspended','terminated']), ('employee_state', '=', 'employee')],
                                  default=lambda self: self.env['hr.employee'].search([('user_id', '=', self._uid), ('emp_state', 'not in', ['suspended','terminated'])], limit=1),)
    raison = fields.Selection([('other', u'سبب أخر'), ('husband', u'مرافقة الزوج'),
                               ('wife', u'مرافقة الزوجة'), ('legit', u'مرافقة كمحرم شرعي')],
                               default="other", string=u'السبب ')
    date_from = fields.Date(string=u'التاريخ من ', default=fields.Datetime.now)
    date_to = fields.Date(string=u'التاريخ الى')
    duration = fields.Integer(string=u'مدتها' , required=1,default=1)
    holiday_status_id = fields.Many2one('hr.holidays.status', string=u'نوع الأجازة', default=lambda self: self.env.ref('smart_hr.data_hr_holiday_status_normal'),)
    spend_advanced_salary = fields.Boolean(string=u'طلب صرف راتب مسبق', related='holiday_status_id.spend_advanced_salary')
    advanced_salary_periode = fields.Integer(string=u'مدة صرف راتب مسبق (باليوم)', related='holiday_status_id.advanced_salary_periode')
    with_advanced_salary = fields.Boolean(string=u'مع صرف راتب مسبقاً', readonly=1, states={'draft': [('readonly', 0)]})
    state = fields.Selection([
        ('draft', u'طلب'),
        ('dm', u'مدير المباشر'),
        ('audit', u'تدقيق'),
        ('hrm', u'مدير شؤون الموظفين'),
        ('external_audit', u'جهة خارجية'),
        ('revision', u'مراجعة الخطاب'),
        ('revision_response', u'تسجيل رد الجهة'),
        ('done', u'اعتمدت'),
        ('cancel', u'ملغاة'),
        ('cutoff', u'مقطوعة'),
        ('refuse', u'مرفوضة'),
        ('confirm', 'To Approve'),
        ('unkhown', 'غير معروف'),
        ('validate1', 'Second Approval'),
        ('validate', 'Approved')], string=u'حالة', default='draft',)

    is_current_user = fields.Boolean(string='Is Current User', compute='_is_current_user')
    is_direct_manager = fields.Boolean(string='Is Direct Manager', compute='_is_direct_manager')
    is_delayed = fields.Boolean(string='is_delayed', default=False)
    num_outspeech = fields.Char(string=u'رقم الخطاب الصادر')
    date_outspeech = fields.Date(string=u'تاريخ الخطاب الصادر')
    outspeech_file = fields.Binary(string=u'الخطاب الصادر', attachment=True)
    outspeech_file_name = fields.Char(string=u'file name')

    num_inspeech = fields.Char(string=u'رقم الخطاب الوارد')
    date_inspeech = fields.Date(string=u'تاريخ الخطاب الوارد')
    inspeech_file = fields.Binary(string=u'الخطاب الوارد', attachment=True)
    inspeech_file_name = fields.Char(string=u'الخطاب الوارد name')
    # Cancellation
    is_cancelled = fields.Boolean(string=u'ملغاة', compute='_is_cancelled')
    is_started = fields.Boolean(string=u'بدأت', compute='_compute_is_started')
    is_finished = fields.Boolean(string=u'انتهت', compute='_compute_is_finished')
    holiday_cancellation = fields.Many2one('hr.holidays.cancellation')    
    # Extension
    is_extension = fields.Boolean(string=u'اجازة ممددة')
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
    birth_certificate = fields.Binary(string=u'شهادة الميلاد', attachment=True)
    extension_period = fields.Integer(string=u'مدة التمديد', default=0)
    external_authoritie = fields.Many2one('external.authorities', string=u'الجهة الخارجية', compute="_set_external_autoritie")
    entitlement_type = fields.Many2one('hr.holidays.entitlement.config', string=u'خاصيّة الإجازة')
    sold_overtime = fields.Float(string=u' رصيد خارج الدوام')
    sold_attendance = fields.Float(string=u'رصيد الحضور و الإنصراف')
    death_person = fields.Char(string=u'المتوفي')
    medical_certification = fields.Binary(string=u'الشهادة الطبية', attachment=True)
    compensation_type = fields.Selection([
        ('holiday', u'إجازة'),
        ('money', u' مقابل ‫مادي‬ ‬ ')], string=u'نوع التعويض')
    accompaniment_type = fields.Selection([
        ('Relatives', u'أحد الأقارب '),
        ('child', u' ‫طفل‬‬')], string=u'نوع المرافقة')
    accompanied_child_age = fields.Integer(string=u'عمر الطفل')
    open_period = fields.Many2one('hr.holidays.periode', string=u'periode')
    medical_report = fields.Binary(string=u'التقرير الطبي', attachment=True)
    prove_exam_duration = fields.Binary(string=u'إثبات اداء الامتحان ومدته', attachment=True)
    study_subject = fields.Char(string=u'موضوع‬ ‫الدِّراسة')
    out_speech_file_name = fields.Char(string=u'مسمى صورة الخطاب الصادر')
    in_speech_file_name = fields.Char(string=u'مسمى صورة الخطاب الوارد')
    birth_certificate_file_name = fields.Char(string=u'مسمى شهادة الميلا')
    medical_certification_file_name = fields.Char(string=u'الشهادة الطبيةا')
    medical_report_file_name = fields.Char(string=u'التقرير الطبي')
    prove_exam_duration_name = fields.Char(string=u'إثبات اداء الامتحان ومدته مسمى')
    medical_report_number = fields.Char(string=u'رقم التقرير الطبي')
    medical_report_date = fields.Date(string=u'تاريخ التقرير الطبي')
    courses_city = fields.Many2one('res.city', string=u'المدينة',)
    courses_country = fields.Many2one('res.country', string=u'البلاد')
    current_holiday_stock = fields.Char(string=u'الرصيد الحالي', compute='_compute_current_holiday_stock')
    sport_participation_topic = fields.Char(string=u'موضوع المشاركة')
    birth_certificate_child_birth_dad = fields.Binary(string=u'شهادة الميلاد', attachment=True)
    birth_certificate_file_name_file_name = fields.Char(string=u'شهادة الميلاد')
    speech_source = fields.Char(string=u'مصدر الخطابات')
    hide_with_advanced_salary = fields.Boolean('hide_with_advanced_salary', default=True)
    # token_compen#id=4&view_type=form&model=salary.grid.grade&menu_id=603sation_stock will take the value of the compensation_stock for tracability
    token_compensation_stock = fields.Integer(string=u'الرصيد المأخوذ', default=0)
    compute_as_deputation = fields.Boolean(string=u'تحتسب هذه المدة انتدابا', default=False)
    display_compute_as_deputation = fields.Boolean('hide_compute_as_deputation', default=False)
    deputation_id = fields.Many2one('hr.deputation', string='الانتداب')
    deputation_balance_computed = fields.Float(string='مدة الانتداب المحتسبة', compute='compute_deputation_balance_compUted')
    can_be_cutted = fields.Boolean(string=u'يمكن قطعها',related='holiday_status_id.can_be_cutted')
    can_be_cancelled = fields.Boolean(string=u'يمكن الغاؤها', related='holiday_status_id.can_be_cancelled')
    display_button_cancel = fields.Boolean(compute='_compute_display_button_cancel')
    display_button_cut = fields.Boolean(compute='_compute_display_button_cut')
    salary_number = fields.Integer(string=u'عدد الرواتب')
    is_holidays_specialist_user = fields.Boolean(string='Is Current User holidays specialist', compute='_is_holidays_specialist_user')

    _constraints = [
        (_check_date, 'You can not have 2 leaves that overlaps on same day!', ['date_from', 'date_to']),
    ]
    
    def _is_holidays_specialist_user(self):
        for rec in self:
            if self.env.user.has_group('smart_hr.group_holidays_specialist'):
                rec.is_holidays_specialist_user = True

    @api.onchange('salary_number','duartion')
    def onchange_salary_number(self):
        if self.duration and self.salary_number:
            if self.duration< self.salary_number*30:
                raise ValidationError(u"لا يمكن طلب اكثر من" + str(self.duration//30) +u"رواتب مسبقة")

    @api.multi
    def _compute_display_button_cancel(self):
        for rec in self:
            if not rec.can_be_cancelled or rec.state != 'done' or rec.is_cancelled is True or rec.is_started is True or rec.is_finished is True or (rec.is_current_user is False and rec.is_holidays_specialist_user is False):
                rec.display_button_cancel = False
            else:
                rec.display_button_cancel = True

    @api.multi
    def _compute_display_button_cut(self):
        for rec in self:
            if not rec.can_be_cutted or rec.state != 'done' or rec.is_cancelled is True or rec.is_started is False or rec.is_finished is True or rec.is_finished is True or (rec.is_current_user is False and rec.is_holidays_specialist_user is False):
                rec.display_button_cut = False
            else:
                rec.display_button_cut = True

    @api.multi
    @api.depends("deputation_id")
    def compute_deputation_balance_compUted(self):

        for rec in self:
            if rec.deputation_id:
                deputation_date_from = fields.Date.from_string(rec.deputation_id.date_from)
                deputation_date_to = fields.Date.from_string(rec.deputation_id.date_to)
                rest_days_deputation = (deputation_date_to - deputation_date_from).days
                half_holiday_duration = rec.duration / 2
                if half_holiday_duration < 21:
                    min_duration = half_holiday_duration
                else:
                    min_duration = 21
                if rec.duration > rest_days_deputation:
                    rec.deputation_balance_computed = rest_days_deputation
                else:
                    rec.deputation_balance_computed = min_duration

    def _get_current_holiday_stock(self, employee_id, holiday_status_id, entitlement_type):
            current_stock = 0
            not_need_stock = False
            entitlement_line = False
            if holiday_status_id  and holiday_status_id.id != self.env.ref('smart_hr.data_hr_holiday_compensation').id:
                if entitlement_type:
                    stock_line = self.env['hr.employee.holidays.stock'].search([('employee_id', '=', employee_id.id), ('holiday_status_id', '=', holiday_status_id.id),
                                                               ('entitlement_id.entitlment_category.id', '=', entitlement_type.id)])
                    entitlement_line = self.env['hr.holidays.status.entitlement'].search([('leave_type', '=', holiday_status_id.id),
                                                               ('entitlment_category.id', '=', entitlement_type.id)])
                else:
                    stock_line = self.env['hr.employee.holidays.stock'].search([('employee_id', '=', employee_id.id), ('holiday_status_id', '=', holiday_status_id.id),
                                                               ])
                    not_all_entitlement_line = self.env['hr.holidays.status.entitlement'].search_count([('leave_type', '=', holiday_status_id.id),
                                                                                                    ('entitlment_category.id', '!=', self.env.ref('smart_hr.data_hr_holiday_entitlement_all').id)
                                                                                                   ])
                    if not_all_entitlement_line == 0:
                        entitlement_line = self.env['hr.holidays.status.entitlement'].search([('leave_type', '=', holiday_status_id.id),
                                                               ('entitlment_category.id', '=', self.env.ref('smart_hr.data_hr_holiday_entitlement_all').id)])
                if stock_line:
                    if entitlement_line.periode:
                        current_stock = stock_line.holidays_available_stock
                    else:
                        current_stock = entitlement_line.holiday_stock_default
                elif entitlement_line and entitlement_line.periode:
                    current_stock = entitlement_line.holiday_stock_default
                elif entitlement_line and not entitlement_line.periode:
                    current_stock = entitlement_line.holiday_stock_default
                if entitlement_line and not entitlement_line.periode and entitlement_line.holiday_stock_default == 0:
                    not_need_stock = True

            if holiday_status_id.id == self.env.ref('smart_hr.data_hr_holiday_compensation').id:
                current_stock = employee_id.compensation_stock
            if holiday_status_id.id == self.env.ref('smart_hr.data_hr_holiday_status_legal_absent').id:
                return self._get_current_holiday_stock(employee_id, self.env.ref('smart_hr.data_hr_holiday_status_normal'), False)
            return{'current_stock': current_stock, 'not_need_stock': not_need_stock}

    @api.multi
    @api.depends("holiday_status_id", "entitlement_type")
    def _compute_current_holiday_stock(self):
        for holiday in self:
            entitlement_type = holiday.entitlement_type if holiday.entitlement_type else False
            stock = self._get_current_holiday_stock(holiday.employee_id, holiday.holiday_status_id, entitlement_type)
            if stock['current_stock'] == 0 and stock['not_need_stock']:
                current_stock = str("لا تحتاج رصيد")
            else:
                current_stock = stock['current_stock']
            holiday.current_holiday_stock = current_stock

    @api.multi
    def _compute_is_started(self):
        for rec in self:
            if rec.date_from <= datetime.today().strftime('%Y-%m-%d'):
                rec.is_started = True
                
    @api.multi
    def _compute_is_finished(self):
        for rec in self:
            if rec.date_to < datetime.today().strftime('%Y-%m-%d'):
                rec.is_finished = True
                
    @api.multi
    @api.onchange('holiday_status_id', 'duration')
    def onchange_hide_with_advanced_salary(self):
        for rec in self:
            if rec.holiday_status_id and rec.duration:
                if rec.holiday_status_id.spend_advanced_salary and rec.duration >= rec.holiday_status_id.advanced_salary_periode:
                    rec.hide_with_advanced_salary = False
                else:
                    rec.hide_with_advanced_salary = True

    @api.onchange('holiday_status_id')
    def onchange_holiday_status_id(self):
        res = {}
        if self.holiday_status_id == self.env.ref('smart_hr.data_hr_holiday_status_illness'):
            res['domain'] = {'entitlement_type': [('code', '=', 'illness')]}
        if self.holiday_status_id == self.env.ref('smart_hr.data_hr_holiday_death'):
            if self.employee_id:
                gender = self.employee_id.gender
                if gender == 'female':
                    res['domain'] = {'entitlement_type': [('code', '=', 'death')]}
                else:
                    data_hr_holiday_entitlement_types_parent = self.env.ref('smart_hr.data_hr_holiday_entitlement_types_parent').id
                    data_hr_holiday_entitlement_types_branch = self.env.ref('smart_hr.data_hr_holiday_entitlement_types_branch').id
                    domain_male = [data_hr_holiday_entitlement_types_parent, data_hr_holiday_entitlement_types_branch]
                    res['domain'] = {'entitlement_type': [('id', 'in', domain_male)]}
        if self.holiday_status_id == self.env.ref('smart_hr.data_hr_holiday_accompaniment_exceptional'):
            res['domain'] = {'entitlement_type': [('code', '=', 'accompaniment_exceptional')]}
        if self.holiday_status_id == self.env.ref('smart_hr.data_hr_holiday_status_sport'):
            res['domain'] = {'entitlement_type': [('code', '=', 'sport')]}
        self.entitlement_type = False
        return res

    @api.onchange('entitlement_type','holiday_status_id')
    def onchange_entitlement_type(self):
        deput_obj = self.env['hr.deputation']
        if self.entitlement_type and self.holiday_status_id:
            if self.entitlement_type.id == self.env.ref('smart_hr.data_entitlement_illness_normal').id:
                search_domain = [
                    ('employee_id', '=', self.employee_id.id),
                    ('state', '=', 'done'),
                    ('date_from', '<=', self.date_from),
                    ('date_to', '>=', self.date_from)
                    ]
                in_deputation = deput_obj.search_count(search_domain)
                if in_deputation:
                    self.display_compute_as_deputation = True

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        res = {}
        if self.employee_id:
            gender = self.employee_id.gender
            if gender == 'male':
                maternity_holiday_id = self.env.ref('smart_hr.data_hr_holiday_status_maternity').id
                adoption_holiday_id = self.env.ref('smart_hr.data_hr_holiday_status_adoption').id
                hildbirth_holiday_id = self.env.ref('smart_hr.data_hr_holiday_status_childbirth').id
                holiday_status_ids = [rec.id for rec in self.env['hr.holidays.status'].search([]) if rec.id not in [maternity_holiday_id, adoption_holiday_id, hildbirth_holiday_id]]
                res['domain'] = {'holiday_status_id': [('id', 'in', holiday_status_ids)]}
            if gender == 'female':
                child_birth_dad_holiday_id = self.env.ref('smart_hr.data_hr_holiday_child_birth_dad').id
                holiday_status_ids = [rec.id for rec in self.env['hr.holidays.status'].search([]) if rec.id not in [child_birth_dad_holiday_id]]
                res['domain'] = {'holiday_status_id': [('id', 'in', holiday_status_ids)]}
            for holiday in self:
                entitlement_type = holiday.entitlement_type if holiday.entitlement_type else False
                stock = self._get_current_holiday_stock(holiday.employee_id, holiday.holiday_status_id, entitlement_type)
                if stock['current_stock'] == 0 and stock['not_need_stock']:
                    current_stock = str("لا تحتاج رصيد")
                else:
                    current_stock = stock['current_stock']
                holiday.current_holiday_stock = current_stock
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
                            balance_line.period_id = open_period.id
#balance_line
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
                if stock_line:
                    
                    open_period.holiday_stock = stock_line.holidays_available_stock
                    stock_line.period_id = open_period.id
                else:
                    stock_line = self.env['hr.employee.holidays.stock'].create({'holidays_available_stock': open_period.holiday_stock,
                                                                                    'employee_id': self.employee_id.id,
                                                                                    'holiday_status_id': self.holiday_status_id.id,
                                                                                    'token_holidays_sum': 0,
                                                                                    'periode': right_entitlement.periode,
                                                                                    'entitlement_id':en.id,
                                                                                    })
                    open_period.active = True
                    stock_line.period_id = open_period.id
                    stock_line.holidays_available_stock = open_period.holiday_stock
                    stock_line.token_holidays_sum = 0

            open_period.holiday_stock -= self.duration
            stock_line.holidays_available_stock -= self.duration
            stock_line.token_holidays_sum += self.duration
            self.open_period = open_period.id
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
                self.token_compensation_stock = self.employee_id.compensation_stock
                self.employee_id.compensation_stock = 0
#                 مدة الترقية
        if self.holiday_status_id.promotion_deductible:
            self.employee_id.promotion_duration -= self.duration
        if self.holiday_status_id.deductible_duration_service:
            self.employee_id.service_duration -= self.duration

        if self.holiday_status_id == self.env.ref('smart_hr.data_hr_holiday_status_study'):
            self.env['courses.followup'].create({'employee_id':self.employee_id.id, 'state':'progress',
                                                 'holiday_id':self.id, 'name':self.study_subject,
                                                 })

        self.env['base.notification'].create({'title': u'إشعار بقبول إجازة',
                                              'message': u'لقد تم قبول الإجازة',
                                              'user_id': self.employee_id.user_id.id,
                                              'show_date': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                              'notif': True,
                                              'res_id': self.id,
                                             'res_action': 'smart_hr.action_hr_holidays_form'})
#         رصيد الغياب بعذر يجب ان تحسم من رصيد الإجازة العادية ولا يكون لها رصيد مستقل

        if self.holiday_status_id.id == self.env.ref('smart_hr.data_hr_holiday_status_legal_absent').id:
            holiday_status_id = self.env.ref('smart_hr.data_hr_holiday_status_normal')
            normal_stock_line = self.env['hr.employee.holidays.stock'].search([('employee_id', '=', self.employee_id.id),
                                                                         ('holiday_status_id', '=', holiday_status_id.id),
                                                                         ])
            normal_periodes = self.env['hr.holidays.periode'].search([('employee_id', '=', self.employee_id.id),
                                                                      ('holiday_status_id', '=', holiday_status_id.id),
                                                                      ('active', '=', True)])
            normal_open_period = False
            if normal_periodes:
                for periode in normal_periodes:
                    if fields.Datetime.from_string(periode.date_to) > fields.Datetime.from_string(self.date_to) and fields.Datetime.from_string(periode.date_from) < fields.Datetime.from_string(self.date_from):
                        normal_open_period = periode
                    else:
                        periode.normal_open_period = False
            if normal_stock_line:
                normal_stock_line.holidays_available_stock -= self.duration
                normal_stock_line.token_holidays_sum += self.duration
            if normal_open_period:
                normal_open_period.holiday_stock -= self.duration

        self.num_decision = self.env['ir.sequence'].get('hr.decision.sequence')
        self.date_decision = fields.Date.today()
        self.state = 'done'


    def compute_intersection_duration(self, date_from1, date_to1, date_from2, date_to2):
        duration = 0
        if not isinstance(date_from1, dt.date):
            date_from1 = fields.Date.from_string(date_from1)
        if not isinstance(date_to1, dt.date):
            date_to1 = fields.Date.from_string(date_to1)
        if not isinstance(date_from1, dt.date):
            date_from2 = fields.Date.from_string(date_from2)
        if not isinstance(date_to1, dt.date):
            date_to2 = fields.Date.from_string(date_to2)

        if date_from1 >= date_from2 and date_to2 >= date_from1:
            duration += self.compute_days_minus_weekends(date_from1, date_to2)
        if date_from2 >= date_from1 and date_to2 <= date_to1:
            duration += self.compute_days_minus_weekends(date_from2, date_to2)
        if date_from2 >= date_from1 and date_to2 >= date_to1:
            duration += self.compute_days_minus_weekends(date_from2, date_to1)
        return duration

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
                                                                   ('entitlement_id', '=', right_entitlement.id), ('active', '=', True),
                                                                   ('date_from', '=', first_day_date.strftime(DEFAULT_SERVER_DATE_FORMAT))])
            holiday_balance = self.env['hr.employee.holidays.stock'].search([('employee_id', '=', employee.id),
                                                                             ('holiday_status_id', '=', self.env.ref('smart_hr.data_hr_holiday_status_normal').id),
                                                                             ('entitlement_id.id', '=', right_entitlement.id), ])
            uncounted_days = 0
            employee_solde = right_entitlement.holiday_stock_default
            periode = right_entitlement.periode
            current_normal_holiday_stock = holiday_balance.holidays_available_stock
            today = date.today()
            d = today - relativedelta(days=1)

#                    مدّة الإجازة ة 

            holiday_uncounted_days = 0
            holiday_uncounted_days = self.search_count([('state', '=', 'done'), ('date_from', '<=', d), ('date_to', '>=', d), ('employee_id', '=', employee.id),
                                        ('holiday_status_id.deductible_normal_leave', '=', True)])
            uncounted_days += holiday_uncounted_days
#                    مدّة كف اليد todo

#                    مدّة الاعارة todo
            lend_obj = self.env['hr.employee.lend']
            lend_uncounted_days = lend_obj.search_count([('employee_id', '=', employee.id), ('state', '=', 'done'), ('date_from', '<=', d), ('date_to', '>=', d)])
            uncounted_days += lend_uncounted_days

            # مدّة غياب‬ ‫الموظف بدون‬ سند‬ ‫ن
            uncounted_absence_days = self.env['hr.attendance.report_day'].search_count([('employee_id', '=', employee.id), ('action', '=', 'absence'), ('date', '=', d)])
            uncounted_days += uncounted_absence_days

            # مدّةالتدريب
            candidate_obj = self.env['hr.candidates']
            formation_uncounted_days = candidate_obj.search_count([('employee_id', '=', employee.id), ('state', '=', 'done'), ('date_from', '<=', d), ('date_to', '>=', d)])
            uncounted_days += formation_uncounted_days

            # الابتعاث
            schol_obj = self.env['hr.scholarship']
            scholarship_uncounted_days = schol_obj.search_count([('employee_id', '=', employee.id), ('state', '=', 'done'), ('date_from', '<=', d), ('date_to', '>=', d)])
            uncounted_days += scholarship_uncounted_days

            init_solde = (employee_solde / (periode * 12)) / 30.0
            balance = init_solde - (uncounted_days * init_solde)

            holiday_balance.write({'holidays_available_stock': current_normal_holiday_stock + balance})
            open_periode.write({'holiday_stock': current_normal_holiday_stock + balance})

    @api.multi
    def button_extend(self):
        # check if its possible to extend this holiday
        if not self.is_extension:
            extensions_number = self.env['hr.holidays'].search_count([('extended_holiday_id', '=', self.id), ('extended_holiday_id', '!=', False), ('state', '=', 'done')])
            if extensions_number >= self.holiday_status_id.extension_number and self.holiday_status_id.extension_number > 0:
                raise ValidationError(u"لا يمكن تمديد هذا النوع من الاجازة أكثر من%s " % str(self.holiday_status_id.extension_number))
        else:
            original_holiday = self.extended_holiday_id
            extensions_number = 1
            while original_holiday.is_extension:
                extensions_number+=1
                original_holiday = original_holiday.extended_holiday_id
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
                'employee_id': self.employee_id.id,
                'holiday_id': self.id,
                'note': '   ',
            }
        holiday_cancellation_id = holidays_cancellation_obj.create(vals)
        # Add to log
        self.message_post(u"تم ارسال طلب إلغاء من قبل '" + unicode(user.name) + u"'")
        self.holiday_cancellation = holiday_cancellation_id.id

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
        # ا‬ن يكون تمتع بالحد الادنى منها
        if self.holiday_status_id == self.env.ref('smart_hr.data_hr_holiday_status_normal'):
            date_from = fields.Date.from_string(self.date_from)
            today_date = fields.Date.from_string(fields.Date.today())
            if (today_date - date_from).days < self.holiday_status_id.minimum:
                raise ValidationError(u"لا يمكن قطع اجازة قبل التمتع بالحد الادنى منها.")
            min_duration_cut_hoiday = self.holiday_status_id.min_duration_cut_hoiday
            taken_holidays = self.search([('state', '=', 'done'), ('employee_id', '=', self.employee_id.id),
                                          ('holiday_status_id', '=', self.holiday_status_id.id), ('date_from', '>=', date(today_date.year-2, 1, 1)),
                                          ('date_to', '<=', today_date)])
            duration_cut_hoiday = 0
            for hol in taken_holidays:
                duration_cut_hoiday += hol.duration
            if duration_cut_hoiday < min_duration_cut_hoiday:
                raise ValidationError(u"لا يمكن قطع اجازة موظف تمتع باجازة عادية خلال الثلاث سنوات الاخيرة مدتها اقل من"+str(min_duration_cut_hoiday)+"يوم")


# Create leave cancellation request
                
        vals = {
                'employee_id': self.employee_id.id,
                'holiday_id': self.id,
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
        
    @api.multi
    def _is_extended(self):
        # Check if the holiday have a pending or completed extension leave
        for rec in self:
            is_extended = False
            for ext in rec.extension_holidays_ids:
                if ext.state != 'refuse':
                    is_extended = True
                    break
            rec.is_extended = is_extended
        
    @api.multi
    def _is_cancelled(self):
        # Check if the holidays have a pending or completed holidays cancellation
        for rec in self:
            is_cancelled = False
            if rec.holiday_cancellation and rec.holiday_cancellation.state != 'refuse': 
                rec.is_cancelled = True

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

    def public_holiday_intersection(self, date):
        if not isinstance(date, dt.date):
            date = fields.Date.from_string(date)

        hr_public_holiday_obj = self.env['hr.public.holiday']
        inter = hr_public_holiday_obj.search([('state', '=', 'done'), ('date_from', '<=', date), ('date_to', '>=', date)], limit=1)
        if inter:
            date_from = fields.Date.from_string(inter.date_from)
            return (date - date_from).days


    def compute_prev_min_holidays(self, employee_id, holiday_status_id,date_from):
        date_from = fields.Date.from_string(self.date_from)
        prev_min_holidays = self.env['hr.holidays'].search([('state', '=', 'done'), ('employee_id', '=', employee_id.id), ('duration', '<', holiday_status_id.maximum_minimum),
                                                                   ('holiday_status_id', '=', holiday_status_id.id), ('date_from', '>=', date(date_from.year, 1, 1))])
        prev_min_holidays_duration = 0
        for holid in prev_min_holidays:
            prev_min_holidays_duration += holid.duration        
        return prev_min_holidays_duration

    @api.onchange('duration', 'date_from')
    def onchange_duration(self):
        warning = {}
#         maximum_minimum duration test
        prev_min_holidays_duration = self.compute_prev_min_holidays(self.employee_id, self.holiday_status_id, self.date_from)
        if self.duration > self.holiday_status_id.maximum_minimum and self.duration < self.holiday_status_id.minimum:
            raise ValidationError(u"ا كثر فترة يمكن طلبها  اقل من " + str(self.holiday_status_id.minimum) + u" ايام هي" + str(self.holiday_status_id.maximum_minimum) + u" أيام")
        elif self.duration < self.holiday_status_id.maximum_minimum:
            if prev_min_holidays_duration + self.duration > self.holiday_status_id.maximum_minimum and self.duration < self.holiday_status_id.minimum:
                raise ValidationError(u"ليس لديك الرصيد الكافي للتمتع ب‬اجازة مدتها اقل من‬ " + str(self.holiday_status_id.maximum_minimum) + u" أيام")
#         compute  duration and date_to
        date_to = fields.Date.from_string(self.date_from) + timedelta(days=self.duration - 1)
        if self.public_holiday_intersection(date_to):
            duration = self.duration - self.public_holiday_intersection(date_to)
            date_to = fields.Date.from_string(self.date_from) + timedelta(days=duration - 1)
            if date_to.weekday() == 4:
                duration -= 1
            elif date_to.weekday() == 5:
                duration -= 2
            if duration < self.holiday_status_id.maximum_minimum:
                if prev_min_holidays_duration + duration < self.holiday_status_id.maximum_minimum:
                    if duration >= 0:
                        self.duration = duration
                        self.date_to = fields.Date.from_string(self.date_from) + timedelta(days=self.duration - 1)
                    else:
                        self.duation = 0
                        self.date_to = fields.Date.from_string(self.date_from) + timedelta(days=self.duration - 1)
                else:
                    self.duration = self.holiday_status_id.minimum
                    self.date_to = fields.Date.from_string(self.date_from) + timedelta(days=self.duration - 1)
            else:
                if duration >= 0:
                    self.duration = duration
                    self.date_to = fields.Date.from_string(self.date_from) + timedelta(days=self.duration - 1)
                else:
                    self.duation = 0
                    self.date_to = fields.Date.from_string(self.date_from) + timedelta(days=self.duration - 1)
            warning = {
                    'title': _('تحذير!'),
                    'message': _('هناك تداخل في تاريخ الإنتهاء مع عطلة او عيد!'),
                }
        elif date_to.weekday() in [4,5] and self.duration:
            warning = {
                'title': _('تحذير!'),
                'message': _('هناك تداخل في تاريخ الإنتهاء مع عطلة نهاية الاسبوع!'),
            }
            if date_to.weekday() == 4:
                duration = self.duration - 1
            elif date_to.weekday() == 5:
                duration = self.duration - 2
            if duration < self.holiday_status_id.maximum_minimum:
                if prev_min_holidays_duration + duration < self.holiday_status_id.maximum_minimum:
                    if duration>=0:
                        self.duration = duration
                        self.date_to = fields.Date.from_string(self.date_from) + timedelta(days=self.duration - 1)
                    else:
                        self.duation = 0
                        self.date_to = fields.Date.from_string(self.date_from) + timedelta(days=self.duration - 1)
                else:
                    self.duration = self.holiday_status_id.minimum
                    self.date_to = fields.Date.from_string(self.date_from) + timedelta(days=self.duration - 1)
            else:
                if duration>=0:
                    self.duration = duration
                    self.date_to = fields.Date.from_string(self.date_from) + timedelta(days=self.duration - 1)
                else:
                    self.duation = 0
                    self.date_to = fields.Date.from_string(self.date_from) + timedelta(days=self.duration - 1)
        elif self.duration:
            self.date_to = date_to
        else:
            self.date_to = self.date_from
        if warning:
            return {'warning': warning}

    @api.multi
    def send_holiday_request(self):
        self.ensure_one()
        user = self.env['res.users'].browse(self._uid)
        self.check_constraintes()
            # check if the holiday status is supposed to be confirmed by direct manager
        if self.holiday_status_id.direct_director_decision:
            self.message_post(u"تم إرسال الطلب من قبل '" + unicode(user.name) + u"' إلى المدير المباشر")
            self.env['base.notification'].create({'title': u'إشعار بوجود طلب اجازة',
                                              'message': u"لقد تم تقديم  طلب اجازة من طرف الموظف" + unicode(self.employee_id.user_id.id),
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
        self.state = 'refuse'
        
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
            decision_appoint_id = self.env['hr.decision.appoint'].sudo().search([('employee_id.id', '=', self.employee_id.id), ('state_appoint', '=', 'active')], order='date_direct_action desc', limit=1)
            if decision_appoint_id:
                date_direct_action = fields.Date.from_string(decision_appoint_id.date_direct_action)
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

        if self.duration < self.holiday_status_id.minimum and self.holiday_status_id != self.env.ref('smart_hr.data_hr_holiday_status_normal'):
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
                if self.holiday_status_id.id != self.env.ref('smart_hr.data_hr_holiday_status_illness').id  and self.entitlement_type!=self.env.ref('smart_hr.data_entitlement_illness_normal').id:
                    raise ValidationError(u"هناك تداخل في التواريخ مع قرار سابق في الإنتداب")
                    
 
            """
 
            TODO: check dates with :أوقات خارج الدوام ... 
 
            """
        hr_public_holiday_obj = self.env['hr.public.holiday']
        if fields.Date.from_string(self.date_from).weekday() in [4, 5] and not self.is_extension:
            raise ValidationError(u"هناك تداخل في تاريخ البدء مع عطلة نهاية الاسبوع  ")
        if fields.Date.from_string(self.date_to).weekday() in [4, 5] and self.holiday_status_id != self.env.ref('smart_hr.data_hr_holiday_status_normal'):
            raise ValidationError(u"هناك تداخل في تاريخ الإنتهاء مع عطلة نهاية الاسبوع")
#         for public_holiday in hr_public_holiday_obj.search([('state', '=', 'done')]):
#             if not self.is_extension:
#                 if public_holiday.date_from <= self.date_from <= public_holiday.date_to or \
#                     public_holiday.date_from <= self.date_to <= public_holiday.date_to or \
#                     self.date_from <= public_holiday.date_from <= self.date_to or \
#                     self.date_from <= public_holiday.date_to <= self.date_to :
#                     raise ValidationError(u"هناك تداخل فى التواريخ مع اعياد و عطل رسمية")
                
#             # تكليف
#         if self.holiday_status_id != self.env.ref('smart_hr.data_hr_holiday_status_compelling'):
#             search_domain = [
#                 ('employee_id', '=', self.employee_id.id),
#                 ('overtime_id.state', '=', 'done'),
#                 ]
#             overtime_line_obj = self.env['hr.overtime.line']
# 
#             for rec in overtime_line_obj.search(search_domain):
#                 if rec.date_from <= self.date_from <= rec.date_to or \
#                         rec.date_from <= self.date_to <= rec.date_to or \
#                         self.date_from <= rec.date_from <= self.date_to or \
#                         self.date_from <= rec.date_to <= self.date_to:
#                     raise ValidationError(u"هناك تداخل في التواريخ مع قرار سابق في تكليف")
#

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
                ('state', 'not in', ['done', 'refuse', 'cancel', 'cutoff']),
                ('employee_id.id', '=', self.employee_id.id),
                ('holiday_status_id.id', '=', self.holiday_status_id.id),
                ('id', '!=', self.id)]
            if self.search_count(domain_search) > 0:
                raise ValidationError(u"لديك طلب قيد الإجراء من نفس هذا النوع من الإجازة.")

        # Constraintes for employee's nationnality
        if self.holiday_status_id.for_saudi and not self.holiday_status_id.for_other:
            # check the nationnality of the employee if it is saudi
            if self.employee_id.country_id and self.employee_id.country_id.code == 'SA':
                raise ValidationError(u"هذا النوع من الإجازة ينطبق فقط على السعوديين.")

        # Constraintes for studyinglevel
        if self.holiday_status_id.educ_lvl_req:
            # check education level
            level_fount = False
            for educ_level in self.employee_id.education_level_ids:
                if educ_level.level_education_id.id in self.holiday_status_id.education_levels.ids:
                    level_fount = True
                    break
            if not level_fount:
                raise ValidationError(u"لم تتحصل على المستوى الدراسي المطلوب.")
            
        # Constraintes for service years required
        if self.holiday_status_id.service_years_required * 364 > self.employee_id.service_duration:
                raise ValidationError(u" ليس لديك" + str(self.holiday_status_id.service_years_required) + u"سنوات خدمة  ")
            
         # Constraintes for evaluation_required
        if self.holiday_status_id.evaluation_condition:
            employee_evaluation_id = self.env['hr.employee.evaluation.level'].search([('employee_id', '=', self.employee_id.id), ('year', '=', date_from.year - 1)], limit=1)
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
        stock = self._get_current_holiday_stock(self.employee_id, self.holiday_status_id, self.entitlement_type)
        if stock['not_need_stock'] is False: 
            if stock['current_stock'] == 0 or stock['current_stock'] < self.duration:  
                raise ValidationError(u"ليس لديك الرصيد الكافي")
        
    @api.multi
    def write(self, vals):
        return super(HrHolidays, self).write(vals)

    @api.model
    def create(self, vals):
        res = super(HrHolidays, self).create(vals)
        res.check_constraintes()
        vals = {}
     
       # Sequence
        
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
    postponement_period = fields.Integer(string=u'(مدة التأجيل(يوم')
    extension_number = fields.Integer(string=u'عدد مرات التمديد', default=-1)
    deductible_normal_leave = fields.Boolean(string=u'تخصم مدتها من رصيد الاجازة العادية')
    deductible_duration_service = fields.Boolean(string=u'تخصم مدتها من فترة الخدمة')
    educ_lvl_req = fields.Boolean(string=u'يطبق شرط المستوى التعليمي')
    need_decision = fields.Boolean(string=u' تحتاج إلى قرار')
    direct_decision = fields.Boolean(string=u'تحتاج إلى قرار مباشرة')
    direct_director_decision = fields.Boolean(string=u'موافقة مدير مباشر', default=True)
    external_decision = fields.Boolean(string=u'موافقة خارجية', default=False)
    salary_spending = fields.Boolean(string=u'مدفوعة الأجر')
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
    spend_advanced_salary = fields.Boolean(string=u'يصرف له راتب مسبق')
    advanced_salary_periode = fields.Integer(string=u'مدة صرف راتب مسبق (باليوم)', default=30)
    maximum_minimum = fields.Integer(string=u'الحد الاقصى للايام الممكنة اقل من الحد الأدنى')
    min_duration_cut_hoiday = fields.Integer(string=u'المدة اللازمة لقطع الاجازة العادية خلال الثلاث سنوات الاخيرة') 
    can_be_cutted = fields.Boolean(string=u'يمكن قطعها', default=True)
    

            
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
    
    
    name = fields.Char(string=u'نوع الاستحقاق',)
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
    leave_type = fields.Many2one('hr.holidays.status', string=u'نوع الإجازة')
#     holiday_stock_open = fields.Boolean(string=u'الرصيد مفتوح')
    extension_period = fields.Integer(string=u'مدة تمديد الرصيد(سنة)', default=0)
    
    @api.multi
    def name_get(self):
        result = []
        for record in self:
            name = '[%s] %s' % (record.leave_type.name, record.entitlment_category.name)
            result.append((record.id, name))
        return result

class HrHolidaysStatusSalaryPercentage(models.Model):
    _name = 'hr.holidays.status.salary.percentage'
    _description = u'نسب الراتب المحتسبة'

    sequence = fields.Integer(string=u'الأولوية')
    month_from = fields.Integer(string=u'عدد الأشهر (من)')
    month_to = fields.Integer(string=u'عدد الأشهر (إلى)')
    salary_proportion = fields.Float(string=u'نسبة الراتب (%)', default=100) 
    holiday_status = fields.Many2one('hr.holidays.status', string='نوع الإجازة')
    entitlement_id = fields.Many2one('hr.holidays.status.entitlement', string=u'نوع الاستحقاق')


class EntitlementConfig(models.Model):
    _name = 'hr.holidays.entitlement.config'
    _description = u' اصناف الاستحقاقات'

    name = fields.Char(string=u'المسمّى')
    code = fields.Char(string='code')

