# -*- coding: utf-8 -*-

from openerp import fields, models, api, _
from openerp.exceptions import ValidationError
from lxml import etree

class hr_overtime(models.Model):
    _name = 'hr.overtime'
    _inherit = ['ir.needaction_mixin']
    _description = 'Overtime Decision'

    name = fields.Char(string=u'رقم القرار', advanced_search=True)
    date = fields.Date(string=u'تاريخ', default=fields.Datetime.now())
    is_direct_manager = fields.Boolean(string='Is Direct Manager', compute='_is_direct_manager')
    is_current_user = fields.Boolean(string='Is Current User', compute='_is_current_user')
    overtime_line_ids = fields.One2many('hr.overtime.line', 'overtime_id', string=u'موظفين', default=lambda self: [(0, _, {'employee_id': self.env['hr.employee'].search([('user_id', '=', self._uid)], limit=1), 'line_type': 1, 'date_from': fields.Date.today(), 'date_to': fields.Date.today()})])
    state = fields.Selection([
        ('draft', u'طلب'),
        ('dm', u'مدير المباشر'),
        ('audit', u'تدقيق'),
        ('acc', u'إرتباط مالى'),
        ('hrm', u'مدير شؤون الموظفين'),
        ('done', u'اعتمدت'),
        ('refuse', u'رفض'),
    ], string=u'الحالة', default='draft', advanced_search=True)

    @api.model
    def create(self, vals):
        res = super(hr_overtime, self).create(vals)
        # Sequence
        vals = {}
        vals['name'] = self.env['ir.sequence'].get('hr.overtime.seq')
        res.write(vals)
        return res

    @api.multi
    def unlink(self):
        for rec in self:
            # Delete lines first
            for line in rec.overtime_line_ids:
                line.unlink()
        # Delete overtime last
        return super(hr_overtime, self).unlink()

    @api.depends('overtime_line_ids.employee_id')
    def _is_direct_manager(self):
        for rec in self:
            if self.env['res.users'].browse(rec._uid).has_group('smart_hr.group_sys_manager'):
                rec.is_direct_manager = True
            elif rec.overtime_line_ids.employee_id.user_id.id != rec._uid:
                if rec.overtime_line_ids.employee_id.parent_id.user_id.id == rec._uid:
                    rec.is_direct_manager = True

    @api.depends('overtime_line_ids.employee_id')
    def _is_current_user(self):
        for rec in self:
            if self.env['res.users'].browse(rec._uid).has_group('smart_hr.group_sys_manager'):
                rec.is_current_user = True
            elif rec.overtime_line_ids.employee_id.user_id.id == rec._uid:
                rec.is_current_user = True

    @api.one
    def button_dm(self):
        for ot in self:
            ot.state = 'dm'

    @api.one
    def button_audit(self):
        for ot in self:
            ot.state = 'audit'

    @api.one
    def button_acc(self):
        for ot in self:
            ot.state = 'acc'

    @api.one
    def button_hrm(self):
        for ot in self:
            ot.state = 'hrm'

    @api.one
    def button_done(self):
        for ot in self:
            ot.state = 'done'
        self.create_report_attachment()

    @api.one
    def button_refuse_dm(self):
        for ot in self:
            ot.state = 'refuse'

    @api.one
    def button_refuse_audit(self):
        for ot in self:
            ot.state = 'refuse'

    @api.one
    def button_refuse_acc(self):
        for ot in self:
            ot.state = 'refuse'

    @api.one
    def button_refuse_hrm(self):
        for ot in self:
            ot.state = 'refuse'

    @api.constrains('overtime_line_ids')
    def check_lines(self):
        for rec in self:
            # Check for incomplete data
            if not rec.overtime_line_ids:
                raise ValidationError(u"البيانات غير مكتملة")
            elif len(rec.overtime_line_ids._ids) > 1:
                raise ValidationError(u"يجب أدخال موظف واحد فقط")
            # Check for duplicate entry
            else:
                for line in rec.overtime_line_ids:
                    tmp_set = rec.overtime_line_ids - line
                    for tmp_ln in tmp_set:
                        if tmp_ln.employee_id == line.employee_id:
                            raise ValidationError(u"تم إدخال موظف اكثر من مرة يرجى التحقق")

    @api.model
    def _needaction_domain_get(self):
        return [
            ('state', 'in', ['dm', 'audit', 'acc', 'hrm']),
        ]

    """
    Report Methods
    """
    @api.multi
    def create_report_attachment(self):
        self.env['report'].get_pdf(self, 'smart_hr.hr_overtime_report')


class hr_overtime_line(models.Model):
    _name = 'hr.overtime.line'
    _description = 'Overtime Line'
    _rec_name = 'overtime_id'

    employee_id = fields.Many2one('hr.employee', string=u'موظف')
    line_type = fields.Selection([
        (1, u'دوام عادى'),
        (2, u'عطلة آخر الأسبوع'),
        (3, u'عطلة الأجازات و الأعياد الرسمية'),
    ], string=u'نوع', default=1)
    reason = fields.Text(string=u'سبب')
    date_from = fields.Date(string=u'تاريخ من', default=fields.Datetime.now())
    date_to = fields.Date(string=u'تاريخ الى', default=fields.Datetime.now())
    days = fields.Integer(string=u'أيام', compute='_compute_days')
    hours = fields.Float(string=u'ساعات', default=0.0)
    overtime_id = fields.Many2one('hr.overtime', string='Overtime Ref.')

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
        res = super(hr_overtime_line, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        if view_type in ['form', 'tree']:
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

    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        # Objects
        leave_obj = self.env['hr.holidays']
        dep_obj = self.env['hr.deputation']
        train_obj = self.env['hr.training']
        overtime_obj = self.env['hr.overtime']
        #
        for ot in self:
            # Check for incorrect dates
            if ot.date_from > ot.date_to:
                raise ValidationError(u"يجب ان يكون تاريخ من اصغر من تاريخ الى")
            # Check for any intersection with other decisions
            # Overtime
            search_domain = [
                ('overtime_line_ids.employee_id', '=', ot.employee_id.id),
                ('overtime_line_ids.id', '!=', ot.id),
                ('state', '!=', 'refuse'),
            ]
            for rec in overtime_obj.search(search_domain):
                for line in rec.overtime_line_ids:
                    if (line.date_from <= ot.date_from <= line.date_to or \
                            line.date_from <= ot.date_to <= line.date_to or \
                            ot.date_from <= line.date_from <= ot.date_to or \
                            ot.date_from <= line.date_to <= ot.date_to) and \
                            line.employee_id == ot.employee_id and \
                            line.id != ot.id:
                        raise ValidationError(u"هناك تداخل فى التواريخ مع قرار سابق فى خارج الدوام")
            # Leave
            domain_search = [
                ('employee_id', '=', ot.employee_id.id),
                ('state', '!=', 'refuse'),
            ]
            for rec in leave_obj.search(domain_search):
                if rec.date_from <= ot.date_from <= rec.date_to or \
                        rec.date_from <= ot.date_to <= rec.date_to or \
                        ot.date_from <= rec.date_from <= ot.date_to or \
                        ot.date_from <= rec.date_to <= ot.date_to:
                    raise ValidationError(u"هناك تداخل فى التواريخ مع قرار سابق فى الاجازات")
            # Training
            search_domain = [
                ('employee_ids', 'in', [ot.employee_id.id]),
                ('state', '!=', 'refuse'),
            ]
            for rec in train_obj.search(search_domain):
                if rec.effective_date_from <= ot.date_from <= rec.effective_date_to or \
                        rec.effective_date_from <= ot.date_to <= rec.effective_date_to or \
                        ot.date_from <= rec.effective_date_from <= ot.date_to or \
                        ot.date_from <= rec.effective_date_to <= ot.date_to:
                    raise ValidationError(u"هناك تداخل فى التواريخ مع قرار سابق فى التدريب")
            # Deputation
            search_domain = [
                ('employee_id', '=', ot.employee_id.id),
                ('state', '!=', 'refuse'),
            ]
            for rec in dep_obj.search(search_domain):
                if rec.date_from <= ot.date_from <= rec.date_to or \
                        rec.date_from <= ot.date_to <= rec.date_to or \
                        ot.date_from <= rec.date_from <= ot.date_to or \
                        ot.date_from <= rec.date_to <= ot.date_to:
                    raise ValidationError(u"هناك تداخل فى التواريخ مع قرار سابق فى الأنتداب")

    @api.constrains('hours')
    def _check_hours(self):
        for rec in self:
            if rec.hours > 3.5 and rec.line_type == 1:
                raise ValidationError(u"لا يمكن عمل عدد ساعات خارج دوام اكثر من نصف الدوام")
            elif rec.hours > 7 and rec.line_type in [2, 3]:
                raise ValidationError(u"لا يمكن عمل عدد ساعات خارج دوام اكثر من دوام كامل")
            elif rec.hours <= 0:
                raise ValidationError(u"عدد ساعات خارج الدوام يجب ان تكون اكبر من صفر")

    @api.depends('line_type', 'date_from', 'date_to')
    def _compute_days(self):
        for rec in self:
            count = 0
            if rec.date_from and rec.date_to:
                start_date = fields.Date.from_string(rec.date_from)
                end_date = fields.Date.from_string(rec.date_to)
                for single_date in daterange(start_date, end_date):
                    if rec.line_type == 1 and single_date.weekday() not in [4, 5]:
                        count += 1
                    elif rec.line_type == 2 and single_date.weekday() in [4, 5]:
                        count += 1
                    elif rec.line_type == 3:
                        count += 1
                days = count
                rec.days = days