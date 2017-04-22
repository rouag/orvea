# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.exceptions import ValidationError
from openerp.tools import SUPERUSER_ID
from umalqurra.hijri_date import HijriDate
from openerp.addons.smart_base.util.umalqurra import *
from umalqurra.hijri import Umalqurra

from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT


class HrDeprivationPremium(models.Model):
    _name = 'hr.deprivation.premium'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _order = 'id desc'
    _description = u'قرار حرمان من العلاوة'

    name = fields.Char(string='رقم القرار',readonly=1, related='decission_id.name')
    order_date = fields.Date(string='تاريخ القرار',readonly=1, related='decission_id.date')
    deprivation_file = fields.Binary(string='ملف القرار', states={'draft': [('readonly', 0)]})
    date_deprivation = fields.Date(string='التاريخ' , default=fields.Datetime.now(), states={'draft': [('readonly', 0)]})
    deprivation_file_name = fields.Char(string='ملف القرار')
    years_id = fields.Many2one('hr.fiscalyear', string=u'  السنة ',required=1)
    employee_ids = fields.Many2many('hr.employee', string='الموظفين', states={'draft': [('readonly', 0)]})
    department_level1_id = fields.Many2one('hr.department', string='الفرع', readonly=1, states={'draft': [('readonly', 0)]})
    department_level2_id = fields.Many2one('hr.department', string='القسم', readonly=1, states={'draft': [('readonly', 0)]})
    department_level3_id = fields.Many2one('hr.department', string='الشعبة', readonly=1, states={'draft': [('readonly', 0)]})
    salary_grid_type_id = fields.Many2one('salary.grid.type', string='الصنف', readonly=1, states={'draft': [('readonly', 0)]},)
    decission_id = fields.Many2one('hr.decision', string=u'القرارات')
    
    deprivation_ids = fields.One2many('hr.deprivation.premium.ligne', 'deprivation_id',
                                      string=u'قائمة المحرومين من العلاوة', 
                                      states={'draft': [('readonly', 0)]})
    state = fields.Selection([('draft', '  طلب'),
                              ('waiting', u'في إنتظار الاعتماد'),
                              ('order',u'إصدار قرار'),
                              ('done', u'اعتمدت'),
                              ('refused', u'مرفوضة'),
                              ], string='الحالة', readonly=1, default='draft')



  
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
  


    @api.multi
    def button_deprivation_premium(self):
        decision_obj= self.env['hr.decision']
        if self.decission_id:
            decission_id = self.decission_id.id
        else :
            decision_type_id = 1
            decision_date = fields.Date.today() # new date
            if self.order_date:
                decision_type_id = self.env.ref('smart_hr.data_decision_deprivation_premium').id
            # create decission
            decission_val={
              #  'name': self.name,
                'decision_type_id':decision_type_id,
                'date':decision_date,
                'employee_id' :False}
            decision = decision_obj.create(decission_val)
            decision.text = decision.replace_text(False,decision_date,decision_type_id,'employee',args={'DATE':self.order_date})
            decission_id = decision.id
            self.decission_id =  decission_id
        return {
            'name': u'قرار حرمان من العلاوة',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'hr.decision',
            'view_id': self.env.ref('smart_hr.hr_decision_wizard_form').id,
            'type': 'ir.actions.act_window',
            'res_id': decission_id,
            'target': 'new'
            }





    @api.multi
    def action_draft(self):
        for rec in self :
            line_ids =[]
            rec.name = self.env['ir.sequence'].get('hr.deprivation.premium.seq')
            for line in rec.employee_ids :
                vals = {'employee_id':line.id,}
                line_ids.append(vals)
            rec.deprivation_ids = line_ids
        self.state = 'waiting'


    @api.multi
    def button_refuse(self):
        for deprivation in self:
            deprivation.state = 'refused'

            
    @api.multi
    def action_waiting(self):
        for rec in self:
            sanction_obj = self.env['hr.sanction']
            sanction_val = {
                                    'name':rec.name,
                                   'type_sanction':self.env.ref('smart_hr.data_hr_sanction_type_grade').id,
                                    'state':'done',
                           }
            lines = []
            sanction = sanction_obj.create(sanction_val)
            for  temp in rec.deprivation_ids :
                if temp.state_deprivation =='waiting' :
                    employee_val = {
                              'employee_id': temp.employee_id,
                              'state':'done',
                              }
                    lines.append(employee_val)
                    temp.state_deprivation ='done'
            sanction.difference_ids = lines
            rec.state = 'done'
    
    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state != 'new' :
                raise ValidationError(u'لا يمكن حذف حرمان من العلاوة  فى هذه المرحلة يرجى مراجعة مدير النظام')
        return super(HrDeprivationPremium, self).unlink()   

class HrdeprivationPremiumLigne(models.Model):
    _name = 'hr.deprivation.premium.ligne'
    _description = u' قائمة المحرومين من العلاوة'

    deprivation_id = fields.Many2one('hr.deprivation.premium', string=' قائمة المحرومين من العلاوة', ondelete='cascade')
    state = fields.Selection(related='deprivation_id.state' ,string=u'الحالة')
    employee_id = fields.Many2one('hr.employee', string=u'  الموظف', required=1)
    raison = fields.Char(string='السبب' )
    is_cancel = fields.Boolean(string='مستبعد' , default=False)
    state_deprivation = fields.Selection([('waiting' , 'في إنتظار التاكيد'),
                              ('excluded', 'مستبعد'),
                              ('done', 'تم التاكيد'),
                              ], string='الحالة', readonly=1, default='waiting')
  
    
    

#     @api.onchange('employee_id')
#     def onchange_employee_id(self):
#         res = {}
#         employee_ids = set()
#         sanctions = self.env['hr.sanction.ligne'].search([('state', '=', 'done'), ('sanction_id.type_sanction', '=', self.env.ref('smart_hr.data_hr_sanction_type_grade').id)])
#         for rec in sanctions:
#             employee_ids.add(rec.employee_id.id)
#         res['domain'] = {'employee_id': [('id', 'in', list(employee_ids))]}
#         return res

#     @api.multi
#     @api.depends('employee_id')
#     def _compute_raison(self):
#         for rec in self:
#             sanctions = self.env['hr.sanction.ligne'].search([('state', '=', 'done'),('employee_id','=',rec.employee_id.id), ('sanction_id.type_sanction', '=', self.env.ref('smart_hr.data_hr_sanction_type_grade').id)],limit=1)
#             if sanctions:
#                 rec.raison = sanctions.raison

    @api.multi
    def button_cancel(self):
        for rec in self:
            rec.is_cancel =True
            rec.state_deprivation = 'excluded'
    
    @api.multi
    def button_confirm(self):
        for deprivation in self:
            deprivation.state = 'done'
