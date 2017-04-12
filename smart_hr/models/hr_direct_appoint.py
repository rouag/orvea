# -*- coding: utf-8 -*-


from openerp import models, fields, api, _
from openerp.exceptions import Warning
from dateutil.relativedelta import relativedelta
from openerp.exceptions import ValidationError
from datetime import date, datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT


class HrDirectAppoint(models.Model):
    _name = 'hr.direct.appoint'
    _order = 'id desc'
    _rec_name = 'employee_id'

    employee_id = fields.Many2one('hr.employee', string=' إسم الموظف', required=1)
    number = fields.Char(string='الرقم الوظيفي', readonly=1)
    code = fields.Char(string=u'رمز الوظيفة ', readonly=1)
    country_id = fields.Many2one(related='employee_id.country_id', store=True, readonly=True, string='الجنسية')
    job_id = fields.Many2one('hr.job', string='الوظيفة', store=True, readonly=1)
    number_job = fields.Char(string='رقم الوظيفة', store=True, readonly=1)
    type_id = fields.Many2one('salary.grid.type', string='الصنف', store=True, readonly=1)
    department_id = fields.Many2one('hr.department', string='الادارة', store=True, readonly=1)
    grade_id = fields.Many2one('salary.grid.grade', string='المرتبة', store=True, readonly=1)
    far_age = fields.Float(string=' السن الاقصى', store=True, readonly=1)
    basic_salary = fields.Float(string='الراتب الأساسي', store=True, readonly=1)
    degree_id = fields.Many2one('salary.grid.degree', string='الدرجة', store=True, readonly=1)
    date_direct_action = fields.Date(string='تاريخ المباشرة ', required=1)
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
        ('promotion', u'ترقية')], string='نوع قرار المباشرة', required=1 )



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
                'name': self.env['ir.sequence'].get('hr.direct.appoint.seq'),
                'decision_type_id':decision_type_id,
                'date':decision_date,
                'employee_id' :self.employee_id.id }
            decision = decision_obj.create(decission_val)
            decision.text = decision.replace_text(self.employee_id,decision_date,decision_type_id,'appoint')
            decission_id = decision.id
            self.decission_id =  decission_id
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
            else:
                raise ValidationError(u"لا يوجد تعيين غير مفعل للموظف!")
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

        self.appoint_id.write({'is_started': True, 'state_appoint': 'active'})
        title = u"' إشعار بمباشرة التعين'"
        msg = u"' إشعار بمباشرة التعين'" + unicode(self.employee_id.display_name) + u"'"
        group_id = self.env.ref('smart_hr.group_department_employee')
        self.send_appoint_group(group_id, title, msg)
        self.env['hr.employee.history'].sudo().add_action_line(self.employee_id, "", self.date, "مباشرة")
        if self.type == 'transfer':
            self.appoint_id.transfer_id.done_date = self.date_direct_action
        if self.type == 'promotion':
            self.appoint_id.promotion_id.done_date = self.date_direct_action
        self.state = 'done'

    @api.onchange('employee_id','type')
    def _onchange_employee_id(self):
        if self.employee_id:
            self.number = self.employee_id.number
            self.country_id = self.employee_id.country_id.id
            type_appointment_transfer = self.env.ref('smart_hr.data_hr_recrute_from_transfert').id
            type_appointment_promotion = [self.env.ref('smart_hr.data_hr_promotion_agent').id, self.env.ref('smart_hr.data_hr_promotion_member').id]
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
            else:
                appoint_line = self.env['hr.decision.appoint'].search([('employee_id', '=', self.employee_id.id),
                                                                        ('state', '=', 'done'),
                                                                        ('type_appointment', '!=', type_appointment_transfer),
                                                                        ('type_appointment', 'not in', type_appointment_promotion),
                                                                        ('state_appoint', '=', 'new')], limit=1)

            if appoint_line:
                self.job_id = appoint_line.job_id.id
                self.code = appoint_line.job_id.name.number
                self.number_job = appoint_line.job_id.number
                self.type_id = appoint_line.type_id.id
                self.far_age = appoint_line.type_id.far_age
                self.grade_id = appoint_line.grade_id.id
                self.department_id = appoint_line.department_id.id
                self.appoint_id = appoint_line.id



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
                                                  'notif': True
                                                  })

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state != 'new':
                raise UserError(u'لا يمكن حذف قرار مباشرة التعين  إلا في حالة طلب !')
            return super(HrDirectAppoint, self).unlink()
