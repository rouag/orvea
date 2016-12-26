# -*- coding: utf-8 -*-

from openerp import fields, models, api, _
from openerp.tools import SUPERUSER_ID
from openerp.exceptions import ValidationError
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta

class HrHolidays(models.Model):
    _inherit = 'hr.holidays'
    _description = 'hr holidays Request'
    _order = 'id desc'

    name = fields.Char(string=u'رقم القرار', advanced_search=True)
    date = fields.Date(string=u'تاريخ الطلب', default=fields.Datetime.now())
    employee_id = fields.Many2one('hr.employee', string=u'الموظف', default=lambda self: self.env['hr.employee'].search([('user_id', '=', self._uid)], limit=1), advanced_search=True)
    raison = fields.Selection([
        ('other', u'سبب أخر'),
        ('husband', u'مرافقة الزوج'),
        ('wife', u'مرافقة الزوجة'),
         ('legit', u'مرافقة كمحرم شرعي'),
        ], default="other", string = u'السبب ')
    date_from = fields.Date(string=u'التاريخ من', default=fields.Datetime.now())
    date_to = fields.Date(string=u'التاريخ الى', default=fields.Datetime.now())
    duration = fields.Integer(string=u'الأيام', compute='_compute_duration')
    holiday_status_id = fields.Many2one('hr.holidays.status', string=u'نوع الأجازة', default=lambda self: self.env.ref('smart_hr.data_hr_holiday_status_normal'), advanced_search=True)
    state = fields.Selection(selection_add=[
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
        ('cutoff', u'مقطوعة')], string=u'حالة', default='draft', advanced_search=True)
    is_current_user = fields.Boolean(string='Is Current User', compute='_is_current_user')
    is_direct_manager = fields.Boolean(string='Is Direct Manager', compute='_is_direct_manager')
    num_outspeech = fields.Char(string=u'رقم الخطاب الصادر')
    date_outspeech = fields.Date(string=u'تاريخ الخطاب الصادر')
    num_inspeech = fields.Char(string=u'رقم الخطاب الوارد')
    date_inspeech = fields.Date(string=u'تاريخ الخطاب الوارد')
    holidays_available_stock = fields.Float(string=u'رصيد الاجازة', compute='_compute_holiday_status_available_stock')
    is_started = fields.Boolean(string=u'بدأت', compute='_compute_is_started', store = True)
    holiday_cancellation = fields.Many2one('hr.holidays.cancellation')
    
    @api.depends('date_from')
    def _compute_is_started(self):
        for rec in self:
            if rec.date_from <= datetime.today().strftime('%Y-%m-%d') and rec.state == 'done':
                rec.is_started = True
                print rec.is_started
                    
    @api.depends('holiday_status_id')
    def _compute_holiday_status_available_stock(self):
        for holiday in self:
            # check if there is entitlements in holiday_status_id
            if not holiday.holiday_status_id.entitlements and holiday.holiday_status_id.limit:
                raise ValidationError(u"يجب التحقق من الإستحقاقات في إعدادات نوع الإجازة.")
            else:
                # loop under entitlements and get the holiday solde depend on grade of the employee
                holiday_solde_by_year_number = {}
                for en in holiday.holiday_status_id.entitlements:
                    if holiday.employee_id.job_id.grade_id in en.entitlment_category.grades:
                        holiday_solde_by_year_number = {en.periode : en.holiday_stock_default}
                        break
            
            # Sum of given holidays depend on holiday_status entitlement's periode
            if holiday_solde_by_year_number.items():
                periode = holiday_solde_by_year_number.items()[0][0]
                # One year
                if periode == 1:
                    given_holiday_scount = 0
                    for rec in holiday.search([('state', '=', 'done'), ('employee_id.id', '=', holiday.employee_id.id), ('holiday_status_id.id', '=', holiday.holiday_status_id.id), ('date_from', '<=', date(date.today().year, 12, 31)), ('date_from', '>=', date(date.today().year, 1, 1))]):
                        given_holiday_scount += rec.duration 
                    holiday.holidays_available_stock = holiday_solde_by_year_number[1] - given_holiday_scount
        

                    
    @api.model
    def _check_state_access_right(self, vals):
        # override this method to be always returning true to avoid checking state access right
        return True
    
    
    @api.depends('employee_id')
    def _is_current_user(self):
        for rec in self:
            if rec.employee_id.user_id.id == rec._uid:
                rec.is_current_user = True
    @api.depends('employee_id')
    def _is_direct_manager(self):
        for rec in self:
            # System Admin Bypass
            if self.env['res.users'].browse(rec._uid).has_group('smart_hr.group_sys_manager'):
                rec.is_direct_manager = True
            elif rec.employee_id.user_id.id != rec._uid and rec.state == 'dm':
                depth = rec._get_dm_depth(rec._uid, rec.employee_id)
                if rec.state_dm == depth:
                    rec.is_direct_manager = True



    @api.depends('date_from', 'date_to')
    def _compute_duration(self):
        for holiday in self:
            if holiday.date_from and holiday.date_to:
                start_date = fields.Date.from_string(holiday.date_from)
                end_date = fields.Date.from_string(holiday.date_to)
                duration = (end_date - start_date).days + 1
                holiday.duration = duration
    @api.one
    def send_holiday_request(self):
        user = self.env['res.users'].browse(self._uid)
        for holiday in self:
            # check if the holiday status is supposed to be confirmed by direct manager
            if holiday.holiday_status_id.direct_director_decision:
                holiday.message_post(u"تم إرسال الطلب من قبل '" + unicode(user.name) + u"' إلى المدير المباشر")
                holiday.state = 'dm'
            else:
                holiday.message_post(u"تم إرسال الطلب من قبل '" + unicode(user.name) + u"' إلى مرحلة التدقيق")
                holiday.state = 'audit'
                
    @api.one
    def button_accept_dm(self):
        self.state = 'audit'
    
    @api.multi
    def action_delay_holiday(self):
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
        
    @api.one
    def button_delay_dm(self):
        self.state = 'draft'
        
    @api.one
    def button_accept_audit(self):
        if self.holiday_status_id.employees_director_decision:
            self.state = 'hrm'
    
    @api.one
    def button_refuse_audit(self):
        if self.holiday_status_id.direct_director_decision:
            self.state = 'dm'
        else:
            self.state = 'draft'
    @api.one
    def button_accept_hrm(self):
        if not self.holiday_status_id.external_decision:
            self.state = 'done'
        # need an external decision
        if self.holiday_status_id.external_decision and self.employee_id.external_decision:
            self.state = 'external_audit'
            
    @api.one
    def button_delay_hrm(self):
        self.state = 'dm'
        
    @api.one
    def button_accept_external_audit(self):
        if self.holiday_status_id.external_decision:
            self.state = 'revision'
            
    @api.one
    def button_refuse_external_audit(self):
        self.state = 'audit'
    
    @api.one
    def button_accept_revision(self):
        self.state = 'revision_response'
            
    @api.one
    def button_refuse_revision(self):
        self.state = 'external_audit'
    
    @api.one
    def button_accept_revision_response(self):
        self.state = 'done'
    @api.one
    def button_refuse_revision_response(self):
        self.state = 'refuse'
    
    
    @api.constrains('date_from', 'date_to')
    def check_dates_periode(self):
        # Objects
        holiday_obj = self.env['hr.holidays']
        train_obj = self.env['hr.training']
        deput_obj = self.env['hr.deputation']
        

        for holiday in self:
            # check demanded periode with solde for holidays that have limit solde
            if holiday.duration > holiday.holidays_available_stock and holiday.holiday_status_id.limit:
                raise ValidationError(u"ليس لديك الرصيد الكافي.")
            
            # Date validation
            if holiday.date_from > holiday.date_to:
                raise ValidationError(u"تاريخ من يجب ان يكون أصغر من تاريخ الى")
            # check minimum request validation
            if holiday.holiday_status_id.minimum != 0 and holiday.duration < holiday.holiday_status_id.minimum:
                raise ValidationError(u"أقل فترة يمكن طلبها من نوع إجازة " + holiday.holiday_status_id.name + u" " + str(holiday.holiday_status_id.minimum) + u" أيام")
            
            # check maximum request validation
            if holiday.holiday_status_id.maximum != 0 and holiday.duration > holiday.holiday_status_id.maximum:
                raise ValidationError(u"أكثر فترة يمكن طلبها من نوع إجازة " + holiday.holiday_status_id.name + u" " + str(holiday.holiday_status_id.maximum) + u" أيام")
   
            # Date overlap
            # الإجازات
            search_domain = [
                ('employee_id', '=', holiday.employee_id.id),
                ('id', '!=', holiday.id),
                ('state', 'not in', ['refuse', 'cancel']),
            ]
            for rec in holiday_obj.search(search_domain):
                if rec.date_from <= holiday.date_from <= rec.date_to or \
                        rec.date_from <= holiday.date_to <= rec.date_to or \
                        holiday.date_from <= rec.date_from <= holiday.date_to or \
                        holiday.date_from <= rec.date_to <= holiday.date_to:
                    raise ValidationError(u"هناك تداخل في التواريخ مع قرار سابق فى الإجازات")
            # التدريب
            search_domain = [
                ('employee_ids', 'in', [holiday.employee_id.id]),
                ('state', '!=', 'refuse'),
            ]
            for rec in train_obj.search(search_domain):
                if rec.effective_date_from <= holiday.date_from <= rec.effective_date_to or \
                        rec.effective_date_from <= holiday.date_to <= rec.effective_date_to or \
                        holiday.date_from <= rec.effective_date_from <= holiday.date_to or \
                        holiday.date_from <= rec.effective_date_to <= holiday.date_to:
                    raise ValidationError(u"هناك تداخل في التواريخ مع قرار سابق في التدريب")
            
            # الإنتتبات
            search_domain = [
                ('employee_id', '=', holiday.employee_id.id),
                ('state', '!=', 'refuse'),
            ]
            for rec in deput_obj.search(search_domain):
                if rec.date_from <= holiday.date_from <= rec.date_to or \
                        rec.date_from <= holiday.date_to <= rec.date_to or \
                        holiday.date_from <= rec.date_from <= holiday.date_to or \
                        holiday.date_from <= rec.date_to <= holiday.date_to:
                    raise ValidationError(u"هناك تداخل في التواريخ مع قرار سابق في الإنتداب")
            
            """
            
            TO DO: check dates with :أوقات خارج الدوام ... 
            
            """
            
    def check_constraintes(self):
        """
        check constraintes beside date and periode ones
        """
        
        # common constraintes
        if self.holiday_status_id in [self.env.ref('smart_hr.data_hr_holiday_status_normal'), self.env.ref('smart_hr.data_hr_holiday_status_exceptional'), self.env.ref('smart_hr.data_hr_holiday_status_compelling')]:
            # check if there is another undone request for the same status of holiday
            domain_search = [
                                ('state', 'not in', ['done', 'refuse']),
                                ('employee_id.id', '=', self.employee_id.id),
                                ('holiday_status_id.id', '=', self.holiday_status_id.id),
                                ('id', '!=', self.id)
                            ]
            if self.search_count(domain_search) > 0:
                raise ValidationError(u"لديك طلب قيد الإجراء من نفس هذا النوع من الإجازة.")
        
        # Constraintes for normal holidays عادية
        if self.holiday_status_id == self.env.ref('smart_hr.data_hr_holiday_status_normal'):
            # check the nationnality of the employee if it is saudi 
            if self.employee_id.country_id != self.env.ref('base.sa'):
                raise ValidationError(u"هذا النوع من الإجازة ينطبق فقط على السعوديين.")

            
        # Constraintes for studying holidays دراسية
        if self.holiday_status_id == self.env.ref('smart_hr.data_hr_holiday_status_study'):
            # check education level
            if self.employee_id.education_level.sequence < self.env.ref('smart_hr.certificate_secondary_education').sequence:
                raise ValidationError(u"لم تتحصل على المستوى الدراسي المطلوب.")
            # check 3 years of services
            date_hiring = self.env['hr.decision.appoint'].search([('employee_id.id', '=', self.employee_id.id)], limit=1).date_hiring
            res = relativedelta(fields.Date.from_string(fields.Datetime.now()), fields.Date.from_string(date_hiring))
            if res.years < 3:
                raise ValidationError(u"ليس لديك ثلاث سنوات خدمة.")
         
        # Constraintes for Compelling holidays اضطرارية
        if self.holiday_status_id == self.env.ref('smart_hr.data_hr_holiday_status_compelling'):
            print 'اضطرارية'
           
        # Constraintes for exceptionnal holidays استثنائية
        if self.holiday_status_id == self.env.ref('smart_hr.data_hr_holiday_status_exceptional'):
            # check raison
            print 'استثنائية'
            
            
        
        return True
    
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
    deductible_normal_leave = fields.Boolean(string=u'تخصم مدتها من رصيد الاجازة العادية')
    deductible_duration_service = fields.Boolean(string=u'تخصم مدتها من فترة الخدمة')
    educ_lvl_req = fields.Boolean(string=u'يطبق شرط المستوى التعليمي')
    direct_decision = fields.Boolean(string=u'تحتاج إلى قرار مباشر')
    direct_director_decision = fields.Boolean(string=u'موافقة مدير مباشر', default=True)
    external_decision = fields.Boolean(string=u'موافقة خارجية', default=False)
    salary_spending = fields.Boolean(string=u'يجوز صرف راتبها')
    employees_director_decision = fields.Boolean(string=u'موافقة مدير شؤون الموظفين', default=True)
    can_be_cancelled = fields.Boolean(string=u'يمكن الغاؤها')
    evaluation_condition = fields.Boolean(string=u'يطبق شرط تقويم الأداء')
    education_levels = fields.One2many('hr.employee.education.level', 'leave_type', string=u'المستويات التعليمية')
    entitlements = fields.One2many('hr.holidays.status.entitlement', 'leave_type', string=u'أنواع الاستحقاقات')
    assessments_required = fields.One2many('hr.assessment.result.config', 'leave_type', string=u'التقييمات المطلوبة')
    percentages = fields.One2many('hr.holidays.status.salary.percentage', 'holiday_status', string=u'نسب الراتب المحتسبة')
    
                
                
class HrHolidaysStatusEntitlement(models.Model):
    _name = 'hr.holidays.status.entitlement'
    _description = u'أنواع الاستحقاقات'
    entitlment_category = fields.Many2one('hr.holidays.status.entitlement.category', string=u'فئة الاستحقاق')
    holiday_stock_default = fields.Integer(string=u'الرصيد')
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
        ], string=u'المدة', default=1)
    leave_type = fields.Many2one('hr.holidays.status', string='leave type')
#     holiday_stock_open = fields.Boolean(string=u'الرصيد مفتوح')
    
    
class HrHolidaysStatusEntitlementCategory(models.Model):
    _name = 'hr.holidays.status.entitlement.category'
    _description = u'فئة استحقاق'
    
    name = fields.Char(string=u'الاسم')
    grades = fields.Many2many('salary.grid.grade', string=u'المراتب')
    
class HrHolidaysStatusSalaryPercentage(models.Model):
    _name = 'hr.holidays.status.salary.percentage'
    _description = u'نسب الراتب المحتسبة'
    
    sequence = fields.Integer(string=u'الأولوية')
    periode = fields.Integer(string=u'عدد الأشهر')
    salary_proportion = fields.Float(string=u'نسبة الراتب (%)', default=100) 
    holiday_status = fields.Many2one('hr.holidays.status', string='holiday status')
