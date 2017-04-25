# -*- coding: utf-8 -*-

from openerp import models, api, fields, _
from openerp.exceptions import ValidationError
from openerp.exceptions import UserError
from datetime import date, datetime, timedelta
from openerp.addons.smart_base.util.umalqurra import *
from umalqurra.hijri_date import HijriDate
from umalqurra.hijri import Umalqurra
from pychart.arrow import default


class hrIncrease(models.Model):
    _name = 'hr.increase'
    _inherit = ['mail.thread']
    _order = 'id desc'
    _description = u'العلاوة'

#     @api.multi
#     def get_default_date(self):
#         # get end date of month 01
#         date = get_hijri_month_end(HijriDate, Umalqurra, '01')
#         if fields.date.today() > date:
#             raise ValidationError(u"لا يمكن إنشاء علاوات بعد نهاية شهر محرّم! ")
#         else:
#             return fields.date.today()

    name = fields.Char(string=' المسمى', readonly=1, states={'new': [('readonly', 0)]})
    number_decision = fields.Char(string='رقم القرار')
    date_decision = fields.Date(string=' تاريخ القرار')
    periode_increase = fields.Many2one('hr.periode.increase', string=u'فترة العلاوة', required=1)
    
    date = fields.Date(string='تاريخ الطلب',default=fields.Datetime.now(), readonly=1)
    employee_deprivated_ids = fields.One2many('hr.employee.deprivation', 'increase_id', string=u'الموظفين المستثنين من العلاوة', required=1)
    employee_increase_ids = fields.One2many('hr.employee.increase.percent', 'increase_id', string=u'الموظفين المستحقين للعلاوة  ', required=1)
    employee_errors_ids = fields.One2many('hr.employee.increase.error', 'increase_id', string=u'الموظفين لديهم أخطاء   ', required=1)
    state = fields.Selection([('draft', u'طلب'),
                              ('pim', u'المصاقة على الموظفين المستثنين من العلاوة '),
                              ('hrm', u'مدير شؤون الموظفين'),
                              ('pim2', u'المصاقة على نسب العلاوة '),
                              ('done', u'اعتمدت'),
                              ], string='الحالة', readonly=1, default='draft')
    note = fields.Text(string='ملاحظات')
    department_level1_id = fields.Many2one('hr.department', string='الفرع', readonly=1, states={'draft': [('readonly', 0)]})
    department_level2_id = fields.Many2one('hr.department', string='القسم', readonly=1, states={'draft': [('readonly', 0)]})
    department_level3_id = fields.Many2one('hr.department', string='الشعبة', readonly=1, states={'draft': [('readonly', 0)]})
    salary_grid_type_id = fields.Many2one('salary.grid.type', string='نوع الموظف', readonly=1, states={'draft': [('readonly', 0)]},)
    decission_id = fields.Many2one('hr.decision', string=u'القرارات')
    is_increase_line = fields.Boolean(string='اللائحة',default=False)

    @api.multi
    def action_employee_increase_ids_lines(self):
        self.ensure_one()
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
        result = []
        result_sanction = []
        res = {}
        # filter by type
        if self.salary_grid_type_id:
            employee_ids = employee_obj.search([('id', 'in', employee_ids), ('type_id', '=', self.salary_grid_type_id.id)]).ids
        result = list(set(employee_ids))
        print'result',result
        liste_employee_ids = set()
        sanctions = self.env['hr.sanction.ligne'].search([('state', '=', 'done'), ('sanction_id.type_sanction', '=', self.env.ref('smart_hr.data_hr_sanction_type_grade').id)])
        print'sanctions',sanctions
        for rec in sanctions:
            liste_employee_ids.add(rec.employee_id.id)
        result_sanction = list(liste_employee_ids)
        result_total = set(result) - set(result_sanction)
        result_inter = []
        result_employee =[]
        result_employee_error =[]
        for rec in result_total:
            employee_id = employee_obj.search([('id', '=', rec)])
            salary_grid_detail_id, basic_salary = employee_id.get_salary_grid_id(False)
            if not employee_id.type_id or not employee_id.degree_id or not employee_id.grade_id or basic_salary == 0.00:
                result_employee_error.append({'employee_id': employee_id})
            else :
                result_employee.append({'employee_id': employee_id,'basic_salary': basic_salary})
        self.employee_increase_ids = result_employee
        self.employee_errors_ids = result_employee_error
        for rec in   result_sanction  :
            result_inter.append({'employee_id': rec})
            print'result_inter',result_inter
        self.employee_deprivated_ids = result_inter
        self.is_increase_line =True

  
    @api.multi
    def action_update_increase_line(self):
        for rec in self :
            result_employee = []
            employee_obj = self.env['hr.employee']
            for line in rec.employee_errors_ids: 
                employee_id = employee_obj.search([('id', '=', line.id)])
                print'employee_id',employee_id
                salary_grid_detail_id, basic_salary = employee_id.get_salary_grid_id(False)
                if not employee_id.type_id or not employee_id.degree_id or not employee_id.grade_id or basic_salary == 0.00:
                    result_employee.append({'employee_id': employee_id,'basic_salary': basic_salary})
                rec.employee_increase_ids = result_employee

    @api.multi
    def open_decission_increase(self):
        decision_obj= self.env['hr.decision']
        if self.decission_id:
            decission_id = self.decission_id.id
        else :
            decision_type_id = 1
            decision_date = fields.Date.today() # new date
            if self.periode_increase:
                decision_type_id = self.env.ref('smart_hr.data_decision_type39').id
 
            # create decission
            decission_val={
              #  'name': self.number_decision,
                'decision_type_id':decision_type_id,
                'date':decision_date,
                'employee_id' :False}
            decision = decision_obj.create(decission_val)
            decision.text = decision.replace_text(False,decision_date,decision_type_id,'employee',args={'DATE':self.date})
            decission_id = decision.id
            self.decission_id = decission_id
        self.number_decision = self.decission_id.name
        self.date_decision = self.decission_id.date
        return {
            'name': _(u'قرار العلاوة'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'hr.decision',
            'view_id': self.env.ref('smart_hr.hr_decision_wizard_form').id,
            'type': 'ir.actions.act_window',
            'res_id': decission_id,
            'target': 'new'
            }

    @api.model
    def create(self, vals):
        res = super(hrIncrease, self).create(vals)
        # Sequence
        vals = {}
        vals['name'] = self.env['ir.sequence'].get('hr.increase.seq')
        res.write(vals)
        return res

    @api.one
    def action_pim(self):
        for rec in self :
            if len(rec.employee_errors_ids)> 1 : 
                raise UserError(u"لا يمكن إرسال إعتماد ويوجد موظفين لهم أخطاء")
            if len(rec.employee_increase_ids)< 1 : 
                raise UserError(u"لا يمكن إرسال إعتماد ولايوجد موظفين مستحقين للعلاوة")
            rec.state = 'pim'
#            if  for line in rec.employee_deprivated_ids :
#                 increase_ids = self.env['hr.employee.increase.percent'].search([('employee_id', '=', line.id)])
#                 if increase_ids :
#                     raise UserError(u"يجب إنشاء حساب بنكي للإيداع  للموظف  %s " % line.display_name)
            

    @api.one
    def button_refuse(self):
        self.state = 'draft'

    @api.one
    def action_refuse_pim2(self):
        self.state = 'hrm'

    @api.one
    def action_hrm(self):
        for rec in self :
            rec.state = 'hrm'

    @api.one
    def action_pim2(self):
        self.state = 'pim2'

    @api.multi
    def action_done(self):
        for rec in self :
            for line in rec.employee_increase_ids:
                new_basic_salary = 0.0
#                 employee_increase_obj = self.env['employee.increase']
#                 self.env['employee.increase'].create({'name': rec.date,
#                                                       'amount': line.increase_percent,
#                                                       'date': self.date,
#                                                       'employee_id': line.employee_id.id,
#                                                   })
                degree_obj = self.env['salary.grid.degree']
                new_degree_code = int(line.degree_id.code) + 1
                if new_degree_code < 10:
                    new_degree_code = '0' + str(new_degree_code)
                new_degree_code = str(new_degree_code)
                new_degree_id = degree_obj.search([('code', '=', new_degree_code),('grade_id','=',line.grade_id.id)], limit=1).id
                print'new_degree_idnew_degree_id',new_degree_id
                if new_degree_id:
                    line.new_degree_id = new_degree_id
                else :
                    line.new_degree_id = line.degree_id.id
                grid_domain= [('grid_id.state', '=', 'done'),
                         ('grid_id.enabled', '=', True),
                         ('type_id', '=', line.type_id.id),
                         ('grade_id', '=', line.grade_id.id),
                         ('degree_id', '=', line.new_degree_id.id)]
                salary_grid_detail_id = self.env['salary.grid.detail'].search(grid_domain, order='date desc', limit=1)
                if salary_grid_detail_id:
                    new_basic_salary = salary_grid_detail_id.basic_salary
                line.new_basic_salary = new_basic_salary
        self.state = 'done'
   
    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state != 'draft' :
                raise ValidationError(u'لا يمكن حذف العلاوةفى هذه المرحلة يرجى مراجعة مدير النظام')
        return super(hrIncrease, self).unlink()

class HrEmployeeDeprivation(models.Model):
    _name = 'hr.employee.deprivation'

    increase_id = fields.Many2one('hr.increase')
    employee_id = fields.Many2one('hr.employee', string=u'الموظف', required=1)
    reason = fields.Char(string=u'السبب', readonly=1 ,compute='_compute_raison' )
    department_level1_id = fields.Many2one('hr.department', related='increase_id.department_level1_id')
    department_level2_id = fields.Many2one('hr.department', related='increase_id.department_level2_id')
    department_level3_id = fields.Many2one('hr.department', related='increase_id.department_level3_id')
    salary_grid_type_id = fields.Many2one('salary.grid.type', related='increase_id.salary_grid_type_id')

    _sql_constraints = [
        ('unique_deprivation_emp', 'UNIQUE(increase_id,employee_id)', u"يجب الا يتكرر الاستثناء من العلاوة لنفس الموظف"),
    ]
    @api.onchange('department_level1_id', 'department_level2_id', 'department_level3_id', 'salary_grid_type_id')
    def onchange_department_level(self):
        dapartment_obj = self.env['hr.department']
        employee_obj = self.env['hr.employee']
        department_level1_id = self.increase_id.department_level1_id and self.increase_id.department_level1_id.id or False
        department_level2_id = self.increase_id.department_level2_id and self.increase_id.department_level2_id.id or False
        department_level3_id = self.increase_id.department_level3_id and self.increase_id.department_level3_id.id or False
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
        result = []
        result_sanction = []
        res = {}
        # filter by type
        if self.salary_grid_type_id:
            employee_ids = employee_obj.search([('id', 'in', employee_ids), ('type_id', '=', self.increase_id.salary_grid_type_id.id)]).ids
        result = list(set(employee_ids))
        liste_employee_ids = set()
        sanctions = self.env['hr.sanction.ligne'].search([('state', '=', 'done'), ('sanction_id.type_sanction', '=', self.env.ref('smart_hr.data_hr_sanction_type_grade').id)])
        for rec in sanctions:
            liste_employee_ids.add(rec.employee_id.id)
        result_sanction = list(liste_employee_ids)
        result_inter = []
        for e in result:
            if e in result_sanction:
                result_inter.append(e)
        res['domain'] = {'employee_id': [('id', 'in', list(result_inter))]}
        return res

    @api.multi
    @api.depends('employee_id')
    def _compute_raison(self):
        for rec in self:
            sanctions = self.env['hr.sanction.ligne'].search([('state', '=', 'done'),('employee_id','=',rec.employee_id.id), ('sanction_id.type_sanction', '=', self.env.ref('smart_hr.data_hr_sanction_type_grade').id)],limit=1)
            if sanctions:
                rec.reason = sanctions.raison

class hrEmployeeIncreasePercent(models.Model):

    _name = 'hr.employee.increase.percent'
    _inherit = ['mail.thread']
    _order = 'id desc'

    _description = u'نسبة العلاوة'
    increase_id  = fields.Many2one('hr.increase')
    employee_id = fields.Many2one('hr.employee', string='الموظف', required=1)
    degree_id = fields.Many2one('salary.grid.degree', string='الدرجة الحالية ', related='employee_id.degree_id')
    new_degree_id =fields.Many2one('salary.grid.degree', string = 'الدرجة الجديدة')
    basic_salary = fields.Float(string=u'الراتب الحالي', )
    type_id = fields.Many2one('salary.grid.type', string='نوع الموظف' ,related = 'employee_id.type_id')
    grade_id = fields.Many2one('salary.grid.grade', string='المرتبة', related = 'employee_id.grade_id')
    new_basic_salary = fields.Float(string=u'الراتب الجديد', )
    state = fields.Selection(related='increase_id.state' ,string=u'الحالة')
    increase = fields.Float(string=u'الراتب الحالي', )
    increase_percent = fields.Float(string=u'العلاوة', compute='increase_percent_count')
    department_level1_id = fields.Many2one('hr.department', related='increase_id.department_level1_id')
    department_level2_id = fields.Many2one('hr.department', related='increase_id.department_level2_id')
    department_level3_id = fields.Many2one('hr.department', related='increase_id.department_level3_id')
    salary_grid_type_id = fields.Many2one('salary.grid.type', related='increase_id.salary_grid_type_id')

    _sql_constraints = [
        ('unique_deprivation_emp', 'UNIQUE(increase_id,employee_id)', u"يجب الا يتكرر استحقاق العلاوة لنفس الموظف"),
    ]
    @api.onchange('department_level1_id', 'department_level2_id', 'department_level3_id', 'salary_grid_type_id')
    def onchange_department_level(self):
        dapartment_obj = self.env['hr.department']
        employee_obj = self.env['hr.employee']
        department_level1_id = self.increase_id.department_level1_id and self.increase_id.department_level1_id.id or False
        department_level2_id = self.increase_id.department_level2_id and self.increase_id.department_level2_id.id or False
        department_level3_id = self.increase_id.department_level3_id and self.increase_id.department_level3_id.id or False
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
        filte_empl = []
        result_total = []
        if self.salary_grid_type_id:
            employee_ids = employee_obj.search([('id', 'in', employee_ids), ('type_id', '=', self.increase_id.salary_grid_type_id.id)]).ids
              # filter by type
        filte_empl = list(set(employee_ids))

        liste_employee_ids = set()
        sanctions = self.env['hr.sanction.ligne'].search([('state', '=', 'done'), ('sanction_id.type_sanction', '=', self.env.ref('smart_hr.data_hr_sanction_type_grade').id)])
        for rec in sanctions:
            liste_employee_ids.add(rec.employee_id.id)
        result_sanction = list(liste_employee_ids)
        result_total = set(filte_empl) - set(result_sanction)
        result.update({'domain': {'employee_id': [('id', 'in',list(result_total))]}})
        return result

    @api.multi
    def increase_percent_count(self):
        for rec in self:
            increase_count = rec.new_basic_salary -rec.basic_salary
            if increase_count < 0.0 :
                rec.increase_percent = 0.00
            else :
                rec.increase_percent = increase_count
            
class hrEmployeeIncreaseError(models.Model):
    _name = 'hr.employee.increase.error'
    _inherit = ['mail.thread']
    _order = 'id desc'

    _description = u'نسبة العلاوة'
    increase_id  = fields.Many2one('hr.increase')
    employee_id = fields.Many2one('hr.employee', string='الموظفين', required=1)
    degree_id = fields.Many2one('salary.grid.degree', string='الدرجة الحالية ', related='employee_id.degree_id')
    new_degree_id =fields.Many2one('salary.grid.degree', string = 'الدرجة الجديدة')
    basic_salary = fields.Float(string=u'الراتب الحالي', related = 'employee_id.basic_salary')
    type_id = fields.Many2one('salary.grid.type', string='الصنف' ,related = 'employee_id.type_id')
    grade_id = fields.Many2one('salary.grid.grade', string='المرتبة', related = 'employee_id.grade_id')
    new_basic_salary = fields.Float(string=u'الراتب الجديد', )


class HrPeriodeIncrease(models.Model):
    _name = 'hr.periode.increase'
    _description = u'فترة العلاوة'

    name = fields.Char(string='المسمى', required=1)
    period_id = fields.Many2one('hr.period', string=u'الفترة', domain=[('is_open', '=', True)], required=1)
   
