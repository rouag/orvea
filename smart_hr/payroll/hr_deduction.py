# -*- coding: utf-8 -*-

from openerp import models, api, fields, _
from openerp.exceptions import ValidationError
from dateutil import relativedelta
import time as time_date
from datetime import datetime
from openerp.addons.smart_base.util.umalqurra import *
from umalqurra.hijri_date import HijriDate
from umalqurra.hijri import Umalqurra


class HrDeduction(models.Model):
    _name = 'hr.deduction'
    _inherit = ['mail.thread']
    _order = 'id desc'
    _description = u'الحسميات'

    @api.multi
    def get_default_month(self):
        return get_current_month_hijri(HijriDate)

    name = fields.Char(string=' المسمى', required=1, readonly=1, states={'new': [('readonly', 0)]})
    # TODO: get default MONTH
    month = fields.Selection(MONTHS, string='الشهر', required=1, readonly=1, states={'new': [('readonly', 0)]}, default=get_default_month)
    date = fields.Date(string='تاريخ الإنشاء', required=1, default=fields.Datetime.now(), readonly=1, states={'new': [('readonly', 0)]})
    date_from = fields.Date('تاريخ من', readonly=1, states={'new': [('readonly', 0)]})
    date_to = fields.Date('إلى', readonly=1, states={'new': [('readonly', 0)]})
    number_decision = fields.Char(string='رقم القرار', required=1, readonly=1, states={'new': [('readonly', 0)]})
    date_decision = fields.Date(string=' تاريخ القرار', required=1, readonly=1, states={'new': [('readonly', 0)]})
    state = fields.Selection([('new', 'طلب'),
                              ('waiting', 'في إنتظار الإعتماد'),
                              ('cancel', 'مرفوض'),
                              ('done', 'اعتمدت')], string='الحالة', readonly=1, default='new')
    line_ids = fields.One2many('hr.deduction.line', 'deduction_id', string='الحسميات', readonly=1, states={'new': [('readonly', 0)]})
    history_ids = fields.One2many('hr.deduction.history', 'deduction_id', string='سجل التغييرات', readonly=1)
    department_level1_id = fields.Many2one('hr.department', string='الفرع', readonly=1, states={'new': [('readonly', 0)]})
    department_level2_id = fields.Many2one('hr.department', string='القسم', readonly=1, states={'new': [('readonly', 0)]})
    department_level3_id = fields.Many2one('hr.department', string='الشعبة', readonly=1, states={'new': [('readonly', 0)]})
    salary_grid_type_id = fields.Many2one('salary.grid.type', string='الصنف', readonly=1, states={'new': [('readonly', 0)]},)
    employee_ids = fields.Many2many('hr.employee', string='الموظفين', readonly=1, states={'new': [('readonly', 0)]})

    @api.onchange('department_level1_id', 'department_level2_id', 'department_level3_id', 'salary_grid_type_id')
    def onchange_department_level(self):
        dapartment_obj = self.env['hr.department']
        employee_obj = self.env['hr.employee']
        department_level1_id = self.department_level1_id and self.department_level1_id.id or False
        department_level2_id = self.department_level2_id and self.department_level2_id.id or False
        department_level3_id = self.department_level3_id and self.department_level3_id.id or False
        employee_ids = []
        dapartment_id = False
        if department_level3_id:
            dapartment_id = department_level3_id
        elif department_level2_id:
            dapartment_id = department_level2_id
        elif department_level1_id:
            dapartment_id = department_level1_id
        if dapartment_id:
            dapartment = dapartment_obj.browse(dapartment_id)
            employee_ids += [x.id for x in dapartment.member_ids]
            for child in dapartment.all_child_ids:
                employee_ids += [x.id for x in child.member_ids]
        result = {}
        if not employee_ids:
            # get all employee
            employee_ids = employee_obj.search([('employee_state', '=', 'employee')]).ids
        # filter by type
        if self.salary_grid_type_id:
            employee_ids = employee_obj.search([('id', 'in', employee_ids), ('type_id', '=', self.salary_grid_type_id.id)]).ids
        result.update({'domain': {'employee_ids': [('id', 'in', list(set(employee_ids)))]}})
        return result

    @api.onchange('month')
    def onchange_month(self):
        self.name = u'حسميات شهر %s' % self.month

    @api.multi
    def compute_deductions(self):
        self.date_from = get_hijri_month_start(HijriDate, Umalqurra, self.month)
        self.date_to = get_hijri_month_end(HijriDate, Umalqurra, self.month)
        self.name = u'حسميات شهر %s' % self.month
        if self.month:
            line_ids = []
            # delete current line
            self.line_ids.unlink()
            # get حسميات  from الخلاصة الشهرية للغيابات والتأخير
            monthly_summary_obj = self.env['hr.monthly.summary.line']
            deduction_type_obj = self.env['hr.deduction.type']
            domain = [('monthly_summary_id.name', '=', self.month), ('monthly_summary_id.state', '=', 'done')]
            monthly_summarys_retard = monthly_summary_obj.search(domain + [('days_retard', '!=', 0.0)])
            monthly_summarys_absence = monthly_summary_obj.search(domain + [('days_absence', '!=', 0.0)])
            retard_leave_type = deduction_type_obj.search([('type', '=', 'retard_leave')])[0]
            absence_type = deduction_type_obj.search([('type', '=', 'absence')])[0]
            for summary in monthly_summarys_retard + monthly_summarys_absence:
                employee = summary.employee_id
                if employee in self.employee_ids:
                    val = {'deduction_id': self.id,
                           'employee_id': employee.id,
                           'department_id': employee.department_id and employee.department_id.id or False,
                           'job_id': employee.job_id and employee.job_id.id or False,
                           'number': employee.number,
                           'state': 'waiting'}
                    if summary.days_retard:
                        val.update({'amount': summary.days_retard, 'deduction_type_id': retard_leave_type.id})
                        line_ids.append(val)
                    elif summary.days_absence:
                        val_absence = val.copy()
                        val_absence.update({'amount': summary.days_absence, 'deduction_type_id': absence_type.id})
                        line_ids.append(val_absence)
            # العقوبات
            line_ids += self.deduction_sanctions()
            self.line_ids = line_ids

    @api.one
    def action_waiting(self):
        self.state = 'waiting'

    @api.multi
    def action_done(self):
        self.state = 'done'

    @api.one
    def button_refuse(self):
        self.state = 'cancel'

    @api.one
    def action_cancel(self):
        # TODO:
        self.state = 'cancel'
        for line in self.line_ids:
            line.state = 'cancel'

    @api.multi
    def deduction_sanctions(self):
        line_ids = []
        sanction_line_ids = self.env['hr.sanction.ligne'].search([('sanction_id.date_sanction_start', '>=', self.date_from),
                                                                  ('sanction_id.date_sanction_start', '<=', self.date_to),
                                                                  ('sanction_id.type_sanction.deduction', '=', True),
                                                                  ('sanction_id.state', '=', 'done')
                                                                  ])
        deduction_type_obj = self.env['hr.deduction.type']
        sanction_deduction_type = deduction_type_obj.search([('type', '=', 'sanction')], limit=1)
        if sanction_deduction_type:
            for line in sanction_line_ids:
                vals = {'deduction_id': self.id,
                        'employee_id': line.employee_id.id,
                        'department_id': line.employee_id.department_id and line.employee_id.department_id.id or False,
                        'job_id': line.employee_id.job_id and line.employee_id.job_id.id or False,
                        'number': line.employee_id.number,
                        'amount': line.days_number,
                        'deduction_type_id': sanction_deduction_type.id,
                        'state': 'waiting'
                        }
                line_ids.append(vals)
        return line_ids

    @api.multi
    def unlink(self):
        self.ensure_one()
        if self.state != 'new':
            raise ValidationError(u"لا يمكن حذف الحسميات إلا في حالة مسودة أو ملغاه! ")
        return super(HrDeduction, self).unlink()


class HrDeductionLine(models.Model):
    _name = 'hr.deduction.line'

    # TODO: get name
    deduction_id = fields.Many2one('hr.deduction', string=' الحسميات', ondelete='cascade')
    employee_id = fields.Many2one('hr.employee', string='الموظف', required=1)
    number = fields.Char(related='employee_id.number', store=True, readonly=True, string=' رقم الوظيفة')
    job_id = fields.Many2one(related='employee_id.job_id', store=True, readonly=True, string=' الوظيفة')
    department_id = fields.Many2one(related='employee_id.department_id', store=True, readonly=True, string=' الادارة')
    deduction_type_id = fields.Many2one('hr.deduction.type', string='نوع الحسم', required=1)
    amount = fields.Char(string='عدد أيام الحسم', required=1)
    month = fields.Selection(MONTHS, related='deduction_id.month', store=True, readonly=True, string='الشهر')
    hr_sanction_ligne_id = fields.Many2one('hr.sanction.ligne', string='العقوبة')
    # do the store=True
    deduction_state = fields.Selection(related='deduction_id.state', store=True, string='الحالة')
    state = fields.Selection([('waiting', 'في إنتظار الحسم'),
                              ('excluded', 'مستبعد'),
                              ('done', 'تم الحسم'),
                              ('cancel', 'ملغى')], string='الحالة', readonly=1, default='waiting')


class HrDeductionHistory(models.Model):
    _name = 'hr.deduction.history'

    deduction_id = fields.Many2one('hr.deduction', string=' الحسميات', ondelete='cascade')
    employee_id = fields.Many2one('hr.employee', string=' الموظف', required=1)
    action = fields.Char(string='الإجراء')
    reason = fields.Char(string='السبب')
    number_decision = fields.Char(string='رقم القرار')
    date_decision = fields.Date(string='تاريخ القرار')


class HrDeductionType(models.Model):
    _name = 'hr.deduction.type'
    _description = u'أنواع الحسميات'

    name = fields.Char(string=' الوصف', required=1)
    code = fields.Char(string='الرمز', required=1)
    type = fields.Selection([('retard_leave', 'تأخير وخروج'), ('absence', 'غياب'), ('sanction', 'عقوبة')], string='النوع', required=1)

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            name = '[%s] %s' % (record.code, record.name)
            result.append((record.id, name))
        return result
