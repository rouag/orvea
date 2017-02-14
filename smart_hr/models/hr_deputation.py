# -*- coding: utf-8 -*-
####################################
### This Module Created by smart-etech ###
####################################

from openerp import fields, models, api, _
from openerp.tools import SUPERUSER_ID
from openerp.exceptions import ValidationError
from lxml import etree
from datetime import datetime
from umalqurra.hijri_date import HijriDate


class hr_deputation(models.Model):
    _name = 'hr.deputation'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = 'Deputation'

    name = fields.Char(string=u'رقم القرار', advanced_search=True)
    date = fields.Date(string=u'التاريخ', default=fields.Datetime.now())
    employee_id = fields.Many2one('hr.employee', string=u'الموظف', default=lambda self: self.env['hr.employee'].search([('user_id', '=', self._uid)], limit=1), advanced_search=True)
    employee_state = fields.Selection([('new', u'جديد'),
                                       ('waiting', u'في إنتظار الموافقة'),
                                       ('update', u'إستكمال البيانات'),
                                       ('done', u'اعتمدت'),
                                       ('refused', u'رفض'),
                                       ('employee', u'موظف')], string=u'الحالة', related='employee_id.employee_state')
    is_direct_manager = fields.Boolean(string='Is Direct Manager', compute='_is_direct_manager')
    is_current_user = fields.Boolean(string='Is Current User', compute='_is_current_user')
    date_from = fields.Date(string=u'من')
    date_to = fields.Date(string=u'الى')
    duration = fields.Integer(string=u'المدة', compute='_compute_duration')
    deputation_stock = fields.Integer(string=u'الرصيد المتاح', related='employee_id.deputation_stock')
    deputation_transport = fields.Boolean(string=u'توفير بدل النقل', advanced_search=True)
    deputation_support = fields.Selection([
        ('none', u'لا شيئ'),
        ('residence', u'السكن'),
        ('residence_living', u'السكن و المعيشة'),
    ], string=u'توفر جهة العمل', default='none', advanced_search=True)
    deputation_type = fields.Selection([
        ('internal', u'داخلى'),
        ('external', u'خارجى'),
    ], string=u'نوع الأنتداب', default='internal', advanced_search=True)
    city_id = fields.Many2one('res.city', string=u'المدينة')
    deputation_category_id = fields.Many2one('hr.deputation.category', string=u'فئة الصنف')
    task_description = fields.Text(string=u'وصف المهمة')
    period_line_ids = fields.One2many('hr.period.line', 'deputation_id', string=u'الفترة')
    is_same_employee = fields.Boolean(string=u'نفس الموظف', compute='_compute_is_same_employee')
    is_finished = fields.Boolean(string='Current Date', compute='_compute_is_finished')
    state = fields.Selection([
        ('draft', u'طلب'),
        ('dm', u'المدير المباشر'),
        ('hrm', u'مدير شؤون الموظفين'),
        ('done', u'اعتمدت'),
        ('refuse', u'رفض'),
    ], string=u'حالة', default='draft', advanced_search=True)

    @api.model
    def create(self, vals):
        ret = super(hr_deputation, self).create(vals)
        # Sequence
        vals = {}
        vals['name'] = self.env['ir.sequence'].get('hr.deputation.seq')
        ret.write(vals)
        # Create Period Lines
        self._create_related_periods(ret)
        return ret

    @api.multi
    def write(self, vals):
        ret = super(hr_deputation, self).write(vals)
        # Create/Update Period Lines
        if vals.get('date_from') or vals.get('date_to'):
            for rec in self:
                self._create_related_periods(rec)
        return ret

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state != 'draft' and self._uid != SUPERUSER_ID:
                raise ValidationError(u'لا يمكن حذف الأنتداب فى هذه المرحلة يرجى مراجعة مدير النظام')
        return super(hr_deputation, self).unlink()

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        # Objects
        user_obj = self.env['res.users']
        employee_obj = self.env['hr.employee']
        # Variables
        uid = self._uid
        user = user_obj.browse(uid)
        emp_ids = employee_obj.search(['|', ('parent_id.user_id', 'child_of', uid), ('user_id', '=', uid)])
        #
        res = super(hr_deputation, self).fields_view_get(view_id=view_id, view_type=view_type,  toolbar=toolbar, submenu=submenu)
        if view_type == 'form':
            # Make fields readonly for all employees except admin
            arch = etree.XML(res['arch'])
            # Get current user group
            is_admin = user.has_group('smart_hr.group_sys_manager')
            is_hr = user.has_group('smart_hr.group_hr')
            is_hr_payroll = user.has_group('smart_hr.group_hr_payroll')
            is_ade = user.has_group('smart_hr.group_ade')
            is_followup = user.has_group('smart_hr.group_followup')
            if not (is_admin or is_hr or is_hr_payroll or is_ade or is_followup):
                # Fields
                employee_id = arch.xpath("//field[@name='employee_id']")[0]
                # Updated attributes
                employee_id.set('domain', "['|',('id','in',%s),('user_id','=',%s)]" % (emp_ids.ids, uid))
            res['arch'] = etree.tostring(arch, encoding="utf-8")
        return res

    def _create_related_periods(self, record):
        # Objects
        period_obj = self.env['hr.period.line']
        # Delete old records
        period_obj.search([('deputation_id', '=', record.id)]).unlink()
        # Create new records
        period_id = period_obj.create({
            'date_from': record.date_from,
            'date_to': record.date_to,
            'deputation_id': record.id,
            'state': 'deputation',
        })
        record.period_line_ids = period_id

    @api.constrains('date_from', 'date_to')
    def check_dates(self):
        for dep in self:
            # Objects
#             leave_obj = self.env['hr.leave']
            dep_obj = self.env['hr.deputation']
            train_obj = self.env['hr.training']
            overtime_obj = self.env['hr.overtime']
#             eid_obj = self.env['hr.eid']
            # Check for incomplete data
            if dep.date_from > dep.date_to:
                raise ValidationError(u'تاريخ بداية الدورة يجب ان يكون أصغر من تاريخ انتهاء الدورة')
            # Check for eid
#             for eid in eid_obj.search([]):
#                 if eid.date_from <= dep.date_from <= eid.date_to or \
#                         eid.date_from <= dep.date_to <= eid.date_to or \
#                         dep.date_from <= eid.date_from <= dep.date_to or \
#                         dep.date_from <= eid.date_to <= dep.date_to:
#                     raise ValidationError(u"هناك تداخل فى التواريخ مع اعياد و مناسبات رسمية")
            # Check for any intersection with other decisions
#             for emp in dep.employee_id:
#                 # Leave
#                 search_domain = [
#                     ('employee_id', '=', emp.id),
#                     ('state', '!=', 'refuse'),
#                 ]
# #                 for rec in leave_obj.search(search_domain):
# #                     if rec.date_from <= dep.date_from <= rec.date_to or \
# #                             rec.date_from <= dep.date_to <= rec.date_to or \
# #                             dep.date_from <= rec.date_from <= dep.date_to or \
# #                             dep.date_from <= rec.date_to <= dep.date_to:
# #                         raise ValidationError(u"هناك تداخل فى التواريخ مع قرار سابق فى الاجازات")
#                 # Overtime
#                 search_domain = [
#                     ('overtime_line_ids.employee_id', '=', emp.id),
#                     ('state', '!=', 'refuse'),
#                 ]
#                 for rec in overtime_obj.search(search_domain):
#                     for line in rec.overtime_line_ids:
#                         if (line.date_from <= dep.date_from <= line.date_to or \
#                                 line.date_from <= dep.date_to <= line.date_to or \
#                                 dep.date_from <= line.date_from <= dep.date_to or \
#                                 dep.date_from <= line.date_to <= dep.date_to) and \
#                                 line.employee_id == emp:
#                             raise ValidationError(u"هناك تداخل فى التواريخ مع قرار سابق فى خارج الدوام")
#             # Training
#             search_domain = [
#                 ('employee_ids', 'in', [dep.employee_id.id]),
#                 ('state', '!=', 'refuse'),
#             ]
#             for rec in train_obj.search(search_domain):
#                 if rec.effective_date_from <= dep.date_from <= rec.effective_date_to or \
#                         rec.effective_date_from <= dep.date_to <= rec.effective_date_to or \
#                         dep.date_from <= rec.effective_date_from <= dep.date_to or \
#                         dep.date_from <= rec.effective_date_to <= dep.date_to:
#                     raise ValidationError(u"هناك تداخل فى التواريخ مع قرار سابق فى التدريب")
#             # Deputation
#             search_domain = [
#                 ('employee_id', '=', dep.employee_id.id),
#                 ('id', '!=', dep.id),
#                 ('state', '!=', 'refuse'),
#             ]
#             for rec in dep_obj.search(search_domain):
#                 if rec.date_from <= dep.date_from <= rec.date_to or \
#                         rec.date_from <= dep.date_to <= rec.date_to or \
#                         dep.date_from <= rec.date_from <= dep.date_to or \
#                         dep.date_from <= rec.date_to <= dep.date_to:
#                     raise ValidationError(u"هناك تداخل فى التواريخ مع قرار سابق فى الأنتداب")

    @api.depends('date_from', 'date_to')
    def _compute_duration(self):
        for rec in self:
            if rec.date_from and rec.date_to:
                start_date = fields.Date.from_string(rec.date_from)
                end_date = fields.Date.from_string(rec.date_to)
                duration = (end_date - start_date).days + 1
                rec.duration = duration

    @api.depends('employee_id')
    def _is_direct_manager(self):
        for rec in self:
            if self.env['res.users'].browse(rec._uid).has_group('smart_hr.group_sys_manager'):
                rec.is_direct_manager = True
            elif rec.employee_id.user_id.id != rec._uid:
                if rec.employee_id.parent_id.user_id.id == rec._uid:
                    rec.is_direct_manager = True

    @api.depends('employee_id')
    def _is_current_user(self):
        for rec in self:
            if self.env['res.users'].browse(rec._uid).has_group('smart_hr.group_sys_manager'):
                rec.is_current_user = True
            elif rec.employee_id.user_id.id == rec._uid:
                rec.is_current_user = True

    @api.depends('employee_id')
    def _compute_is_same_employee(self):
        for rec in self:
            # get current employee
            # Objects
            employee_obj = self.env['hr.employee']
            # Variables
            current_employee_id = employee_obj.search([('user_id', '=', self._uid)], limit=1)
            if current_employee_id == rec.employee_id:
                rec.is_same_employee = True

    @api.depends('date_to')
    def _compute_is_finished(self):
        for rec in self:
            if rec.date_to <= datetime.today().strftime('%Y-%m-%d'):
                rec.is_finished = True

    @api.one
    def button_dm(self):
        user = self.env['res.users'].browse(self._uid)
        for dep in self:
            dep.state = 'dm'
            dep.message_post(u"تم إرسال الطلب من قبل '" + unicode(user.name) + u"'")

    @api.one
    def button_hrm(self):
        user = self.env['res.users'].browse(self._uid)
        for dep in self:
            dep.state = 'hrm'
            dep.message_post(u"تم الموافقة من قبل '" + unicode(user.name) + u"'")

    @api.one
    def button_done(self):
        user = self.env['res.users'].browse(self._uid)
        for dep in self:
            # Update Employee Deputation Stock
            dep.employee_id.deputation_stock -= dep.duration
            dep.state = 'done'
            dep.message_post(u"تم الإعتماد من قبل '" + unicode(user.name) + u"'")
            dep.create_report_attachment()

    @api.one
    def button_refuse(self):
        for dep in self:
            dep.state = 'refuse'

    @api.model
    def _needaction_domain_get(self):
        return [
            ('state', 'in', ['dm', 'hrm']),
        ]

    """
        Scheduler function
    """
    @api.model
    def update_deputation_stock(self):
        # Objects
        employee_obj = self.env['hr.employee']
        # Check first day of new hijri month
        today_date = fields.Date.from_string(fields.Date.today())
        hijri_date = HijriDate(today_date.year, today_date.month, today_date.day, gr=True)
        if int(hijri_date.day) == 1 and int(hijri_date.month) == 1:
            # Loop all employees
            for emp in employee_obj.search([]):
                # Update Deputation Stock
                emp.deputation_stock = 60

    '''
        Report Functions
    '''
    def num2hindi(self,string_number):
        if string_number:
            hindi_numbers = {'0':'٠','1':'١','2':'٢','3':'٣','4':'٤','5':'٥','6':'٦','7':'٧','8':'٨','9':'٩','.':','}
            if isinstance(string_number, unicode):
                hindi_string = string_number.encode('utf-8','replace')
            else:
                hindi_string = str(string_number)
            for number in hindi_numbers:
                hindi_string = hindi_string.replace(str(number),hindi_numbers[number])
            return hindi_string
        
    def get_ummqura(self, g_date):
        try:
            g_date = fields.Date.from_string(g_date)
            hijri_date = HijriDate(g_date.year, g_date.month, g_date.day, gr=True)
            hijri_date_str = "{0}/{1}/{2}".format(int(hijri_date.year), int(hijri_date.month), int(hijri_date.day))
            return self.num2hindi(hijri_date_str)
        except Exception:
            return False

    def get_day_name(self, g_date):
        try:
            g_date = fields.Date.from_string(g_date)
            hijri_date = HijriDate(g_date.year, g_date.month, g_date.day, gr=True)
            return hijri_date.day_name
        except Exception:
            return False

    def get_hindi_nums(self, string_number):
        return self.num2hindi(string_number)

    # Create the PDF attachment and save it in database or ftp
    @api.multi
    def create_report_attachment(self):
        self.env['report'].get_pdf(self, 'smart_hr.hr_deputation_report')
        self.env['report'].get_pdf(self, 'smart_hr.hr_dep_accr_report')


class hr_deputation_category(models.Model):
    _name = 'hr.deputation.category'
    _description = 'Deputation Countries Categories'

    category = fields.Selection([
        ('high', u'مرتفعة'),
        ('a', u'أ'),
        ('b', u'ب'),
        ('c', u'ج'),
    ], string=u'الفئات', default='c')
    country_ids = fields.Many2many('res.country', 'deputation_country_rel', 'count_id', 'dep_id', string=u'البلاد')

    _sql_constraints = [
        ('unique_category', 'UNIQUE(category)', u"لا يمكن تكرار الفئات  "),
    ]

    @api.multi
    def name_get(self):
        res = []
        for rec in self:
            name = dict(self.env['hr.deputation.category'].fields_get(allfields=['category'])['category']['selection'])[str(rec.category)]
            res.append((rec.id, name))
        return res