# -*- coding: utf-8 -*-
####################################
### This Module Created by Slnee ###
####################################

from openerp import fields, models, api
from openerp.exceptions import ValidationError

class hr_attendance_followup_summary_view_wizard(models.TransientModel):
    _name = "hr.attendance.followup.summary.view.wizard"
    _description = "Attendance Follow-Up Summary View Wizard"

    employee_ids = fields.Many2many('hr.employee', 'att_summary_emp_rel', 'emp_id', 'wiz_id', string=u'الموظفون')
    all_employees = fields.Boolean(string=u'كل الموظفون', default=True)
    date_from = fields.Date(string=u'تاريخ من', default=fields.Datetime.now())
    date_to = fields.Date(string=u'تاريخ الى', default=fields.Datetime.now())

    @api.constrains('date_from', 'date_to')
    def check_dates(self):
        if self.date_from > self.date_to:
            raise ValidationError(u"'تاريخ من' يجب ان يكون اصغر من 'تاريخ إلى'")

    @api.multi
    def button_display(self):
        for wiz in self:
            ret = self.env.ref('smart_hr.action_hr_attendance_followup_summary_view_report').read()[0]
            ret['context'] = {
                'employee_ids': wiz.employee_ids.ids,
                'all_employees': wiz.all_employees,
                'date_from': wiz.date_from,
                'date_to': wiz.date_to,
            }
            return ret

    @api.multi
    def button_print(self):
        # Printing
        report_action = self.env['report'].get_action(self, 'smart_hr.hr_attendance_followup_summary_report')
        data = {
            'ids': [],
            'model': 'hr.employee',
            'form': self.read([])[0],
        }
        report_action['data'] = data
        return report_action