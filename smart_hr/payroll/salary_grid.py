# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-
from openerp.exceptions import UserError
from openerp import models, fields, api, _
from openerp.exceptions import Warning
from dateutil.relativedelta import relativedelta
from openerp.exceptions import ValidationError
from datetime import date, datetime, timedelta


class SalaryGrid(models.Model):
    _name = 'salary.grid'
    _inherit = ['mail.thread']
    _description = u'سلّم الرواتب'

    name = fields.Char(string='الإسم', required=1)
    numero_order = fields.Char(string='رقم القرار')
    date = fields.Date(string='التاريخ')
    enabled = fields.Boolean(string='مفعل')
    grid_ids = fields.One2many('salary.grid.detail', 'grid_id')
    state = fields.Selection([('draft', 'مسودة'),
                              ('verify', 'في إنتظار الإعتماد'),
                              ('done', 'اعتمدت'),
                              ('refused', 'مرفوضة'),
                              ], 'الحالة', default='draft')

    @api.multi
    def action_verify(self):
        self.state = 'verify'

    @api.multi
    def action_done(self):
        self.state = 'done'

    @api.multi
    def action_refuse(self):
        self.state = 'refused'


class SalaryGridType(models.Model):
    _name = 'salary.grid.type'
    _description = u' الأصناف'

    name = fields.Char(string='الصنف', required=1)
    code = fields.Integer(string='الرمز')
    is_member = fields.Boolean(string='صنف أعضاء')
    grid_id = fields.Many2one('salary.grid', string='سلّم الرواتب')
    basic_salary = fields.Float(string='الراتب الأساسي')
    allowance_ids = fields.Many2many('hr.allowance.type', string=u'البدلات')
    far_age = fields.Float(string=' السن الاقصى')
    code = fields.Char(string='الرمز')
    reward_ids = fields.Many2many('hr.reward.type', string=u'المكافآت‬')
    retrait_monthly = fields.Integer(string='نسبة الحسم الشهري على التقاعد:')
    assurance_monthly = fields.Integer(string='نسبة التامين الشهري  من الراتب الاساسي:')
    salary_recent = fields.Float(string=' أخر راتب شهري')
    passing_score = fields.Float(string=u'المجموع المطلوبة للتعين')


class SalaryGridGrade(models.Model):
    _name = 'salary.grid.grade'
    _description = u'المراتب'

    name = fields.Char(string='المسمى', required=1)
    code = fields.Char(string='الرمز')
    job_create_id = fields.Many2one('hr.job.create', string=' وظائف')
    job_strip_from_id = fields.Many2one('hr.job.strip.from', string=' وظائف')
    years_job = fields.Integer(string='مدة استحقاق المرتبة')


class SalaryGridDegree(models.Model):
    _name = 'salary.grid.degree'
    _order = 'sequence'
    _description = u'الدرجة'

    name = fields.Char(string='المسمى', required=1)
    code = fields.Char(string='الرمز')
    grade_id = fields.Many2one('salary.grid.grade', string='المرتبة')
    sequence = fields.Integer(string='الترتيب')

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            name = '[%s] %s' % (record.code, record.name)
            result.append((record.id, name))
        return result


class SalaryGridDetail(models.Model):
    _name = 'salary.grid.detail'
    _description = u'تفاصيل سلم الرواتب'
    _rec_name = 'grid_id'

    @api.multi
    def get_default_date(self):
        return self.grid_id.date

    grid_id = fields.Many2one('salary.grid', string='سلّم الرواتب', required=1, ondelete='cascade')
    date = fields.Date(string='التاريخ')
    type_id = fields.Many2one('salary.grid.type', string='الصنف', required=1)
    grade_id = fields.Many2one('salary.grid.grade', string='المرتبة', required=1)
    degree_id = fields.Many2one('salary.grid.degree', string='الدرجة', required=1)
    basic_salary = fields.Float(string='الراتب الأساسي', required=1)
    retirement = fields.Float(string='نسبة المحسوم للتقاعد')
    insurance = fields.Float(string='نسبة  التأمين')
    net_salary = fields.Float(string='صافي الراتب', readonly=1, compute='_compute_net_salary')
    allowance_ids = fields.One2many('salary.grid.detail.allowance', 'grid_detail_id', string='البدلات')
    reward_ids = fields.One2many('salary.grid.detail.reward', 'grid_detail_id', string='المكافآت‬')
    indemnity_ids = fields.One2many('salary.grid.detail.indemnity', 'grid_detail_id', string='التعويضات')
    insurance_type = fields.Many2one('hr.insurance.type', string=u'نوع التأمين')
    reward = fields.Float(string='العلاوة')

    @api.multi
    @api.depends('allowance_ids', 'reward_ids', 'indemnity_ids', 'basic_salary', 'retirement', 'insurance', 'retirement')
    def _compute_net_salary(self):
        for rec in self:
            net_salary = rec.basic_salary
            for allowance in rec.allowance_ids:
                net_salary += allowance.get_value(False)
            for reward in rec.reward_ids:
                net_salary += reward.get_value(False)
            for indemnity in rec.indemnity_ids:
                net_salary += indemnity.get_value(False)
            # deductions
            retirement = rec.basic_salary * rec.retirement / 100.0
            insurance = rec.basic_salary * rec.insurance / 100.0
            net_salary -= retirement
            net_salary -= insurance
            rec.net_salary = net_salary

    @api.model
    def create(self, vals):
        res = super(SalaryGridDetail, self).create(vals)
        res.write({'date': res.grid_id.date})
        return res


class SalaryGridDetailAllowance(models.Model):
    _name = 'salary.grid.detail.allowance'

    grid_detail_id = fields.Many2one('salary.grid.detail', string='تفاصيل سلم الرواتب', ondelete='cascade')
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
        salary_grid_obj = self.env['salary.grid.detail']
        # employee info
        employee = self.env['hr.employee'].browse(employee_id)
        ttype = employee.job_id.type_id
        grade = employee.job_id.grade_id
        degree = employee.degree_id
        amount = 0.0
        # search the correct salary_grid for this employee
        if employee_id:
            salary_grids = employee.get_salary_grid_id(False)
            if not salary_grids:
                raise ValidationError(_(u'للا يوجد سلم رواتب لأحد الموظفين. !'))
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


class SalaryGridDetailAllowanceCity(models.Model):
    _name = 'salary.grid.detail.allowance.city'

    allowance_id = fields.Many2one('salary.grid.detail.allowance', string='البدل', ondelete='cascade')
    city_id = fields.Many2one('res.city', string='المدينة', required=1)
    percentage = fields.Float(string='النسبة', required=1)


class SalaryGridDetailReward(models.Model):
    _name = 'salary.grid.detail.reward'

    grid_detail_id = fields.Many2one('salary.grid.detail', string='تفاصيل سلم الرواتب', ondelete='cascade')
    reward_id = fields.Many2one('hr.reward.type', string='المكافأة', required=1)
    compute_method = fields.Selection([('amount', 'مبلغ'),
                                       ('percentage', 'نسبة من الراتب الأساسي'),
                                       ('formula_1', 'نسبة‬ البدل‬ * راتب‬  الدرجة‬ الاولى‬  من‬ المرتبة‬  التي‬ يشغلها‬ الموظف‬'),
                                       ('formula_2', 'نسبة‬ البدل‬ * راتب‬  الدرجة‬ التي ‬ يشغلها‬ الموظف‬'),
                                       ('job_location', 'تحتسب  حسب مكان العمل')], required=1, string='طريقة الإحتساب')
    amount = fields.Float(string='المبلغ')
    min_amount = fields.Float(string='الحد الأدنى')
    percentage = fields.Float(string='النسبة')
    line_ids = fields.One2many('salary.grid.detail.reward.city', 'reward_id', string='النسب حسب المدينة')

    @api.model
    def get_value(self, employee_id):
        allowance_city_obj = self.env['salary.grid.detail.reward.city']
        degree_obj = self.env['salary.grid.degree']
        salary_grid_obj = self.env['salary.grid.detail']
        # employee info
        employee = self.env['hr.employee'].browse(employee_id)
        ttype = employee.job_id.type_id
        grade = employee.job_id.grade_id
        degree = employee.degree_id
        amount = 0.0
        # search the correct salary_grid for this employee
        if employee_id:
            salary_grids = employee.get_salary_grid_id(False)
            if not salary_grids:
                raise ValidationError(_(u'للا يوجد سلم رواتب لأحد الموظفين. !'))
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


class SalaryGridDetailRewardCity(models.Model):
    _name = 'salary.grid.detail.reward.city'

    reward_id = fields.Many2one('salary.grid.detail.reward', string='البدل', ondelete='cascade')
    city_id = fields.Many2one('res.city', string='المدينة', required=1)
    percentage = fields.Float(string='النسبة', required=1)


class SalaryGridDetailIndemnity(models.Model):
    _name = 'salary.grid.detail.indemnity'

    grid_detail_id = fields.Many2one('salary.grid.detail', string='تفاصيل سلم الرواتب', ondelete='cascade')
    indemnity_id = fields.Many2one('hr.indemnity.type', string='التعويض', required=1)
    compute_method = fields.Selection([('amount', 'مبلغ'),
                                       ('percentage', 'نسبة من الراتب الأساسي'),
                                       ('formula_1', 'نسبة‬ البدل‬ * راتب‬  الدرجة‬ الاولى‬  من‬ المرتبة‬  التي‬ يشغلها‬ الموظف‬'),
                                       ('formula_2', 'نسبة‬ البدل‬ * راتب‬  الدرجة‬ التي ‬ يشغلها‬ الموظف‬'),
                                       ('job_location', 'تحتسب  حسب مكان العمل')], required=1, string='طريقة الإحتساب')
    amount = fields.Float(string='المبلغ')
    min_amount = fields.Float(string='الحد الأدنى')
    percentage = fields.Float(string='النسبة')
    line_ids = fields.One2many('salary.grid.detail.indemnity.city', 'indemnity_id', string='النسب حسب المدينة')

    @api.model
    def get_value(self, employee_id):
        allowance_city_obj = self.env['salary.grid.detail.indemnity.city']
        degree_obj = self.env['salary.grid.degree']
        salary_grid_obj = self.env['salary.grid.detail']
        # employee info
        employee = self.env['hr.employee'].browse(employee_id)
        ttype = employee.job_id.type_id
        grade = employee.job_id.grade_id
        degree = employee.degree_id
        amount = 0.0
        # search the correct salary_grid for this employee
        if employee_id:
            salary_grids = employee.get_salary_grid_id(False)
            if not salary_grids:
                raise ValidationError(_(u'للا يوجد سلم رواتب لأحد الموظفين. !'))
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


class SalaryGridDetailIndemnityCity(models.Model):
    _name = 'salary.grid.detail.indemnity.city'

    indemnity_id = fields.Many2one('salary.grid.detail.indemnity', string='البدل', ondelete='cascade')
    city_id = fields.Many2one('res.city', string='المدينة', required=1)
    percentage = fields.Float(string='النسبة', required=1)
