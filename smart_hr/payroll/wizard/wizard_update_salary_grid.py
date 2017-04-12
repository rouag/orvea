# -*- coding: utf-8 -*-
from openerp import models, fields, api, exceptions, tools, _
from dateutil.relativedelta import relativedelta
from openerp.exceptions import ValidationError
from datetime import date, datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT


class WizardUpdateGrid(models.TransientModel):
    _name = 'wizard.update.grid'

    @api.model
    def default_get(self, fields):
        res = super(WizardUpdateGrid, self).default_get(fields)
        salary_grid_line = self._context.get('active_id', False)
        salary_grid_line_obj = self.env['salary.grid.detail']
        salary_grid_line = salary_grid_line_obj.search([('id', '=', salary_grid_line)], limit=1)
        if salary_grid_line:
            res.update({'grid_id': salary_grid_line.grid_id.id,
                        'type_id': salary_grid_line.type_id.id,
                        'grade_id': salary_grid_line.grade_id.id,
                        'degree_id': salary_grid_line.degree_id.id,
                        'basic_salary': salary_grid_line.basic_salary,
                        'retirement': salary_grid_line.retirement,
                        'retirement_amount': salary_grid_line.retirement_amount,
                        'insurance': salary_grid_line.insurance,
                        'insurance_type': salary_grid_line.insurance_type.id,
                        'net_salary': salary_grid_line.net_salary,
                        'increase': salary_grid_line.increase,
                        'transport_allowance_amout': salary_grid_line.transport_allowance_amout,

                        'new_basic_salary': salary_grid_line.basic_salary,
                        'new_retirement': salary_grid_line.retirement,
                        'new_retirement_amount': salary_grid_line.retirement_amount,
                        'new_insurance': salary_grid_line.insurance,
                        'new_net_salary': salary_grid_line.net_salary,
                        'new_insurance_type': salary_grid_line.insurance_type.id,
                        'new_net_salary': salary_grid_line.net_salary,
                        'new_increase': salary_grid_line.increase,
                        })
        return res

    grid_id = fields.Many2one('salary.grid', string='سلّم الرواتب', required=1, ondelete='cascade')
    date = fields.Date(string='التاريخ', default=fields.Date.today())
    type_id = fields.Many2one('salary.grid.type', string='نوع السلم', required=1, readonly=1)
    grade_id = fields.Many2one('salary.grid.grade', string='المرتبة', required=1, readonly=1)
    new_grade_name = fields.Char(string='مسمى المرتبة الجديد')
    degree_id = fields.Many2one('salary.grid.degree', string='الدرجة', required=1, readonly=1)

    allowance_ids = fields.One2many('wiz.grid.detail.allowance', 'grid_detail_id', string='البدلات')
    # old values
    basic_salary = fields.Float(string='الراتب الأساسي', required=1, readonly=1)
    retirement = fields.Float(string='نسبة المحسوم للتقاعد', readonly=1)
    retirement_amount = fields.Float(string='المبلغ المحسوم للتقاعد', readonly=1, compute='_compute_retirement_amount', store=True)
    insurance = fields.Float(string='نسبة  التأمين', readonly=1)
    insurance_type = fields.Many2one('hr.insurance.type', string=u'نوع التأمين', readonly=1)
    increase = fields.Float(string='العلاوة', readonly=1)
    net_salary = fields.Float(string='صافي الراتب', readonly=1, compute='_compute_net_salary', store=True)
    # new values
    new_basic_salary = fields.Float(string='الراتب الأساسي', required=1)
    new_retirement = fields.Float(string='نسبة المحسوم للتقاعد')
    new_retirement_amount = fields.Float(string='المبلغ المحسوم للتقاعد', compute='_compute_new_retirement_amount', store=True)
    new_insurance = fields.Float(string='نسبة  التأمين')
    new_insurance_type = fields.Many2one('hr.insurance.type', string=u'نوع التأمين')
    new_increase = fields.Float(string='العلاوة',)
    new_net_salary = fields.Float(string='صافي الراتب', readonly=1, compute='_compute_new_net_salary', store=True)

    transport_allowance_amout = fields.Float(string='مبلغ بدل النقل', readonly=1, compute='_compute_transport_allowance_amout', store=True)

    @api.multi
    @api.depends('new_basic_salary', 'new_retirement')
    def _compute_new_retirement_amount(self):
        for rec in self:
            retirement = rec.new_basic_salary * rec.new_retirement / 100.0
            rec.new_retirement_amount = retirement

    @api.multi
    @api.depends('allowance_ids')
    def _compute_transport_allowance_amout(self):
        transport_allowance = self.env.ref('smart_hr.hr_allowance_type_01')
        for rec in self:
            transport_allowance_amout = 0.0
            for allowance in rec.allowance_ids:
                amount = allowance.get_value(False)
                if transport_allowance == allowance.allowance_id:
                    transport_allowance_amout = amount
            rec.transport_allowance_amout = transport_allowance_amout

    @api.multi
    @api.depends('allowance_ids', 'new_basic_salary', 'new_retirement', 'new_insurance')
    def _compute_new_net_salary(self):
        for rec in self:
            net_salary = rec.new_basic_salary
            for allowance in rec.allowance_ids:
                amount = allowance.get_value(False)
                net_salary += amount
            # deductions
            insurance = rec.new_basic_salary * rec.new_insurance / 100.0
            net_salary -= rec.new_retirement_amount
            net_salary -= insurance
            rec.new_net_salary = net_salary

    @api.onchange('type_id')
    def onchange_type_id(self):
        salary_grid_line = self._context.get('active_id', False)
        salary_grid_line_obj = self.env['salary.grid.detail']
        salary_grid_line = salary_grid_line_obj.search([('id', '=', salary_grid_line)], limit=1)
        if self.type_id and salary_grid_line:
            allowance_ids = []
            for rec in salary_grid_line.allowance_ids:
                allowance_ids.append({'grid_detail_id': self.id,
                                      'allowance_id': rec.allowance_id.id,
                                      'compute_method': rec.compute_method,
                                      'amount': rec.amount
                                      })
            self.allowance_ids = allowance_ids

    @api.multi
    def action_salary_grid_line(self):
        salary_grid_line = self._context.get('active_id', False)
        salary_grid_line_obj = self.env['salary.grid.detail']
        salary_grid_line = salary_grid_line_obj.search([('id', '=', salary_grid_line)], limit=1)
        # make a copy of salary grid detail 
        old_salary_grid_line = salary_grid_line.copy()
        old_salary_grid_line.allowance_ids = salary_grid_line.allowance_ids.ids
        old_salary_grid_line.is_old = True
        # update salary_grid_line with new values
        salary_grid_line.basic_salary = self.new_basic_salary
        salary_grid_line.increase = self.new_increase
        salary_grid_line.retirement = self.new_retirement
        salary_grid_line.retirement_amount = self.new_retirement_amount
        salary_grid_line.insurance_type = self.new_insurance_type.id
        salary_grid_line.insurance = self.new_insurance
        salary_grid_line.net_salary = self.new_net_salary
        salary_grid_line.date = fields.Date.today()
        # update allowance, increase, indemnity
        allowance_ids = []
        for rec in self.allowance_ids:
            allowance_ids.append({'grid_detail_id': salary_grid_line.id,
                                  'allowance_id': rec.allowance_id.id,
                                  'compute_method': rec.compute_method,
                                  'amount': rec.amount
                                  })
        salary_grid_line.allowance_ids = allowance_ids
        # change the grade name
        if self.new_grade_name:
            old_grade_name = self.grade_id.name
            self.grade_id.name = self.new_grade_name
            # get all jobs with same grade_id
            job_ids = self.env['hr.job'].search([('grade_id', '=', self.grade_id.id)])
            for job in job_ids:
                job_history_vals = {
                    'action': u'تغير مسمى المرتبة من ' + old_grade_name + u' إلى ' + self.new_grade_name,
                    'action_date': date.today(),
                    'description': u'تغير مسمى المرتبة',
                    'job_id': job.id,
                }
                self.env['hr.job.history.actions'].create(job_history_vals)
            # get all employees with same grade_id
            employee_ids = self.env['hr.employee'].search([('grade_id', '=', self.grade_id.id)])
            for employee in employee_ids:
                emp_history_vals = {'employee_id': employee.id,
                                    'date': fields.Datetime.now(),
                                    'type': u'تغير مسمى المرتبة من ' + old_grade_name + u' إلى ' + self.new_grade_name,
                                    'operation_type': '14',
                                    'job_id': employee.job_id.name.name,
                                    'grade_id': employee.job_id.grade_id.id,
                                    'number': employee.job_id.number,
                                    'department_id': employee.department_id.id,
                                    'dep_side': employee.user_id.company_id.name,
                                    }
                self.env['hr.employee.history'].create(emp_history_vals)


class SalaryGridDetailAllowance(models.TransientModel):
    _name = 'wiz.grid.detail.allowance'

    grid_detail_id = fields.Many2one('wizard.update.grid', string='تفاصيل سلم الرواتب', ondelete='cascade')
    allowance_id = fields.Many2one('hr.allowance.type', string='البدل', required=1)
    compute_method = fields.Selection([('amount', 'مبلغ'),
                                       ('percentage', 'نسبة من الراتب الأساسي'),
                                       ('formula_1', 'نسبة‬ البدل‬ * راتب‬  الدرجة‬ الاولى‬  من‬ المرتبة‬  التي‬ يشغلها‬ الموظف‬'),
                                       ('formula_2', 'نسبة‬ البدل‬ * راتب‬  الدرجة‬ التي ‬ يشغلها‬ الموظف‬'),
                                       ('job_location', 'تحتسب  حسب مكان العمل')], required=1, string='طريقة الإحتساب')
    amount = fields.Float(string='المبلغ')
    min_amount = fields.Float(string='الحد الأدنى')
    percentage = fields.Float(string='النسبة')
    line_ids = fields.One2many('salary.grid.detail.allowance.city', 'allowance_id', string='النسب حسب المدينة')

    @api.model
    def get_value(self, employee_id):
        allowance_city_obj = self.env['salary.grid.detail.allowance.city']
        degree_obj = self.env['salary.grid.degree']
        salary_grid_obj = self.env['wizard.update.grid']
        # employee info
        employee = self.env['hr.employee'].browse(employee_id)
        ttype = employee.job_id.type_id
        grade = employee.job_id.grade_id
        degree = employee.degree_id
        amount = 0.0
        # search the correct salary_grid for this employee
        if employee_id:
            salary_grids, basic_salary = employee.get_salary_grid_id(False)
            if not salary_grids:
                raise ValidationError(_(u'لا يوجد سلم رواتب لأحد الموظفين. !'))
        else:
            salary_grids = self.grid_detail_id
            basic_salary = salary_grids.basic_salary
        # compute
        if self.compute_method == 'amount':
            amount = self.amount
        if self.compute_method == 'percentage':
            amount = self.percentage * basic_salary / 100.0
        if self.compute_method == 'job_location' and employee and employee.dep_city:
            citys = allowance_city_obj.search([('allowance_id', '=', self.id), ('city_id', '=', employee.dep_city.id)])
            if citys:
                amount = citys[0].percentage * basic_salary / 100.0
        if self.compute_method == 'formula_1':
            # get first degree for the grade
            degrees = degree_obj.search([('grade_id', '=', grade.id)])
            if degrees:
                salary_grids = salary_grid_obj.search([('type_id', '=', ttype.id), ('grade_id', '=', grade.id), ('degree_id', '=', degrees[0].id)])
                if salary_grids:
                    amount = salary_grids[0].basic_salary * self.percentage / 100.0
        if self.compute_method == 'formula_2':
            amount = self.percentage * basic_salary / 100.0
        if self.min_amount and amount < self.min_amount:
            amount = self.min_amount
        return amount


