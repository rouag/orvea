# -*- coding: utf-8 -*-


from openerp import fields, models, api
from openerp.exceptions import ValidationError

class hr_attendance_followup_view_wizard(models.TransientModel):
    _name = "hr.attendance.followup.view.wizard"
    _description = "Attendance Follow-Up View Wizard"

    employee_id = fields.Many2one('hr.employee', string=u'الموظف')
    employee_ids = fields.Many2many('hr.employee', 'hr_emp_attend_fol_wiz_rel', 'wiz_id', 'emp_id', string=u'الموظفون')
    multi_employee = fields.Boolean(string=u'طباعة موظفون')
    date_from = fields.Date(string=u'تاريخ من', default=fields.Datetime.now())
    date_to = fields.Date(string=u'تاريخ الى', default=fields.Datetime.now())
    absent = fields.Boolean(string=u'الغيابات', default=True)
    lateness = fields.Boolean(string=u'التأخيرات', default=True)
    fingerprint = fields.Boolean(string=u'التبصيم', default=True)

    @api.constrains('date_from', 'date_to')
    def check_dates(self):
        if self.date_from > self.date_to:
            raise ValidationError(u"'تاريخ من' يجب ان يكون اصغر من 'تاريخ إلى'")

    @api.multi
    def button_display(self):
        for wiz in self:
            ret = self.env.ref('smart_hr.action_hr_attendance_followup_view_report').read()[0]
            ret['context'] = {
                'employee_id': wiz.employee_id.id,
                'date_from': wiz.date_from,
                'date_to': wiz.date_to,
                'absent': wiz.absent,
                'lateness': wiz.lateness,
                'fingerprint': wiz.fingerprint,
            }
            ret['name'] += " '" + wiz.employee_id.name + "'"
            return ret

    @api.multi
    def button_print(self):
        # Printing
        report_action = self.env['report'].get_action(self, 'smart_hr.hr_attendance_followup_report')
        data = {
            'ids': [],
            'model': 'hr.employee',
            'form': self.read([])[0],
        }
        report_action['data'] = data
        return report_action