# -*- coding: utf-8 -*-

from openerp import models, fields, api, _, SUPERUSER_ID
from openerp.exceptions import Warning
from dateutil.relativedelta import relativedelta
from openerp.exceptions import ValidationError
from datetime import date, datetime, timedelta
from openerp.tools import SUPERUSER_ID
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT


class HrImproveSituatim(models.Model):
    _name = 'hr.improve.situation'
    _inherit = ['mail.thread']
    _description = u'تحسين وضع'
    _rec_name = 'employee_id'

    employee_id = fields.Many2one('hr.employee', string=' إسم الموظف', required=1, )
    number = fields.Char(string='الرقم الموظف', readonly=1)
    state = fields.Selection([('new', 'طلب'), ('waiting', 'في إنتظار الإعتماد'), ('done', 'اعتمدت')], readonly=1,
                             default='new')
    order_date = fields.Date(string='تاريخ الطلب', default=fields.Datetime.now())
    order_number = fields.Char(string='رقم الخطاب', required=1)
    job_id = fields.Many2one('hr.job', string='الوظيفة', readonly=1)
    number_job = fields.Char(string='الرمز الوظيفي', readonly=1)
    type_id = fields.Many2one('salary.grid.type', string='الصنف', readonly=1)
    department_id = fields.Many2one('hr.department', string='الادارة', readonly=1)
    grade_id = fields.Many2one('salary.grid.grade', string='المرتبة', readonly=1)
    degree_id = fields.Many2one('salary.grid.degree', string='الدرجة', readonly=1)
    far_age = fields.Float(string=' السن الاقصى', readonly=1)
    basic_salary = fields.Float(string='الراتب الأساسي', readonly=1)
    transport_allow = fields.Float(string='بدل النقل', readonly=1)
    retirement = fields.Float(string='المحسوم للتقاعد', readonly=1)
    net_salary = fields.Float(string='صافي الراتب', readonly=1)
    salary_recent = fields.Float(string=' أخر راتب شهري ', readonly=1)
    transport_alocation = fields.Boolean(string='بدل نقل', readonly=1)
    type_improve = fields.Many2one('hr.type.improve.situation', string='نوع التحسين', required=1,
                                   states={'new': [('readonly', 0)]})
    order_picture1 = fields.Binary(string='صورة القرار')
    new_job_id = fields.Many2one('hr.job', string='الوظيفة', required=1,Domain=[('state','=','unoccupied')])
    number_job1 = fields.Char(string='رقم الوظيفة')
    order_date1 = fields.Date(string='تاريخ القرار')
    date_hiring1 = fields.Date(string='تاريخ التعيين')
    type_id1 = fields.Many2one('salary.grid.type', string='الصنف')
    department_id1 = fields.Many2one('hr.department', string='الادارة', readonly=1)
    grade_id1 = fields.Many2one('salary.grid.grade', string='المرتبة' , readonly=1)
    degree_id1 = fields.Many2one('salary.grid.degree', string='الدرجة' , required=1)
    basic_salary1 = fields.Float(string='الراتب الأساسي')
    net_salary1 = fields.Float(string='صافي الراتب')
    is_same_type = fields.Boolean(string='نفس الصنف',related="type_improve.is_same_type")
    defferential_is_paied = fields.Boolean(string='defferential is paied', default=False)
    decission_id  = fields.Many2one('hr.decision', string=u'القرارات',)



    @api.multi
    def open_decission_improve(self):
        decision_obj= self.env['hr.decision']
        if self.decission_id:
            decission_id = self.decission_id.id
        else :
            decision_type_id = 1
            decision_date = fields.Date.today() # new date
            if self.type_improve and self.employee_id.type_id.id == self.env.ref('smart_hr.data_salary_grid_type3').id:
                decision_type_id = self.env.ref('smart_hr.data_decision_type7').id
            if self.type_improve and self.employee_id.type_id.id == self.env.ref('smart_hr.data_salary_grid_type4').id:
                decision_type_id = self.env.ref('smart_hr.data_decision_type9').id
            if self.type_improve :
                decision_type_id = self.env.ref('smart_hr.data_decision_type7').id
            # create decission
            decission_val={
                'name': self.env['ir.sequence'].get('hr.improve.seq'),
                'decision_type_id':decision_type_id,
                'date':decision_date,
                'employee_id' :self.employee_id.id }
            decision = decision_obj.create(decission_val)
            decision.text = decision.replace_text(self.employee_id,decision_date,decision_type_id,'employee')
            decission_id = decision.id
            self.decission_id =  decission_id
        return {
            'name': _(u'قرار تحسين الوضع'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'hr.decision',
            'view_id': self.env.ref('smart_hr.hr_decision_wizard_form').id,
            'type': 'ir.actions.act_window',
            'res_id': decission_id,
            'target': 'new'
            }




    @api.onchange('type_id1')
    def onchange_type_id1(self):
        res = {}
        if  self.type_id1 :
            job_search_ids = self.env['hr.job'].search([('type_id', '=' , self.type_id1.id)])
            job_ids = [rec.id for rec in job_search_ids]
            res['domain'] = {'new_job_id': [('id', 'in', job_ids)]}
            return res

    @api.onchange('new_job_id')
    def _onchange_new_job_id(self):
        for rec in self:
            if rec.new_job_id :
                rec.department_id1 = rec.new_job_id.department_id
                rec.grade_id1 = rec.new_job_id.grade_id

    @api.one
    def action_waiting(self):
        self.state = 'waiting'

    @api.multi
    def action_done(self):
        self.ensure_one()
        self.env['hr.decision.appoint'].create({'employee_id': self.employee_id.id,
                                                'job_id': self.new_job_id.id,
                                                'number_job': self.new_job_id.number,
                                                'code': self.new_job_id.name.number,
                                                'grade_id': self.new_job_id.grade_id.id,
                                                'department_id': self.new_job_id.department_id.id,
                                                'degree_id': self.degree_id1.id,
                                                'date_hiring': self.order_date,
                                                'order_date': fields.Datetime.now(),
                                                'state': 'draft',
                                                'type_appointment': self.type_improve.type_appointment.id,
                                                'name': self.order_number,
                                                  })
        self.state = 'done'
        user = self.env['res.users'].browse(self._uid)
        self.message_post(u"تمت إحداث تحسين الوضع جديد '" + unicode(user.name) + u"'")

    @api.one
    def button_refuse(self):
        self.state = 'new'

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        if self.employee_id:

            employee_id_line = self.env['hr.employee'].search([('id', '=', self.employee_id.id)
                                                                       ])
            if employee_id_line:
                self.number = employee_id_line.number
                self.number_job = employee_id_line.job_id.name.number
                self.job_id = employee_id_line.job_id
                self.type_id = employee_id_line.type_id
                self.grade_id = employee_id_line.grade_id
                self.degree_id = employee_id_line.degree_id
                self.department_id = employee_id_line.department_id
                self.basic_salary = employee_id_line.basic_salary

    @api.onchange('type_improve')
    def _onchange_type_improve(self):
        for rec in self:
            if rec.type_improve.is_same_type == True :
                rec.new_job_id = rec.job_id
                rec.type_id1 = rec.type_id 

class HrTypeImproveSituation(models.Model):
    _name = 'hr.type.improve.situation'
    _description = u'أنواع تحسين الوضع'

    name = fields.Char(string='النوع', required=1)
    code = fields.Char(string='الرمز')
    is_same_type = fields.Boolean(string='نفس الصنف')
    type_appointment = fields.Many2one('hr.type.appoint', string=u'نوع التعيين', required=1 )
