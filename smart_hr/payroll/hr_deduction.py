# -*- coding: utf-8 -*-

from openerp import models, api, fields, _
from openerp.exceptions import ValidationError
from dateutil import relativedelta
import time as time_date
from datetime import datetime

MONTHS = [('1', 'محرّم'),
          ('2', 'صفر'),
          ('3', 'ربيع الأول'),
          ('4', 'ربيع الثاني'),
          ('5', 'جمادي الأولى'),
          ('6', 'جمادي الآخرة'),
          ('7', 'رجب'),
          ('8', 'شعبان'),
          ('9', 'رمضان'),
          ('10', 'شوال'),
          ('11', 'ذو القعدة'),
          ('12', 'ذو الحجة')]


class hrDeduction(models.Model):
    _name = 'hr.deduction'
    _description = u'الحسميات'

    name = fields.Char(string=' المسمى', required=1, readonly=1, states={'new': [('readonly', 0)]})
    # TODO: get default MONTH
    month = fields.Selection(MONTHS, string='الشهر', required=1, readonly=1, states={'new': [('readonly', 0)]})
    date = fields.Date(string='تاريخ الإنشاء', required=1, default=fields.Datetime.now(), readonly=1, states={'new': [('readonly', 0)]})
    date_from = fields.Date('تاريخ من', default=lambda *a: time_date.strftime('%Y-%m-01'),
                            readonly=1, states={'new': [('readonly', 0)]})
    date_to = fields.Date('إلى', default=lambda *a: str(datetime.now() + relativedelta.relativedelta(months=+1, day=1, days=-1))[:10],
                          readonly=1, states={'new': [('readonly', 0)]})
    number_decision = fields.Char(string='رقم القرار', required=1, readonly=1, states={'new': [('readonly', 0)]})
    date_decision = fields.Date(string=' تاريخ القرار', required=1, readonly=1, states={'new': [('readonly', 0)]})
    state = fields.Selection([('new', 'طلب'),
                              ('waiting', 'في إنتظار الإعتماد'),
                              ('cancel', 'مرفوض'),
                              ('done', 'اعتمدت')], string='الحالة', readonly=1, default='new')
    line_ids = fields.One2many('hr.deduction.line', 'deduction_id', string='الحسميات', readonly=1, states={'new': [('readonly', 0)]})
    history_ids = fields.One2many('hr.deduction.history', 'deduction_id', string='سجل التغييرات', readonly=1)

    @api.onchange('month')
    def onchange_month(self):
        if self.month:
            self.name = u'حسميات شهر %s' % self.month
            line_ids = []
            # delete current line
            self.line_ids.unlink()
            # get حسميات  from الخلاصة الشهرية للغيابات والتأخير
            monthly_summary_obj = self.env['hr.monthly.summary.line']
            deduction_type_obj = self.env['hr.deduction.type']
            monthly_summarys = monthly_summary_obj.search([('monthly_summary_id.name', '=', self.month),
                                                           ('monthly_summary_id.state', '=', 'done'),
                                                           ('days_retard', '!=', 0.0), ('days_absence', '!=', 0.0)])
            retard_leave_type = deduction_type_obj.search([('type', '=', 'retard_leave')])[0]
            absence_type = deduction_type_obj.search([('type', '=', 'absence')])[0]
            for summary in monthly_summarys:
                employee = summary.employee_id
                val = {'deduction_id': self.id,
                       'employee_id': employee.id,
                       'department_id': employee.department_id and employee.department_id.id or False,
                       'job_id': employee.job_id and employee.job_id.id or False,
                       'number': employee.number}
                if summary.days_retard:
                    val.update({'amount': summary.days_retard, 'deduction_type_id': retard_leave_type.id})
                    line_ids.append(val)
                if summary.days_absence:
                    val_absence = val.copy()
                    val_absence.update({'amount': summary.days_absence, 'deduction_type_id': absence_type.id})
                    line_ids.append(val_absence)
            self.line_ids = line_ids

    @api.one
    def action_waiting(self):
        self.state = 'waiting'

    @api.multi
    def action_done(self):
        self.state = 'done'

    @api.one
    def action_refuse(self):
        self.state = 'cancel'


class hrDeductionLine(models.Model):
    _name = 'hr.deduction.line'

    deduction_id = fields.Many2one('hr.deduction', string=' الحسميات')
    employee_id = fields.Many2one('hr.employee', string=' إسم الموظف', required=1)
    number = fields.Char(related='employee_id.number', store=True, readonly=True, string=' الرقم الوظيفي')
    job_id = fields.Many2one(related='employee_id.job_id', store=True, readonly=True, string=' الوظيفة')
    department_id = fields.Many2one(related='employee_id.department_id', store=True, readonly=True, string=' القسم')
    deduction_type_id = fields.Many2one('hr.deduction.type', string='نوع الحسم', required=1)
    amount = fields.Char(string='عدد أيام الحسم', required=1)


class hrDeductionHistory(models.Model):
    _name = 'hr.deduction.history'

    deduction_id = fields.Many2one('hr.deduction', string=' الحسميات')
    employee_id = fields.Many2one('hr.employee', string=' الموظف', required=1)
    action = fields.Char(string='الإجراء')
    reason = fields.Char(string='السبب', required=1,)
    number_decision = fields.Char(string='رقم القرار')
    date_decision = fields.Date(string='تاريخ القرار')


class hrDeductionType(models.Model):
    _name = 'hr.deduction.type'
    _description = u'أنواع الحسميات'

    name = fields.Char(string=' الوصف', required=1)
    code = fields.Char(string='الرمز', required=1)
    type = fields.Selection([('retard_leave', 'تأخير وخروج'), ('absence', 'غياب')], string='النوع', required=1)

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            name = '[%s] %s' % (record.code, record.name)
            result.append((record.id, name))
        return result
