# -*- coding: utf-8 -*-

from openerp import fields, models, api, _
from openerp.tools import SUPERUSER_ID
from openerp.exceptions import ValidationError
from datetime import date, datetime, timedelta
from antlr import ifelse

class HrHolidays(models.Model):
    _inherit = 'hr.holidays'
    _description = 'hr holidays Request'
    _order = 'id desc'

    name = fields.Char(string=u'رقم القرار', advanced_search=True)
    date = fields.Date(string=u'تاريخ الطلب', default=fields.Datetime.now())
    employee_id = fields.Many2one('hr.employee', string=u'الموظف', default=lambda self: self.env['hr.employee'].search([('user_id', '=', self._uid)], limit=1), advanced_search=True)
    date_from = fields.Date(string=u'التاريخ من', default=fields.Datetime.now())
    date_to = fields.Date(string=u'التاريخ الى', default=fields.Datetime.now())
    duration = fields.Integer(string=u'الأيام', compute='_compute_duration')
    holiday_status_id = fields.Many2one('hr.holidays.status', string=u'نوع الأجازة', default=lambda self: self.env.ref('smart_hr.data_hr_leave_type_01'), advanced_search=True)
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
        ('cancel', u'ملغاة')], string=u'حالة', default='draft', advanced_search=True)
    is_current_user = fields.Boolean(string='Is Current User', compute='_is_current_user')
    is_direct_manager = fields.Boolean(string='Is Direct Manager', compute='_is_direct_manager')
    num_outspeech = fields.Char(string=u'رقم الخطاب الصادر')
    date_outspeech = fields.Date(string=u'تاريخ الخطاب الصادر')
    num_inspeech = fields.Char(string=u'رقم الخطاب الوارد')
    date_inspeech = fields.Date(string=u'تاريخ الخطاب الوارد')
    
    @api.model
    def create(self, vals):
        res = super(HrHolidays, self).create(vals)
        # Sequence
        vals = {}
        vals['state'] = 'draft'
        vals['name'] = self.env['ir.sequence'].get('hr.holidays.seq')
        res.write(vals)
        return res
    
    @api.model
    def _check_state_access_right(self, vals):
        # override this method to be always returning true to avoid check state access right
        return True
    
    
    @api.depends('employee_id')
    def _is_current_user(self):
        for rec in self:
            # System Admin Bypass
            if self.env['res.users'].browse(rec._uid).has_group('smart_hr.group_sys_manager'):
                rec.is_current_user = True
            elif rec.employee_id.user_id.id == rec._uid:
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
        for lv in self:
            if lv.date_from and lv.date_to:
                start_date = fields.Date.from_string(lv.date_from)
                end_date = fields.Date.from_string(lv.date_to)
                duration = (end_date - start_date).days + 1
                lv.duration = duration
    @api.one
    def send_holiday_request(self):
        user = self.env['res.users'].browse(self._uid)
        for lv in self:
            # check if the holiday status is supposed to be confirmed by direct manager
            if lv.holiday_status_id.direct_director_decision:
                lv.message_post(u"تم إرسال الطلب من قبل '" + unicode(user.name) + u"' إلى المدير المباشر")
                lv.state = 'dm'
            else:
                lv.message_post(u"تم إرسال الطلب من قبل '" + unicode(user.name) + u"' إلى مرحلة التدقيق")
                lv.state = 'audit'
                
    @api.one
    def button_accept_dm(self):
        self.state = 'audit'
    @api.one
    def button_refuse_dm(self):
        self.state = 'refuse'
        
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
        if self.holiday_status_id.external_decision:
            self.state = 'external_audit'
            
    @api.one
    def button_refuse_hrm(self):
        self.state = 'audit'
        
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
        eid_obj = self.env['hr.eid']
        for lv in self:
            # Date validation
            if lv.date_from > lv.date_to:
                raise ValidationError(u"تاريخ من يجب ان يكون أصغر من تاريخ الى")
            # check minimum request validation
            if lv.holiday_status_id.minimum != 0 and lv.duration < lv.holiday_status_id.minimum:
                raise ValidationError(u"أقل فترة يمكن طلبها من نوع إجازة " + lv.holiday_status_id.name + u" " + str(lv.holiday_status_id.minimum) + u" أيام")
   
            # Date overlap
            # Leaves
            domain_search = [
                ('employee_id', '=', lv.employee_id.id),
                ('id', '!=', lv.id),
                ('state', 'not in', ['refuse', 'cancel']),
            ]
            for rec in holiday_obj.search(domain_search):
                if rec.date_from <= lv.date_from <= rec.date_to or \
                        rec.date_from <= lv.date_to <= rec.date_to or \
                        lv.date_from <= rec.date_from <= lv.date_to or \
                        lv.date_from <= rec.date_to <= lv.date_to:
                    raise ValidationError(u"هناك تداخل في التواريخ مع قرار سابق فى الإجازات")
            # Check for eid
            for eid in eid_obj.search([]):
                if eid.date_from <= lv.date_from <= eid.date_to or \
                        eid.date_from <= lv.date_to <= eid.date_to or \
                        lv.date_from <= eid.date_from <= lv.date_to or \
                        lv.date_from <= eid.date_to <= lv.date_to:
                    raise ValidationError(u"هناك تداخل في التواريخ مع اعياد و مناسبات رسمية")
           
            # Training
            search_domain = [
                ('employee_ids', 'in', [lv.employee_id.id]),
                ('state', '!=', 'refuse'),
            ]
            for rec in train_obj.search(search_domain):
                if rec.effective_date_from <= lv.date_from <= rec.effective_date_to or \
                        rec.effective_date_from <= lv.date_to <= rec.effective_date_to or \
                        lv.date_from <= rec.effective_date_from <= lv.date_to or \
                        lv.date_from <= rec.effective_date_to <= lv.date_to:
                    raise ValidationError(u"هناك تداخل في التواريخ مع قرار سابق في التدريب")
            """
            
            TO DO: check dates with :مع الإنتتبات، وأوقات خارج الدوام ... 
            
            """
            
            
class HrHolidaysStatus(models.Model):
    _name = 'hr.holidays.status'
    _inherit = 'hr.holidays.status'
    _description = 'holidays status'

    name = fields.Char(string=u'نوع الاجازة')
    minimum = fields.Integer(string=u'الحد الأدنى')
    maximum = fields.Integer(string=u'الحد الأقصى')
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
    leave_stock_default = fields.Integer(string=u'الرصيد')
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
#     leave_stock_open = fields.Boolean(string=u'الرصيد مفتوح')
    
    
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
