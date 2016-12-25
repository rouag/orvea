# -*- coding: utf-8 -*-


from openerp import models, fields, api, tools, _
import openerp.addons.decimal_precision as dp


class HrPayslipRun(models.Model):
    _name = 'hr.payslip.run'
    _inherit = ['hr.payslip.run', 'mail.thread']

    state = fields.Selection([('draft', 'مسودة'),
                              ('verify', 'في إنتظار الإعتماد'),
                              ('done', 'تم'),
                              ('cancel', 'ملغى'),
                              ('close', 'مغلق'),
                              ], 'الحالة', select=1, readonly=1, copy=False)

    @api.one
    def action_verify(self):
        self.state = 'verify'
        for slip in self.slip_ids:
            if slip.state == 'draft':
                slip.state = 'verify'

    @api.one
    def action_done(self):
        self.state = 'done'
        for slip in self.slip_ids:
            slip.state = 'done'

    @api.one
    def action_cancel(self):
        self.state = 'cancel'
        for slip in self.slip_ids:
            slip.state = 'cancel'


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    days_off_line_ids = fields.One2many('hr.payslip.days_off', 'payslip_id', 'الإجازات والغيابات', readonly=True, states={'draft': [('readonly', False)]})
    state = fields.Selection([('draft', 'مسودة'),
                              ('verify', 'في إنتظار الإعتماد'),
                              ('done', 'تم'),
                              ('cancel', 'ملغى'),
                              ], 'الحالة', select=1, readonly=1, copy=False)

    @api.one
    def action_verify(self):
        self.state = 'verify'

    @api.one
    def action_done(self):
        self.state = 'done'

    @api.one
    def action_cancel(self):
        self.state = 'cancel'

    @api.onchange('employee_id', 'date_from')
    def onchange_employee(self):
        if (not self.employee_id) or (not self.date_from) or (not self.date_to):
            return
        employee_id = self.employee_id
        date_from = self.date_from
        date_to = self.date_to
        # get name fo month
        # ttyme = datetime.fromtimestamp(time.mktime(time.strptime(date_from, "%Y-%m-%d")))
        # tools.ustr(ttyme.strftime('%B-%Y')
        self.name = _('راتب الموظف %s للفترة : %s - %s') % (employee_id.name, date_from, date_to)
        self.company_id = employee_id.company_id
        self.struct_id = self.employee_id.payroll_structure_id
        # computation of أيام العمل
        return


class HrPayslipWorkedDays(models.Model):
    _inherit = 'hr.payslip.worked_days'

    # make contract_id not required
    contract_id = fields.Many2one('hr.contract', 'Contract', required=False)


class HrPayslipDaysOff(models.Model):
    _name = 'hr.payslip.days_off'

    name = fields.Char('الوصف', required=1)
    payslip_id = fields.Many2one('hr.payslip', 'Pay Slip', required=1, ondelete='cascade', select=1)
    code = fields.Char('الرمز', required=0)
    number_of_days = fields.Float('عدد الأيام')
    number_of_hours = fields.Float('عدد الساعات')


class HrSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'
    _order = 'sequence'
