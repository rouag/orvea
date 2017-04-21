# -*- coding: utf-8 -*-
from openerp import models, fields, api, exceptions, tools 
from openerp import api, fields, models, _
from dateutil.relativedelta import relativedelta
from openerp.exceptions import ValidationError
from datetime import date, datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT


class TransfertBenefitsWizard(models.TransientModel):
    _name = 'transfert.benefits.wizard'

    @api.model
    def default_get(self, fields):
        res = super(TransfertBenefitsWizard, self).default_get(fields)
        transfert_line = self._context.get('active_id', False)
        transfert_line_obj = self.env['hr.transfert.sorting.line4']
        transfert = transfert_line_obj.search([('id', '=', transfert_line)], limit=1)
        location_allowance_ids = []
        job_allowance_ids = []
        transfert_allowance_ids = []
        if transfert:
            # fill location_allowance_ids
            if not transfert.hr_employee_transfert_id.location_allowance_ids:
                for rec in transfert.new_department_id.dep_side.allowance_ids:
                    location_allowance_ids.append({'location_decision_appoint_id': transfert.id,
                                                   'allowance_id': rec.allowance_id.id,
                                                   'compute_method': 'amount',
                                                   'amount': 0.0})
            else:
                for rec in transfert.hr_employee_transfert_id.location_allowance_ids:
                    location_allowance_ids.append({'location_decision_appoint_id': transfert.id,
                                                   'allowance_id': rec.allowance_id.id,
                                                   'compute_method': rec.compute_method,
                                                   'amount': rec.amount})
            # fill job_allowance_ids
            if not transfert.hr_employee_transfert_id.job_allowance_ids:
                for rec in transfert.new_job_id.serie_id.allowanse_ids:
                    job_allowance_ids.append({'decision_appoint_id': transfert.id,
                                              'allowance_id': rec.id,
                                              'compute_method': 'amount',
                                              'amount': 0.0})
            else:
                for rec in transfert.hr_employee_transfert_id.job_allowance_ids:
                    job_allowance_ids.append({'job_transfert_id': transfert.id,
                                              'allowance_id': rec.allowance_id.id,
                                              'compute_method': rec.compute_method,
                                              'amount': rec.amount})
            # fill transfert_allowance_ids
            if transfert.hr_employee_transfert_id.transfert_allowance_ids:
                for rec in transfert.new_job_id.serie_id.allowanse_ids:
                    transfert_allowance_ids.append({'transfert_id': transfert.id,
                                                    'allowance_id': rec.id,
                                                    'compute_method': rec.compute_method,
                                                    'amount': rec.amount})
            res.update({'transfert_line_obj': transfert.id,
                        'job_id': transfert.new_job_id.id,
                        'specific_id': transfert.new_job_id.specific_id.id,
                        'type_id': transfert.new_type_id.id,
                        'department_id': transfert.new_department_id.id,
                        'degree_id': transfert.new_degree_id.id,
                        'grade_id': transfert.new_job_id.grade_id.id,
                        'employee_id': transfert.hr_employee_transfert_id.employee_id.id,
                        'location_allowance_ids': [(0, 0, elem) for elem in location_allowance_ids],
                        'job_allowance_ids': [(0, 0, elem) for elem in job_allowance_ids],
                        'transfert_allowance_ids': [(0, 0, elem) for elem in transfert_allowance_ids],
                        })
        return res

    transfert_line_obj = fields.Many2one('hr.transfert.sorting.line4', string=u'طلب نقل موظف')
    employee_id = fields.Many2one('hr.employee', readonly=1, string=u'الموظف')
    degree_id = fields.Many2one('salary.grid.degree', string=u'الدرجة', readonly=1)
    grade_id = grade_id = fields.Many2one('salary.grid.grade', string=u'المرتبة', readonly=1)
    department_id = fields.Many2one('hr.department', string='مقر الوظيفة', readonly=1)
    job_id = fields.Many2one('hr.job', string=u'الوظيفة', readonly=1)
    specific_id = fields.Many2one('hr.groupe.job', string=u'المجموعة النوعية', readonly=1)
    type_id = fields.Many2one('salary.grid.type', string=u'الصنف', readonly=1)
    job_allowance_ids = fields.One2many('transfert.appoint.allowance', 'job_transfert_id', string=u'بدلات الوظيفة')
    transfert_allowance_ids = fields.One2many('transfert.appoint.allowance', 'transfert_id', string=u'بدلات النقل')
    location_allowance_ids = fields.One2many('transfert.appoint.allowance', 'location_transfert_id', string=u'بدلات المنطقة')

    @api.multi
    def action_transfert(self):
        self.transfert_line_obj.hr_employee_transfert_id.location_allowance_ids.unlink()
        self.transfert_line_obj.hr_employee_transfert_id.job_allowance_ids.unlink()
        self.transfert_line_obj.hr_employee_transfert_id.transfert_allowance_ids.unlink()
        job_allowance_ids = []
        for rec in self.job_allowance_ids:
            job_allowance_ids.append({'job_transfert_id': self.transfert_line_obj.hr_employee_transfert_id.id,
                                      'allowance_id': rec.allowance_id.id,
                                      'compute_method': rec.compute_method,
                                      'amount': rec.amount
                                      })
        self.transfert_line_obj.hr_employee_transfert_id.job_allowance_ids = job_allowance_ids
        transfert_allowance_ids = []
        for rec in self.transfert_allowance_ids:
            job_allowance_ids.append({'transfert_id': self.transfert_line_obj.hr_employee_transfert_id.id,
                                      'allowance_id': rec.allowance_id.id,
                                      'compute_method': rec.compute_method,
                                      'amount': rec.amount
                                      })
        self.transfert_line_obj.hr_employee_transfert_id.transfert_allowance_ids = transfert_allowance_ids
        location_allowance_ids = []
        for rec in self.location_allowance_ids:
            location_allowance_ids.append({'location_transfert_id': self.transfert_line_obj.hr_employee_transfert_id.id,
                                           'allowance_id': rec.allowance_id.id,
                                           'compute_method': rec.compute_method,
                                           'amount': rec.amount
                                           })
        self.transfert_line_obj.hr_employee_transfert_id.location_allowance_ids = location_allowance_ids


class TransfertAppointAllowance(models.TransientModel):
    _name = 'transfert.appoint.allowance'
    _description = u'بدلات'

    job_transfert_id = fields.Many2one('transfert.benefits.wizard', string='النقل', ondelete='cascade')
    transfert_id = fields.Many2one('transfert.benefits.wizard', string='النقل', ondelete='cascade')
    location_transfert_id = fields.Many2one('transfert.benefits.wizard', string='النقل', ondelete='cascade')
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

    def get_salary_grid_id(self, employee_id, type_id, grade_id, degree_id, operation_date):
        '''
        @return:  two values value1: salary grid detail, value2: basic salary
        '''
        # search for  the newest salary grid detail
        domain = [('grid_id.state', '=', 'done'),
                  ('grid_id.enabled', '=', True),
                  ('type_id', '=', type_id.id),
                  ('grade_id', '=', grade_id.id),
                  ('degree_id', '=', degree_id.id)
                  ]
        if operation_date:
            # search the right salary grid detail for the given operation_date
            domain.append(('date', '<=', operation_date))
        salary_grid_id = self.env['salary.grid.detail'].search(domain, order='date desc', limit=1)
        if not salary_grid_id:
            # doamin for  the newest salary grid detail
            if len(domain) == 6:
                domain.pop(5)
            salary_grid_id = self.env['salary.grid.detail'].search(domain, order='date desc', limit=1)
        # retreive old salary increases to add them with basic_salary
        domain = [('salary_grid_detail_id', '=', salary_grid_id.id)]
        if operation_date:
            domain.append(('date', '<=', operation_date))
        salary_increase_ids = self.env['employee.increase'].search(domain)
        sum_increases_amount = 0.0
        for rec in salary_increase_ids:
            sum_increases_amount += rec.amount
        if employee_id.basic_salary == 0:
            basic_salary = salary_grid_id.basic_salary + sum_increases_amount
        else:
            basic_salary = employee_id.basic_salary + sum_increases_amount
        return salary_grid_id, basic_salary

    @api.onchange('compute_method', 'amount', 'percentage')
    def onchange_get_value(self):
        allowance_city_obj = self.env['salary.grid.detail.allowance.city']
        degree_obj = self.env['salary.grid.degree']
        salary_grid_obj = self.env['salary.grid.detail']
        # employee info
        transfert_id = self.job_transfert_id
        if self.transfert_id:
            transfert_id = self.transfert_id
        if self.location_transfert_id:
            transfert_id = self.location_transfert_id

        employee = transfert_id.employee_id
        ttype = transfert_id.type_id
        grade = transfert_id.grade_id
        degree = transfert_id.degree_id
        amount = 0.0
        # search the correct salary_grid for this employee
        salary_grids, basic_salary = self.get_salary_grid_id(employee, ttype, grade, degree, False)
        print ttype, grade, degree
        print salary_grids
        if not salary_grids:
            raise ValidationError(_(u'لا يوجد سلم رواتب للموظف. !'))
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
        self.amount = amount

