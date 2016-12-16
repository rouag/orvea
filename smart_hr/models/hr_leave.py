# -*- coding: utf-8 -*-

from openerp import fields, models, api, _
from openerp.tools import SUPERUSER_ID
from openerp.exceptions import ValidationError
from lxml import etree
from ..apis.iclib.hijri  import ummqura
from ..apis.datetime_func import daterange
from umalqurra.hijri_date import HijriDate
from datetime import date, datetime, timedelta
from smart_utils.num2hindi import num2hindi

class HrLeave(models.Model):
    _name = 'hr.leave'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = 'Leave Request'
    _order = 'id desc'

    name = fields.Char(string=u'رقم القرار', advanced_search=True)
    date = fields.Date(string=u'تاريخ الطلب', default=fields.Datetime.now())
    employee_id = fields.Many2one('hr.employee', string=u'الموظف', default=lambda self: self.env['hr.employee'].search([('user_id', '=', self._uid)], limit=1), advanced_search=True)
    is_direct_manager = fields.Boolean(string='Is Direct Manager', compute='_is_direct_manager')
    is_current_user = fields.Boolean(string='Is Current User', compute='_is_current_user')
    edit_employee = fields.Boolean(string='Allow Editing Employee')
    alternative_employee_id = fields.Many2one('hr.employee', string=u'الموظف البديل', advanced_search=True)
    date_from = fields.Date(string=u'التاريخ من', default=fields.Datetime.now())
    date_to = fields.Date(string=u'التاريخ الى', default=fields.Datetime.now())
    duration = fields.Integer(string=u'الأيام', compute='_compute_duration')
    leave_type_id = fields.Many2one('hr.leave.type', string=u'نوع الأجازة', default=lambda self: self.env.ref('smart_hr.data_hr_leave_type_01'), advanced_search=True)
    leave_type_stock = fields.Float(string=u'رصيد الاجازة', compute='_compute_leave_type_stock')
    # Extension
    is_extension = fields.Boolean(string=u'تمديد إجازة')
    is_extended = fields.Boolean(string=u'ممددة', compute='_is_extended')
    extended_leave_id = fields.Many2one('hr.leave', string=u'الإجازة الممددة')
    parent_id = fields.Many2one('hr.leave', string=u'Parent')
    extension_leave_ids = fields.One2many('hr.leave', 'parent_id', string=u'التمديدات')
    # Cancellation
    is_cancelled = fields.Boolean(string=u'ملغاة', compute='_is_cancelled')
    is_started = fields.Boolean(string=u'بدأت', compute='_compute_is_started')
    leave_cancellation_ids = fields.One2many('hr.leave.cancellation', 'leave_id', string=u'طلبات الإلغاء')
    # Sick Leave Fields
    hospital = fields.Char(string=u'المستشفى')
    hospital_report_no = fields.Char(string=u'رقم التقرير الطبي')
    hospital_report_date = fields.Date(string=u'تاريخ التقرير الطبي')
    hospital_attach = fields.Binary(string=u'ارفاق التقرير الطبي')
    hospital_attach_fname = fields.Char(string=u'اسم ملف التقرير الطبي')
    # Aid Leave
    aid_letter = fields.Char(string=u'مسمى الخطاب')
    aid_letter_no = fields.Char(string=u'رقم الخطاب')
    aid_letter_date = fields.Char(string=u'تاريخ الخطاب')
    # Sport Leave
    sport_letter = fields.Char(string=u'مسمى الخطاب')
    sport_letter_no = fields.Char(string=u'رقم الخطاب')
    sport_letter_date = fields.Char(string=u'تاريخ الخطاب')
    sport_reason = fields.Char(string=u'للمشاركة في')
    # Education Leave
    edu_subject = fields.Char(string=u'لدراسة')
    edu_specialty = fields.Char(string=u'التخصص')
    # Death Leave
    relationship = fields.Selection([
        (1, u'أحد الوالدين أو الأبناء أو الزوجة'),
        (2, u'أحد الإخوة أو الأخوات'),
    ], string=u'صلة القرابة', default=1)
    justification_file = fields.Binary(string=u'ملف الإثبات')
    justification_file_fname = fields.Char(stirng=u'إسم ملف الإثبات')
    notes = fields.Text(string=u'ملاحظات')
    salary_calc_type = fields.Selection([
        (1, u'راتب كامل'),
        (2, u'نصف راتب'),
        (3, u'ربع راتب'),
        (4, u'بدون راتب'),
    ], string=u'طريقة احتساب الراتب', default=1)
    state_dm = fields.Selection([
        (1, u'الأول'),
        (2, u'الثاني'),
        (3, u'الثالث'),
        (4, u'الرابع'),
        (5, u'الخامس'),
        (6, u'السادس'),
        (7, u'السابع'),
        (8, u'الثامن'),
        (9, u'التاسع'),
        (10, u'العاشر'),
    ], string=u'حالات المدراء المباشرين', default=1)
    state = fields.Selection([
        ('draft', u'طلب'),
        ('dm', u'مدير المباشر'),
        ('audit', u'تدقيق'),
        ('hrm', u'مدير شؤون الموظفين'),
        ('done', u'اعتمدت'),
        ('refuse', u'رفض'),
        ('cancel', u'ملغاة'),
    ], string=u'حالة', default='draft', advanced_search=True)

    @api.model
    def create(self, vals):
        res = super(HrLeave, self).create(vals)
        # Extension
        extended_leave_id = vals.get('extended_leave_id', False)
        if extended_leave_id:
            extended_leave = self.env['hr.leave'].browse(extended_leave_id)
            # Add this leave to extension list
            extended_leave.extension_leave_ids += res
        # Sequence
        vals = {}
        vals['name'] = self.env['ir.sequence'].get('hr.leave.seq')
        res.write(vals)
        # If direct manager is creator exclude draft state
        if res.edit_employee:
            res.button_dm()
        return res

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state != 'draft' and self._uid != SUPERUSER_ID:
                raise ValidationError(u'لا يمكن حذف الإجازة فى هذه المرحلة يرجى مراجعة مدير النظام')
        return super(HrLeave, self).unlink()

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
        res = super(HrLeave, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
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
                alternative_employee_id = arch.xpath("//field[@name='alternative_employee_id']")[0]
                # Updated attributes
                employee_id.set('domain', "['|',('id','in',%s),('user_id','=',%s)]" % (emp_ids.ids, uid))
                alternative_employee_id.set('domain', "['|',('id','in',%s),('user_id','=',%s)]" % (emp_ids.ids, uid))
            res['arch'] = etree.tostring(arch, encoding="utf-8")
        return res

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

    @api.depends('employee_id')
    def _is_current_user(self):
        for rec in self:
            # System Admin Bypass
            if self.env['res.users'].browse(rec._uid).has_group('smart_hr.group_sys_manager'):
                rec.is_current_user = True
            elif rec.employee_id.user_id.id == rec._uid:
                rec.is_current_user = True

    @api.depends('extension_leave_ids')
    def _is_extended(self):
        # Check if the leave have a pending or completed extension leave
        for rec in self:
            is_extended = False
            for ext in rec.extension_leave_ids:
                if ext.state != 'refuse':
                    is_extended = True
                    break
            rec.is_extended = is_extended

    @api.depends('leave_cancellation_ids')
    def _is_cancelled(self):
        # Check if the leave have a pending or completed leave cancellation
        for rec in self:
            is_cancelled = False
            for cancel in rec.leave_cancellation_ids:
                if cancel.state != 'refuse':
                    is_cancelled = True
                    break
            rec.is_cancelled = is_cancelled

    @api.depends('date_from')
    def _compute_is_started(self):
        for rec in self:
            if rec.date_from <= datetime.today().strftime('%Y-%m-%d'):
                rec.is_started = True

    @api.multi
    def _get_dm_depth(self, uid, emp):
        # Objects
        employee_obj = self.env['hr.employee']
        # Variables
        depth = 0
        manager_id = employee_obj.search([('user_id', '=', uid)], limit=1)
        employee_id = emp
        while True:
            depth += 1
            if employee_id.parent_id == manager_id:
                break
            elif depth > 10:
                break
            employee_id = employee_id.parent_id
        return depth

    @api.depends('date_from', 'date_to')
    def _compute_duration(self):
        for lv in self:
            if lv.date_from and lv.date_to:
                start_date = fields.Date.from_string(lv.date_from)
                end_date = fields.Date.from_string(lv.date_to)
                duration = (end_date - start_date).days + 1
                lv.duration = duration

    @api.depends('leave_type_id', 'employee_id')
    def _compute_leave_type_stock(self):
        for lv in self:
            if lv.employee_id and lv.leave_type_id:
                # Normal, Statement and Accompaniment: should all take from the Normal leave stock
                if lv.leave_type_id in [self.env.ref('smart_hr.data_hr_leave_type_01'),
                                        self.env.ref('smart_hr.data_hr_leave_type_11'),
                                        self.env.ref('smart_hr.data_hr_leave_type_16')]:
                    lv.leave_type_stock = lv.employee_id.leave_normal
                # Emergency
                elif lv.leave_type_id == self.env.ref('smart_hr.data_hr_leave_type_02'):
                    lv.leave_type_stock = lv.employee_id.leave_emergency
                # Compensation
                elif lv.leave_type_id == self.env.ref('smart_hr.data_hr_leave_type_10'):
                    lv.leave_type_stock = lv.employee_id.leave_compensation

    @api.constrains('date_from', 'date_to')
    def check_dates(self):
        # Objects
        leave_obj = self.env['hr.leave']
#         dep_obj = self.env['hr.deputation']
        train_obj = self.env['hr.training']
        overtime_obj = self.env['hr.overtime']
        eid_obj = self.env['hr.eid']
        # Variables
        normal_leave = self.env.ref('smart_hr.data_hr_leave_type_01')
        emergency_leave = self.env.ref('smart_hr.data_hr_leave_type_02')
        sick_leave = self.env.ref('smart_hr.data_hr_leave_type_03')
        compensation_leave = self.env.ref('smart_hr.data_hr_leave_type_10')
        statement_leave = self.env.ref('smart_hr.data_hr_leave_type_16')
        death_leave = self.env.ref('smart_hr.data_hr_leave_type_17')
        newborn_leave = self.env.ref('smart_hr.data_hr_leave_type_18')
        for lv in self:
            # Sick Leave 2 days validation
            if lv.leave_type_id == sick_leave:
                days_count = -1
                for single_date in daterange(fields.Date.from_string(lv.date_to), fields.Date.from_string(fields.Date.today())):
                    if single_date.weekday() not in [4, 5]:
                        days_count += 1
                if days_count > 2:
                    raise ValidationError(u"لا يمكن التقديم على إجازة مرضية بعد أكثر من يومين")
            # Date validation
            if lv.date_from > lv.date_to:
                raise ValidationError(u"تاريخ من يجب ان يكون أصغر من تاريخ الى")
            # Leave stock validation
            if lv.leave_type_stock < lv.duration and lv.leave_type_id in [normal_leave, emergency_leave, compensation_leave, statement_leave]:
                raise ValidationError(u"الرصيد غير كافي")
            # Normal Leave minimum request validation
            if lv.leave_type_id == normal_leave and lv.duration < 5:
                raise ValidationError(u"أقل فترة يمكن طلبها من نوع إجازة عادية 5 أيام")
            # Consecutive leaves check for normal leaves
            # (not applicable for extension leaves)
            if lv.leave_type_id in [normal_leave] and not lv.is_extension:
                # Check if there is a previous leave request
                # Get the day number to handle the weekend gap
                week_day = fields.Date.from_string(lv.date_from).weekday()
                # General case
                diff = 1
                # The leave start day is Sunday
                if week_day == 6:
                    diff = 3
                # The leave start day is Saturday
                elif week_day == 5:
                    diff = 2
                previous_day = fields.Date.to_string(fields.Date.from_string(lv.date_from) - timedelta(days=diff))
                domain_search = [
                    ('employee_id', '=', lv.employee_id.id),
                    ('id', '!=', lv.id),
                    ('state', 'not in', ['refuse', 'cancel']),
                    ('leave_type_id', 'in', [normal_leave.id]),
                    ('date_to', '=', previous_day)
                ]
                if leave_obj.search_count(domain_search) > 0:
                    raise ValidationError(u"لديك إجازة سابقة تنتهي مباشرة قبل الإجازة الجديدة, يمكنك تمديد الإجازة السابقة")
            # Statement Leave validation
            if lv.leave_type_id == statement_leave:
                # Employee must have ZERO days in emergency leave stock
                if lv.employee_id.leave_emergency > 0:
                    raise ValidationError(u"لديك رصيد إجازة إضطرارية, لا يمكنك التقديم على إجازة إفادة")
                # Leave duration can only be from 1 to 4 days
                if lv.duration > 4:
                    raise ValidationError(u"فترة إجازة الإفادة لا يمكن أن تتجاوز 4 أيام")
            # Death Leave
            if lv.leave_type_id == death_leave:
                if lv.relationship == 1 and lv.duration > 3:
                    raise ValidationError(u"إجازة الوفاة في هاته الحالة لا يمكن أن تتجاوز 3 أيام")
                if lv.relationship == 2 and lv.duration > 1:
                    raise ValidationError(u"إجازة الوفاة في هاته الحالة محددة بيوم واحد")
            # Newborn baby leave
            if lv.leave_type_id == newborn_leave:
                if lv.duration != 1:
                    raise ValidationError(u"إجازة المولود يجب ألا تتجاوز اليوم الواحد")
            # Date overlap
            # Leaves
            domain_search = [
                ('employee_id', '=', lv.employee_id.id),
                ('id', '!=', lv.id),
                ('state', 'not in', ['refuse', 'cancel']),
            ]
            for rec in leave_obj.search(domain_search):
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
            # Overtime
            search_domain = [
                ('overtime_line_ids.employee_id', '=', lv.employee_id.id),
                ('state', '!=', 'refuse'),
            ]
            for rec in overtime_obj.search(search_domain):
                for line in rec.overtime_line_ids:
                    if line.date_from <= lv.date_from <= line.date_to or \
                            line.date_from <= lv.date_to <= line.date_to or \
                            lv.date_from <= line.date_from <= lv.date_to or \
                            lv.date_from <= line.date_to <= lv.date_to:
                        raise ValidationError(u"هناك تداخل فى التواريخ مع قرار سابق فى خارج الدوام")
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
            # Deputation
            search_domain = [
                ('employee_id', '=', lv.employee_id.id),
                ('state', '!=', 'refuse'),
            ]
#             for rec in dep_obj.search(search_domain):
#                 if rec.date_from <= lv.date_from <= rec.date_to or \
#                         rec.date_from <= lv.date_to <= rec.date_to or \
#                         lv.date_from <= rec.date_from <= lv.date_to or \
#                         lv.date_from <= rec.date_to <= lv.date_to:
#                     raise ValidationError(u"هناك تداخل في التواريخ مع قرار سابق في الإنتداب")

    @api.constrains('alternative_employee_id')
    def check_alternative_employee_id(self):
        # Objects
        leave_obj = self.env['hr.leave']
#         dep_obj = self.env['hr.deputation']
        train_obj = self.env['hr.training']
        overtime_obj = self.env['hr.overtime']
        for lv in self:
            if lv.alternative_employee_id:
                # Check overlap
                # Leave
                search_domain = [
                    '|',
                    ('employee_id', '=', lv.alternative_employee_id.id),
                    ('alternative_employee_id', '=', lv.alternative_employee_id.id),
                    ('id', '!=', lv.id),
                    ('state', 'not in', ['refuse', 'cancel']),
                ]
                for rec in leave_obj.search(search_domain):
                    if rec.date_from <= lv.date_from <= rec.date_to or \
                            rec.date_from <= lv.date_to <= rec.date_to or \
                            lv.date_from <= rec.date_from <= lv.date_to or \
                            lv.date_from <= rec.date_to <= lv.date_to:
                        raise ValidationError(u"الموظف البديل لديه تداخل في التواريخ مع قرار سابق في الإجازات")
                # Deputation
                search_domain = [
                    ('employee_id', '=', lv.alternative_employee_id.id),
                    ('state', '!=', 'refuse'),
                ]
#                 for rec in dep_obj.search(search_domain):
#                     if rec.date_from <= lv.date_from <= rec.date_to or \
#                             rec.date_from <= lv.date_to <= rec.date_to or \
#                             lv.date_from <= rec.date_from <= lv.date_to or \
#                             lv.date_from <= rec.date_to <= lv.date_to:
#                         raise ValidationError(u"الموظف البديل لديه تداخل في التواريخ مع قرار سابق في الإنتداب")
                # Training
                search_domain = [
                    ('employee_ids', 'in', [lv.alternative_employee_id.id]),
                    ('state', '!=', 'refuse'),
                ]
                for rec in train_obj.search(search_domain):
                    if rec.effective_date_from <= lv.date_from <= rec.effective_date_to or \
                            rec.effective_date_from <= lv.date_to <= rec.effective_date_to or \
                            lv.date_from <= rec.effective_date_from <= lv.date_to or \
                            lv.date_from <= rec.effective_date_to <= lv.date_to:
                        raise ValidationError(u"الموظف البديل لديه تداخل في التواريخ مع قرار سابق في التدريب")
                # Overtime
                search_domain = [
                    ('overtime_line_ids.employee_id', '=', lv.alternative_employee_id.id),
                    ('state', '!=', 'refuse'),
                ]
                for rec in overtime_obj.search(search_domain):
                    for line in rec.overtime_line_ids:
                        if line.date_from <= lv.date_from <= line.date_to or \
                                line.date_from <= lv.date_to <= line.date_to or \
                                lv.date_from <= line.date_from <= lv.date_to or \
                                lv.date_from <= line.date_to <= lv.date_to:
                            raise ValidationError(u"الموظف البديل لديه تداخل في التواريخ مع قرار سابق في خارج الدوام")

    @api.constrains('leave_type_id', 'state')
    def check_leave_type_requirements(self):
        sick_leave = self.env.ref('smart_hr.data_hr_leave_type_03')
        for rec in self:
            # Check for sick leave
            if rec.leave_type_id == sick_leave:
                if rec.state == "dm" and not (rec.hospital_report_no and \
                        rec.hospital_report_date and rec.hospital_attach):
                    raise ValidationError(u"أدخل المعلومات المتبقية بخصوص خطاب المستشفى")

    @api.one
    def button_dm(self):
        user = self.env['res.users'].browse(self._uid)
        for lv in self:
            lv.state = 'dm'
            # Update leave stock
            # Get the Employee recordset using Administrator user to bypass access rights/rules
            employee_sudo = self.env['hr.employee'].sudo().browse(lv.employee_id.id)
            # Normal, Statement and Accompaniment
            if lv.leave_type_id in [self.env.ref('smart_hr.data_hr_leave_type_01'),
                                    self.env.ref('smart_hr.data_hr_leave_type_11'),
                                    self.env.ref('smart_hr.data_hr_leave_type_16')]:
                new_stock = lv.employee_id.leave_normal - lv.duration
                employee_sudo.write({'leave_normal': new_stock})
            # Emergency
            elif lv.leave_type_id == self.env.ref('smart_hr.data_hr_leave_type_02'):
                new_stock = lv.employee_id.leave_emergency - lv.duration
                employee_sudo.write({'leave_emergency': new_stock})
            # Compensation
            elif lv.leave_type_id == self.env.ref('smart_hr.data_hr_leave_type_10'):
                new_stock = lv.employee_id.leave_compensation - lv.duration
                employee_sudo.write({'leave_compensation': new_stock})
            lv.message_post(u"تم إرسال الطلب من قبل '" + unicode(user.name) + u"'")

    @api.one
    def button_state_approve(self):
        user = self.env['res.users'].browse(self._uid)
        for lv in self:
            if lv.state == 'dm':
                if lv.leave_type_id == self.env.ref('smart_hr.data_hr_leave_type_01') and not lv.alternative_employee_id:
                    raise ValidationError(u'يجب تحديد الموظف البديل قبل الموافقة')
                # System Admin Bypass
                if self.env['res.users'].browse(lv._uid).has_group('smart_hr.group_sys_manager'):
                    lv.button_audit()
#                     return
#                 manager_id = self.env['hr.employee'].search([('user_id', '=', lv._uid)], limit=1)
#                 if manager_id.department_id.is_root:
#                     lv.button_audit()
#                 else:
#                     lv.state_dm += 1
#                     lv.message_post(u"تم الموافقة من قبل '" + unicode(user.name) + u"'")

    @api.one
    def button_audit(self):
        user = self.env['res.users'].browse(self._uid)
        for lv in self:
            lv.state = 'audit'
            lv.message_post(u"تم الموافقة من قبل '" + unicode(user.name) + u"'")

    @api.one
    def button_hrm(self):
        user = self.env['res.users'].browse(self._uid)
        for lv in self:
            lv.state = 'hrm'
            lv.message_post(u"تم التدقيق من قبل '" + unicode(user.name) + u"'")

    @api.one
    def button_done(self):
        user = self.env['res.users'].browse(self._uid)
        for lv in self:
            lv.state = 'done'
            lv.message_post(u"تم الإعتماد من قبل '" + unicode(user.name) + u"'")
        self.create_report_attachment()

    @api.one
    def button_refuse(self):
        for lv in self:
            lv.state = 'refuse'
            # Update leave stock
            # Normal, Statement and Accompaniment
            if lv.leave_type_id in [self.env.ref('smart_hr.data_hr_leave_type_01'),
                                    self.env.ref('smart_hr.data_hr_leave_type_11'),
                                    self.env.ref('smart_hr.data_hr_leave_type_16')]:
                lv.employee_id.leave_normal += lv.duration
            # Emergency
            elif lv.leave_type_id == self.env.ref('smart_hr.data_hr_leave_type_02'):
                lv.employee_id.leave_emergency += lv.duration
            # Compensation
            elif lv.leave_type_id == self.env.ref('smart_hr.data_hr_leave_type_10'):
                lv.employee_id.leave_compensation += lv.duration

    @api.one
    def button_draft(self):
        user = self.env['res.users'].browse(self._uid)
        for lv in self:
            lv.state = 'draft'
            lv.message_post(u"تم إعادة فتح الطلب من قبل '" + unicode(user.name) + u"'")

    @api.multi
    def button_extend(self):
        view_id = self.env.ref('smart_hr.view_form_hr_leave').id
        context = self._context.copy()
        default_date_from = fields.Date.to_string(fields.Date.from_string(self.date_to) + timedelta(days=1))
        context.update({
            u'default_is_extension': True,
            u'default_extended_leave_id': self.id,
            u'default_date_from': default_date_from,
            u'readonly_by_pass': True,
        })
        return {
            'name': 'تمديد الإجازة',
            'view_type': 'form',
            'view_mode': 'tree',
            'views': [(view_id, 'form')],
            'res_model': 'hr.leave',
            'view_id': view_id,
            'type': 'ir.actions.act_window',
            'res_id': False,
            'target': 'current',
            'context': context,
        }

    @api.one
    def button_cancel(self):
        # Objects
        leave_cancellation_obj = self.env['hr.leave.cancellation']
        # Variables
        user = self.env['res.users'].browse(self._uid)
        # Create leave cancellation request
        for lv in self:
            vals = {
                'leave_id': lv.id,
            }
            leave_cancellation_id = leave_cancellation_obj.create(vals)
            # Add to log
            lv.message_post(u"تم ارسال طلب إلغاء من قبل '" + unicode(user.name) + u"'")

    @api.model
    def _needaction_domain_get(self):
        return [
            ('state', 'in', ['dm', 'audit', 'hrm']),
        ]

    ''' Report Functions '''
    def get_today_date(self):
        return self.get_ummqura(fields.Datetime.now())

    def get_ummqura(self, g_date):
        try:
            g_date = fields.Date.from_string(g_date)
            hijri_date = HijriDate(g_date.year, g_date.month, g_date.day, gr=True)
            hijri_date_str = "{0}/{1}/{2}".format(int(hijri_date.year), int(hijri_date.month), int(hijri_date.day))
            return num2hindi(hijri_date_str)
        except Exception:
            return False

    def get_hindi_nums(self, string_number):
        return num2hindi(string_number)

    # Create the PDF attachment and save it in database or ftp
    @api.multi
    def create_report_attachment(self):
        self.env['report'].get_pdf(self, 'smart_hr.hr_leave_report')

class HrLeaveType(models.Model):
    _name = 'hr.leave.type'
    _description = 'Leave Type'

    name = fields.Char(string=u'نوع الاجازة')
    minimum = fields.Integer(string=u'الحد الأدنى')
    maximum = fields.Integer(string=u'الحد الأقصى')
    deductible_normal_leave = fields.Boolean(string=u'تخصم مدتها من رصيد الاجازة العادية')
    deductible_duration_service = fields.Boolean(string=u'تخصم مدتها من فترة الخدمة')
    salary_proportion = fields.Float(string=u'نسبة الراتب المحتسبة (%)', default=100)  
    educ_lvl_req = fields.Boolean(string=u'يطبق شرط المستوى التعليمي')
    evaluation_condition = fields.Boolean(string=u'يطبق شرط تقويم الأداء')
    education_levels = fields.One2many('hr.employee.education.level', 'leave_type', string=u'المستويات التعليمية')
    entitlements = fields.One2many('hr.leave.type.entitlement', 'leave_type', string=u'أنواع الاستحقاقات')
    assessments_required = fields.One2many('hr.assessment.result.config', 'leave_type', string=u'التقييمات المطلوبة')
    
#     leave_stock_default = fields.Integer(string=u'الرصيد الأفتراضي')
#     leave_stock_open = fields.Boolean(string=u'الرصيد مفتوح')
#     
#     @api.constrains('leave_stock_default')
#     def _check_stock_value(self):
#         for rec in self:
#             if rec.leave_stock_default <= 0 and not rec.leave_stock_open:
#                 raise ValidationError(u'قيمة الرصيد الأفتراضي يجب ان يكون اكبر من صفر')
# 
#     """
#         Scheduler function
#     """
#     @api.model
#     def update_leave_stock(self):
#         self.update_normal_leave()
#         self.update_emergency_leave()
# 
#     @api.model
#     def update_normal_leave(self):
#         # Objects
#         employee_obj = self.env['hr.employee']
#         # Check first day of arabic month
#         today_date = fields.Date.from_string(fields.Datetime.now())
#         hijri_date = ummqura.from_gregorian(today_date.year, today_date.month, today_date.day)
#         # Is first day in month
#         if hijri_date[2] == 1:
#             # Loop all employees
#             for emp in employee_obj.search([]):
#                 # Normal
#                 current_normal = emp.leave_normal
#                 expected_normal = current_normal + 3
#                 emp.leave_normal = expected_normal
#                 # TODO Disabling the below part is against labour laws
#                 # TODO Disabled upon municipality request
#                 # if emp.age >= 50 or emp.service_years >= 25:
#                 #     if expected_normal > 120:
#                 #         emp.leave_normal = 120
#                 #     else:
#                 #         emp.leave_normal = expected_normal
#                 # else:
#                 #     if expected_normal > 90:
#                 #         emp.leave_normal = 90
#                 #     else:
#                 #         emp.leave_normal = expected_normal

#     @api.model
#     def update_emergency_leave(self):
#         # Objects
#         employee_obj = self.env['hr.employee']
#         # Check first day of arabic month
#         today_date = fields.Date.from_string(fields.Datetime.now())
#         hijri_date = ummqura.from_gregorian(today_date.year, today_date.month, today_date.day)
#         # Is first day in year
#         if hijri_date[1] == 1 and hijri_date[2] == 1:
#             # Loop all employees
#             for emp in employee_obj.search([]):
#                 # Emergency
#                 emp.leave_emergency = 5
                
                
class HrLeaveTypeEntitlement(models.Model):
    _name = 'hr.leave.type.entitlement'
    _description = u'أنواع الاستحقاقات'
    entitlment_category = fields.Many2one('hr.leave.type.entitlement.category', string=u'فئة الاستحقاق')
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
    leave_type = fields.Many2one('hr.leave.type', string='leave type')
#     leave_stock_open = fields.Boolean(string=u'الرصيد مفتوح')
    
    
class HrleaveTypeEntitlementCategory(models.Model):
    _name = 'hr.leave.type.entitlement.category'
    _description = u'فئة استحقاق'
    
    name = fields.Char(string=u'الاسم')
    grades = fields.Many2many('salary.grid.grade', string=u'المراتب')
