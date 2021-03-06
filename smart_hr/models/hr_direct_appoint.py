# -*- coding: utf-8 -*-


from openerp import models, fields, api, _
from openerp.exceptions import Warning
from dateutil.relativedelta import relativedelta
from openerp.exceptions import ValidationError
from datetime import date, datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT


class HrDirectAppoint(models.Model):
    _name = 'hr.direct.appoint'
    _order = 'date desc'
    _rec_name = 'employee_id'

    employee_id = fields.Many2one('hr.employee', string=' إسم الموظف', required=1)
    number = fields.Char(string='الرقم الوظيفي', readonly=1)
    code = fields.Char(string=u'رمز الوظيفة ', readonly=1)
    country_id = fields.Char(related='employee_id.country_id.national', readonly=True, string='الجنسية')
    job_id = fields.Many2one('hr.job', string='الوظيفة', readonly=1)
    number_job = fields.Char(string='رقم الوظيفة', readonly=1)
    type_id = fields.Many2one('salary.grid.type', string='الصنف', readonly=1)
    department_id = fields.Many2one('hr.department', string='الادارة', readonly=1)
    grade_id = fields.Many2one('salary.grid.grade', string='المرتبة', readonly=1)
    far_age = fields.Float(string=' السن الاقصى', readonly=1)
    basic_salary = fields.Float(string='الراتب الأساسي', readonly=1)
    degree_id = fields.Many2one('salary.grid.degree', string='الدرجة', readonly=1)
    date_direct_action = fields.Date(string='تاريخ المباشرة ', required=1, default=fields.Datetime.now())
    type_appointment = fields.Many2one('hr.type.appoint', string=u'نوع التعيين')
    appoint_id = fields.Many2one('hr.decision.appoint', string=u'تعيين الموظف')
    date = fields.Date(string=u'التاريخ ', default=fields.Datetime.now(), readonly=1)
    state = fields.Selection([('new', '  طلب'),
                              ('waiting', u'في إنتظار المباشرة'),
                              ('done', u'مباشرة'),
                              ('cancel', u'ملغاة')], string='الحالة', readonly=1, default='new')

    decission_id = fields.Many2one('hr.decision', string=u'القرارات')

    type = fields.Selection([
        ('appoint' , u'تعيين'),
        ('transfer', u'نقل'),
        ('promotion', u'ترقية'),
        ('shcolarship', u'ابتعاث'),
        ('improve_situation', u'تحسين وضع')], string='نوع قرار المباشرة', required=1 )
    history_line_id = fields.Many2one('hr.employee.history')
    shcolarship_id = fields.Many2one('hr.scholarship', string=u'الابتعاث')



    @api.multi
    def open_decission_direct(self):
        decision_obj= self.env['hr.decision']
        if self.decission_id:
            decission_id = self.decission_id.id
        else :
            decision_type_id = 1
            decision_date = fields.Date.today() # new date
            if self.employee_id:
                decision_type_id = self.env.ref('smart_hr.data_employee_direct_appoint').id

            # create decission
            decission_val={
               # 'name': self.env['ir.sequence'].get('hr.direct.appoint.seq'),
                'decision_type_id':decision_type_id,
                'date':decision_date,
                'employee_id' :self.employee_id.id }
            decision = decision_obj.create(decission_val)
            decision.text = decision.replace_text(self.employee_id, decision_date, decision_type_id, 'appoint')
            decission_id = decision.id
            self.decission_id = decission_id
        self.history_line_id.num_decision = self.decission_id.name
        self.history_line_id.date_decision = self.decission_id.date
        return {
            'name': _(u'قرار مباشرة التعيين'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'hr.decision',
            'view_id': self.env.ref('smart_hr.hr_decision_wizard_form').id,
            'type': 'ir.actions.act_window',
            'res_id': decission_id,
            'target': 'new'
            }




    @api.multi
    def action_waiting(self):
        if self.appoint_id:
            self.appoint_id.write({'date_direct_action': self.date_direct_action})
            if not self.employee_id.recruiter_date:
                self.employee_id.recruiter_date = self.date_direct_action
            if not self.employee_id.begin_work_date:
                self.employee_id.begin_work_date = self.date_direct_action
        else:
            if self.type == 'transfer':
                raise ValidationError(u"لا يوجد تعيين بنقل غير مفعل للموظف!")
            elif self.type == 'promotion':
                raise ValidationError(u"لا يوجد تعيين بترقية غير مفعل للموظف!")
            elif self.type == 'appoint':
                raise ValidationError(u"لا يوجد تعيين غير مفعل للموظف!")
            elif self.type == 'improve_situation':
                raise ValidationError(u"لا يوجد تعيين بتحسين وضع غير مفعل للموظف!")
        if not self.shcolarship_id and self.type == 'shcolarship':
            raise ValidationError(u"لا يوجد ابتعاث غير مباشر بعده للموظف!")
        self.state = 'waiting'

    @api.multi
    def button_cancel_appoint(self):
        self.ensure_one()

        appoint_line = self.env['hr.decision.appoint'].search(
            [('employee_id', '=', self.employee_id.id), ('state', '=', 'done')], limit=1)
        for line in appoint_line:
            line.write({'state_appoint': 'refuse'})
        self.state = 'cancel'

    @api.multi
    def button_direct_appoint(self):
        self.ensure_one()
        if self.date_direct_action > datetime.today().strftime('%Y-%m-%d'):
            raise ValidationError(u"لا يمكن  التفعيل  ،  تاريخ المباشرة يجب أن يكون أصغر  أو مساوي لتاريخ اليوم ")
        if self.appoint_id:
            self.appoint_id.action_activate()
        title = u" إشعار بمباشرة "
        msg = u"' إشعار بمباشرة " + unicode(self.employee_id.display_name) + u"'"
        group_id = self.env.ref('smart_hr.group_department_employee')
        self.send_appoint_group(group_id, title, msg)
        if self.type == 'transfer':
            self.appoint_id.transfer_id.done_date = self.date_direct_action
        elif self.type == 'promotion':
            self.appoint_id.promotion_id.done_date = self.date_direct_action
        elif self.type == 'improve_situation':
            self.appoint_id.improve_id.done_date = self.date_direct_action
            self.appoint_id.improve_id.state_active = 'active'
        elif self.type == 'shcolarship':
            self.shcolarship_id.restarted = True
        history_line_id = self.env['hr.employee.history'].sudo().add_action_line(self.employee_id, self.decission_id.name, self.decission_id.date, "مباشرة")
        self.history_line_id = history_line_id
        self.state = 'done'

    @api.onchange('date_direct_action')
    def _onchange_date_direct_action(self):
        if self.date_direct_action and self.date_direct_action < datetime.today().strftime('%Y-%m-%d'):
            warning = {
                'title': _('تحذير!'),
                'message': _(' تاريخ المباشرة يجب أن يكون أكبر  أو مساوي لتاريخ اليوم '),
            }
            self.date_direct_action = False
            return {'warning': warning}

    @api.onchange('employee_id', 'type')
    def _onchange_employee_id(self):
        if self.employee_id and self.date_direct_action:
            self.number = self.employee_id.number
            self.country_id = self.employee_id.country_id.id
            shcolarship_id = False
            appoint_line = False
            type_appointment_transfer = self.env.ref('smart_hr.data_hr_recrute_from_transfert').id
            type_appointment_promotion = [self.env.ref('smart_hr.data_hr_promotion_agent').id, self.env.ref('smart_hr.data_hr_promotion_member').id]
            type_appointment_improve_situation = self.env.ref('smart_hr.data_hr_improve_situation_type').id
            if self.type == 'transfer':
                type_appointment = type_appointment_transfer
                appoint_line = self.env['hr.decision.appoint'].search([('employee_id', '=', self.employee_id.id),
                                                                        ('state', '=', 'done'),
                                                                        ('type_appointment', '=', type_appointment),
                                                                        ('state_appoint', '=', 'new')], limit=1)
            elif self.type == 'promotion':
                type_appointment = [self.env.ref('smart_hr.data_hr_promotion_agent').id, self.env.ref('smart_hr.data_hr_promotion_member').id]
                appoint_line = self.env['hr.decision.appoint'].search([('employee_id', '=', self.employee_id.id),
                                                                        ('state', '=', 'done'),
                                                                        ('type_appointment', '=', type_appointment),
                                                                        ('state_appoint', '=', 'new')], limit=1)
            elif self.type == 'appoint':
                appoint_line = self.env['hr.decision.appoint'].search([('employee_id', '=', self.employee_id.id),
                                                                        ('state', '=', 'done'),
                                                                        ('type_appointment', 'not in', [type_appointment_transfer, type_appointment_improve_situation]),
                                                                        ('type_appointment', 'not in', type_appointment_promotion),
                                                                        ('state_appoint', '=', 'new')], limit=1)
            elif self.type == 'improve_situation':
                appoint_line = self.env['hr.decision.appoint'].search([('employee_id', '=', self.employee_id.id),
                                                                        ('state', '=', 'done'),
                                                                        ('type_appointment', '=', type_appointment_improve_situation),
                                                                        ('state_appoint', '=', 'new')], limit=1)
            if self.type in ['transfer', 'promotion', 'appoint', 'improve_situation']:
                if appoint_line:
                    self.job_id = appoint_line.job_id.id
                    self.code = appoint_line.job_id.name.number
                    self.number_job = appoint_line.job_id.number
                    self.type_id = appoint_line.job_id.type_id.id
                    self.far_age = appoint_line.type_id.far_age
                    self.department_id = appoint_line.department_id.id
                    self.appoint_id = appoint_line.id
                    self.grade_id = appoint_line.job_id.grade_id.id
                    self.degree_id = appoint_line.degree_id.id
                    self.basic_salary = appoint_line.basic_salary
                else:
                    self.job_id = False
                    self.code = False
                    self.number_job = False
                    self.type_id = False
                    self.far_age = False
                    self.department_id = False
                    self.appoint_id = False
                    self.grade_id = False
                    self.degree_id = False
                    self.basic_salary = False
            elif self.type == 'shcolarship':
                shcolarship_id = self.env['hr.scholarship'].search([('employee_id', '=', self.employee_id.id), ('state', 'in', ['done', 'finished']),
                                                                    ('date_to', '<', self.date_direct_action), ('restarted', '=', False)], limit=1)
                self.job_id = self.employee_id.job_id.id
                self.code = self.employee_id.job_id.name.number
                self.number_job = self.employee_id.job_id.number
                self.type_id = self.employee_id.job_id.type_id.id
                self.far_age = self.employee_id.type_id.far_age
                self.department_id = self.employee_id.department_id.id
                self.grade_id = self.employee_id.grade_id.id
                self.degree_id = self.employee_id.degree_id.id
                salary_grid_id, basic_salary = self.employee_id.get_salary_grid_id(self.date_direct_action)
                self.basic_salary = basic_salary
                if shcolarship_id:
                    self.shcolarship_id = shcolarship_id.id


   
    def send_appoint_group(self, group_id, title, msg):
        """
        @param group_id: res.groups
        """
        for recipient in group_id.users:
            self.env['base.notification'].create({'title': title,
                                                  'message': msg,
                                                  'user_id': recipient.id,
                                                  'show_date': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                                  'res_id': self.id,
                                                  'res_action': 'smart_hr.action_hr_direct_appoint',
                                                   'type': 'hr_employee_appoint_direct_type',
                                                  })

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state != 'new':
                raise UserError(u'لا يمكن حذف قرار مباشرة التعين  إلا في حالة طلب !')
            return super(HrDirectAppoint, self).unlink()
