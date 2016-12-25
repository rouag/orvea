# -*- coding: utf-8 -*-


from openerp import fields, models, api
from openerp.exceptions import ValidationError
from lxml import etree

class hr_attendance_view_wizard(models.TransientModel):
    _name = "hr.attendance.view.wizard"
    _description = "Attendance View Wizard"

    employee_id = fields.Many2one('hr.employee', string=u'الموظف', default=lambda self: self.env['hr.employee'].search([('user_id', '=', self._uid)], limit=1))
    employee_ids = fields.Many2many('hr.employee', 'hr_emp_attend_wiz_rel', 'wiz_id', 'emp_id', string=u'الموظفون')
    multi_employee = fields.Boolean(string=u'طباعة موظفون')
    edit_employee = fields.Boolean(string='Allow Editing Employee', compute='_set_edit_employee')
    date_from = fields.Date(string=u'تاريخ من', default=fields.Datetime.now())
    date_to = fields.Date(string=u'تاريخ الى', default=fields.Datetime.now())

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
        res = super(hr_attendance_view_wizard, self).fields_view_get(view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
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
                employee_ids = arch.xpath("//field[@name='employee_ids']")[0]
                # Updated attributes
                employee_id.set('domain', "['|',('id','in',%s),('user_id','=',%s)]" % (emp_ids.ids, uid))
                employee_ids.set('domain', "['|',('id','in',%s),('user_id','=',%s)]" % (emp_ids.ids, uid))
            res['arch'] = etree.tostring(arch, encoding="utf-8")
        return res

    @api.depends('employee_id', 'date_from', 'date_to')
    def _set_edit_employee(self):
        for rec in self:
            is_followup = self.env['res.users'].browse(rec._uid).has_group('smart_hr.group_followup')
            is_followup_manager = self.env['res.users'].browse(rec._uid).has_group('smart_hr.group_followup_manager')
            is_direct_manager = self.env['res.users'].browse(rec._uid).has_group('smart_hr.group_dm')
            is_hrm = self.env['res.users'].browse(rec._uid).has_group('smart_hr.group_hrm')
            is_adm = self.env['res.users'].browse(rec._uid).has_group('smart_hr.group_adm')
            is_municipality_president = self.env['res.users'].browse(rec._uid).has_group('smart_hr.group_municipality_president')
            if is_followup or is_followup_manager or is_direct_manager or is_hrm or is_adm or is_municipality_president:
                rec.edit_employee = True

    @api.constrains('date_from', 'date_to')
    def check_dates(self):
        if self.date_from > self.date_to:
            raise ValidationError(u"'تاريخ من' يجب ان يكون اصغر من 'تاريخ إلى'")

    @api.multi
    def button_display(self):
        for wiz in self:
            ret = self.env.ref('smart_hr.action_hr_attendance_view_report').read()[0]
            ret['context'] = {
                'employee_id': wiz.employee_id.id,
                'date_from': wiz.date_from,
                'date_to': wiz.date_to,
            }
            ret['name'] += " '" + wiz.employee_id.name + "'"
            return ret

    @api.multi
    def button_print(self):
        # Printing
        report_action = self.env['report'].get_action(self, 'smart_hr.hr_attendance_report')
        data = {
            'ids': [],
            'model': 'hr.employee',
            'form': self.read([])[0],
        }
        report_action['data'] = data
        return report_action