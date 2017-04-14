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
    grid_ids = fields.One2many('salary.grid.detail', 'grid_id', domain=[('is_old', '=', False)])
    attachments = fields.Many2many('ir.attachment', string=u"المرفقات")
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
    def button_refuse(self):
        self.state = 'refused'


class SalaryGridType(models.Model):
    _name = 'salary.grid.type'
    _description = u' الأصناف'

    name = fields.Char(string='نوع السلم', required=1)
    code = fields.Integer(string='الرمز')
    is_member = fields.Boolean(string='صنف أعضاء')
    grid_id = fields.Many2one('salary.grid', string='سلّم الرواتب')
    basic_salary = fields.Float(string='الراتب الأساسي')
    allowance_ids = fields.Many2many('hr.allowance.type', string=u'البدلات')
    far_age = fields.Float(string=' السن الاقصى')
    code = fields.Char(string='الرمز')
    retrait_monthly = fields.Integer(string='نسبة الحسم الشهري على التقاعد:')
    assurance_monthly = fields.Integer(string='نسبة التامين الشهري  من الراتب الاساسي:')
    salary_recent = fields.Float(string=' أخر راتب شهري')
    passing_score = fields.Float(string=u'المجموع المطلوبة لاتعين')


class SalaryGridGrade(models.Model):
    _name = 'salary.grid.grade'
    _inherit = ['mail.thread']
    _description = u'المراتب'

    name = fields.Char(string='المسمى', required=1, track_visibility='onchange')
    code = fields.Char(string='الرمز')
    job_create_id = fields.Many2one('hr.job.create', string=' وظائف')
    job_strip_from_id = fields.Many2one('hr.job.strip.from', string=' وظائف')
    years_job = fields.Integer(string='استحقاق مدة الترقية')


class SalaryGridDegree(models.Model):
    _name = 'salary.grid.degree'
    _order = 'sequence'
    _description = u'الدرجة'

    name = fields.Char(string='المسمى', required=1)
    code = fields.Char(string='الرمز')
    grade_id = fields.Many2one('salary.grid.grade', string='المرتبة')
    sequence = fields.Integer(string='الترتيب')


class SalaryGridDetail(models.Model):
    _name = 'salary.grid.detail'
    _description = u'تفاصيل سلم الرواتب'
    _rec_name = 'grid_id'

    @api.multi
    def get_default_date(self):
        return self.grid_id.date

    grid_id = fields.Many2one('salary.grid', string='سلّم الرواتب', required=1, ondelete='cascade')
    date = fields.Date(string='التاريخ')
    type_id = fields.Many2one('salary.grid.type', string='نوع السلم', required=1)
    grade_id = fields.Many2one('salary.grid.grade', string='المرتبة', required=1)
    degree_id = fields.Many2one('salary.grid.degree', string='الدرجة', required=1)
    basic_salary = fields.Float(string='الراتب الأساسي', required=1)
    retirement = fields.Float(string='نسبة المحسوم للتقاعد')
    retirement_amount = fields.Float(string='المبلغ المحسوم للتقاعد', readonly=1, compute='_compute_retirement_amount', store=True)
    insurance = fields.Float(string='نسبة  التأمين')
    net_salary = fields.Float(string='صافي الراتب', readonly=1, compute='_compute_net_salary', store=True)
    allowance_ids = fields.One2many('salary.grid.detail.allowance', 'grid_detail_id', string='البدلات')
    insurance_type = fields.Many2one('hr.insurance.type', string=u'نوع التأمين')
    increase = fields.Float(string='العلاوة')
    transport_allowance_amout = fields.Float(string='مبلغ بدل النقل', readonly=1, compute='_compute_transport_allowance_amout', store=True)
    is_old = fields.Boolean(string='غير ساري المفعول', default=False)

    @api.multi
    @api.depends('basic_salary', 'retirement')
    def _compute_retirement_amount(self):
        for rec in self:
            retirement = rec.basic_salary * rec.retirement / 100.0
            rec.retirement_amount = retirement

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
    @api.depends('allowance_ids', 'basic_salary', 'retirement', 'insurance')
    def _compute_net_salary(self):
        for rec in self:
            net_salary = rec.basic_salary
            for allowance in rec.allowance_ids:
                amount = allowance.get_value(False)
                net_salary += amount
            # deductions
            insurance = rec.basic_salary * rec.insurance / 100.0
            net_salary -= rec.retirement_amount
            net_salary -= insurance
            rec.net_salary = net_salary

    @api.model
    def create(self, vals):
        res = super(SalaryGridDetail, self).create(vals)
        res.write({'date': res.grid_id.date})
        return res

    @api.multi
    def hide_line(self):
        self.ensure_one()
        count_mployee = self.env['hr.employee'].search_count([('type_id', '=', self.type_id.id),
                                                              ('grade_id', '=', self.grade_id.id),
                                                              ('degree_id', '=', self.degree_id.id)])
        if count_mployee:
            raise ValidationError(_(u'لا يمكن الحذف في حالة إرتباط السلم بموظف!'))
        else:
            self.is_old = True


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


class SalaryGridDetailAllowanceCity(models.Model):
    _name = 'salary.grid.detail.allowance.city'

    allowance_id = fields.Many2one('salary.grid.detail.allowance', string='البدل', ondelete='cascade')
    city_id = fields.Many2one('res.city', string='المدينة', required=1)
    percentage = fields.Float(string='النسبة', required=1)
