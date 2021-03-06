# -*- coding: utf-8 -*-

from openerp import fields, models, api, _
from openerp.exceptions import ValidationError
from openerp.tools import SUPERUSER_ID
from datetime import date, datetime, timedelta


class HrTermination(models.Model):
    _name = 'hr.termination'
    _inherit = ['ir.needaction_mixin', 'mail.thread']
    _description = u'طي القيد'
    _order = 'date desc'

    name = fields.Char(string=u'الرقم', readonly=1)
    date = fields.Date(string=u'التاريخ ',readonly=1, default=fields.Datetime.now())
    date_termination = fields.Date(string=u'تاريخ طي القيد  ', default=fields.Datetime.now())
    termination_date = fields.Date(string=u'تاريخ الإعتماد')
    employee_id = fields.Many2one('hr.employee', string=u'الموظف', required=1, domain=[('emp_state', 'not in', ['suspended', 'terminated']), ('employee_state', '=', 'employee')])
    employee_state = fields.Selection([('new', u'جديد'),
                                       ('waiting', u'في إنتظار الموافقة'),
                                       ('update', u'إستكمال البيانات'),
                                       ('done', u'اعتمدت'),
                                       ('refused', u'رفض'),
                                       ('employee', u'موظف')], string=u'الحالة', related='employee_id.employee_state')
    # Employee Info
    employee_no = fields.Char(related='employee_id.number')
    job_id = fields.Many2one(string=u'الوظيفة', related='employee_id.job_id')
    join_date = fields.Date(string=u'تاريخ الالتحاق بالجهة', related='employee_id.join_date')
    age = fields.Integer(string=u'السن', related='employee_id.age')
    country_id = fields.Many2one(related='employee_id.country_id', store=True, readonly=True, string='الجنسية')
    # Termination Info
    termination_type_id = fields.Many2one('hr.termination.type', string=u'نوع الطي', )
    nb_salaire = fields.Float(related='termination_type_id.nb_salaire', store=True, readonly=True,
                              string=u'عدد الرواتب المستحق')
    all_holidays = fields.Boolean(related='termination_type_id.all_holidays', store=True, readonly=True,
                                  string=u'كل الإجازة')
    max_days = fields.Float(related='termination_type_id.max_days', store=True, readonly=True,
                            string=u'الحد الاقصى لأيام الإجازة')

    reason = fields.Char(string=u'السبب')
    number_order = fields.Char(string=u'رقم القرار')
    letter_source = fields.Char(string=u'جهة الخطاب', )
    letter_no = fields.Char(string=u'رقم الخطاب')
    letter_date = fields.Date(string=u'تاريخ الخطاب')
    file_attachment = fields.Binary(string=u'مرفق الصورة الضوئية', attachment=True)
    file_attachment_name = fields.Char(string=u'مرفق الصورة الضوئية')
    decission_id = fields.Many2one('hr.decision', string=u'القرارات', )
    state = fields.Selection([
        ('draft', u'طلب'),
        ('hrm', u'مدير شؤون الموظفين'),
        ('done', u'اعتمدت'),
        ('refuse', u'رفض'),
    ], string=u'الحالة', default='draft')
    done_date = fields.Date(string='تاريخ التفعيل')
    history_line_id = fields.Many2one('hr.employee.history')

#     @api.onchange('termination_type_id')
#     def _onchange_employee_id(self):
#         res = {}
#         if not self.employee_id:
#             minus_employee_ids = self.env['hr.employee'].search([('emp_state', '=', 'employee')])
#             res['domain'] = {'employee_id': [('id', 'not in', minus_employee_ids)]}
#             return res

    @api.onchange('termination_type_id')
    def _onchange_termination_type_id(self):
        if self.employee_id.country_id.code == 'SA':
            for rec in self.termination_type_id:
                rec.nb_salaire = 0
                rec.all_holidays = 0
                rec.max_days = 0
                rec.nationality = True

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise ValidationError(u'لا يمكن حذف طي القيد فى هذه المرحلة يرجى مراجعة مدير النظام')
        return super(HrTermination, self).unlink()

    #     @api.constrains('employee_id')
    #     def check_employee_id(self):
    #         for ter in self:
    #             if self.search_count([('employee_id', '=', ter.employee_id.id), ('state', '=', 'done')]):
    #                 raise ValidationError(u"هذا الموظف تم أعتماد طي قيد لديه من قبل")

    @api.multi
    def check_constraintes(self):
        if self.termination_type_id.id == self.env.ref('smart_hr.data_hr_ending_service_type_normal').id:
            hr_employee_configuration_id = self.env['hr.employee.configuration'].search([], limit=1)
            if hr_employee_configuration_id:
                age_member = hr_employee_configuration_id.age_member
                age_nomember = hr_employee_configuration_id.age_nomember
                if (self.employee_id.is_member == True) and (self.employee_id.age < age_member):
                    raise ValidationError(u" السن الادنى  هو %s سنة" % age_member)
                if (self.employee_id.is_member == False) and (self.employee_id.age < age_nomember) :
                    raise ValidationError(u" السن الادنى  هو %s سنة" % age_nomember)
            else:
                    raise ValidationError(u"لالرجاء مراجعة اعدادات الموظف")
        if self.termination_type_id.evaluation_condition:
            years_progress = self.termination_type_id.years_progress
            for year in range(1, years_progress):
                employee_evaluation_id = self.env['hr.employee.evaluation.level'].search(
                    [('employee_id', '=', self.employee_id.id), ('year', '=', date.today().year - year)], limit=1)
                if employee_evaluation_id:
                    if employee_evaluation_id.degree_id.id not in self.termination_type_id.evaluation_required.ids:
                        raise ValidationError(u"الرجاء مراجعة تقييم وظيفي خاص لنوع طي القيد")
                else:
                    raise ValidationError(u"لا يوجد تقييم وظيفي خاص بالموظف ل%sسنة" % years_progress)

    @api.multi
    def button_hrm(self):
        self.ensure_one()
        self.check_constraintes()
        self.state = 'hrm'

    @api.model
    def create(self, vals):
        ret = super(HrTermination, self).create(vals)
        # Sequence
        vals = {}
        vals['name'] = self.env['ir.sequence'].get('hr.termination.sequence')
        ret.write(vals)
        return ret

    @api.one
    def button_done(self):
        for ter in self:
            if ter.employee_id.emp_state == 'suspended':
                raise ValidationError(u'لا يمكن طي قيد الموظف وهو مكفوف إليد')
            # Update Employee State
            ter.employee_id.emp_state = 'terminated'
            # Update Job
            #  ter.employee_id.job_id.write({'state': 'unoccupied', 'category': 'unooccupied_termination'})
            #ter.employee_id.job_id.employee = False
           # ter.employee_id.job_id = False
            # Update State
            ter.done_date = fields.Date.today()
            ter.state = 'done'
            # Set the termination date with the date of the final approve
            ter.termination_date = fields.Date.today()
            history_line_id = self.env['hr.employee.history'].sudo().add_action_line(ter.employee_id, ter.decission_id.name, ter.decission_id.date, "طي قيد")
            ter.history_line_id = history_line_id

    @api.one
    def button_refuse(self):
        for ter in self:
            ter.state = 'refuse'

    @api.model
    def _needaction_domain_get(self):
        return [
            ('state', '=', 'hrm'),
        ]

    @api.multi
    def open_decission_termination(self):
        decision_obj = self.env['hr.decision']
        if self.decission_id:
            decission_id = self.decission_id.id
        else:
            decision_type_id = 130
            decision_date = fields.Date.today()  # new date
            if self.termination_type_id.id == self.env.ref(
                    'smart_hr.data_hr_ending_service_early').id and self.employee_id.type_id.id == self.env.ref(
                    'smart_hr.data_salary_grid_type').id:
                decision_type_id = self.env.ref('smart_hr.data_decision_type11').id
            elif self.termination_type_id.id == self.env.ref(
                    'smart_hr.data_hr_ending_service_type_normal').id and self.employee_id.type_id.id == self.env.ref(
                    'smart_hr.data_salary_grid_type').id:
                decision_type_id = self.env.ref('smart_hr.data_decision_type14').id
            elif self.termination_type_id.id == self.env.ref(
                    'smart_hr.data_hr_ending_service_type_normal').id and self.employee_id.type_id.id == self.env.ref(
                    'smart_hr.data_salary_grid_type4').id:
                decision_type_id = self.env.ref('smart_hr.data_decision_type19').id
            elif self.termination_type_id.id == self.env.ref(
                    'smart_hr.data_hr_ending_service_type_healthy').id and self.employee_id.type_id.id == self.env.ref(
                    'smart_hr.data_salary_grid_type').id:
                decision_type_id = self.env.ref('smart_hr.data_decision_type17').id
            elif self.termination_type_id.id == self.env.ref(
                    'smart_hr.data_hr_ending_service_demision').id and self.employee_id.type_id.id == self.env.ref(
                    'smart_hr.data_salary_grid_type').id:
                decision_type_id = self.env.ref('smart_hr.data_decision_type22').id
            elif self.termination_type_id.id == self.env.ref(
                    'smart_hr.data_hr_ending_service_demision').id and self.employee_id.type_id.id == self.env.ref(
                    'smart_hr.data_salary_grid_type3').id:
                decision_type_id = self.env.ref('smart_hr.data_decision_type24').id
            elif self.termination_type_id.id == self.env.ref(
                    'smart_hr.data_hr_ending_service_absence').id and self.employee_id.type_id.id == self.env.ref(
                    'smart_hr.data_salary_grid_type').id:
                decision_type_id = self.env.ref('smart_hr.data_decision_type18').id
            elif self.termination_type_id.id == self.env.ref(
                    'smart_hr.data_hr_ending_service_absence').id and self.employee_id.type_id.id == self.env.ref(
                    'smart_hr.data_salary_grid_type3').id:
                decision_type_id = self.env.ref('smart_hr.data_decision_type23').id
            elif self.termination_type_id.id == self.env.ref('smart_hr.data_hr_ending_service_job').id:
                decision_type_id = self.env.ref('smart_hr.data_decision_type11').id
            elif self.termination_type_id.id == self.env.ref('smart_hr.data_hr_ending_service_death').id:
                decision_type_id = self.env.ref('smart_hr.data_decision_type35').id
            elif self.termination_type_id.id == self.env.ref(
                    'smart_hr.data_hr_ending_period_experience').id and self.employee_id.type_id.id == self.env.ref(
                    'smart_hr.data_salary_grid_type3').id:
                decision_type_id = self.env.ref('smart_hr.data_decision_type15').id
            elif self.termination_type_id.id == self.env.ref('smart_hr.data_hr_ending_estimite_less').id:
                decision_type_id = self.env.ref('smart_hr.data_decision_type11').id
            elif self.termination_type_id.id == self.env.ref('smart_hr.data_hr_ending_reason_todbeah').id:
                decision_type_id = self.env.ref('smart_hr.data_decision_type11').id
            if not decision_type_id:
                raise ValidationError(u'لا يوجد قرار من نوع %s  في النظام .' % self.termination_type_id.name)
            # create decission
            decission_val = {
              #  'name': self.name,
                'decision_type_id': decision_type_id,
                'date': decision_date,
                'employee_id': self.employee_id.id}
            decision = decision_obj.create(decission_val)
            decision.text = decision.replace_text(self.employee_id, decision_date, decision_type_id, 'termination')
            decission_id = decision.id
            self.decission_id = decission_id
        self.history_line_id.num_decision = self.decission_id.name
        self.history_line_id.date_decision = self.decission_id.date
        return {
            'name': _(u'قرار طى القيد'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'hr.decision',
            'view_id': self.env.ref('smart_hr.hr_decision_wizard_form').id,
            'type': 'ir.actions.act_window',
            'res_id': decission_id,
            'target': 'new'
        }


class HrTerminationType(models.Model):
    _name = 'hr.termination.type'
    _description = 'Termination Type'

    name = fields.Char(string=u'اسم')
    code = fields.Char(string=u'الرمز')
    nb_salaire = fields.Float(string=u'عدد الرواتب المستحق')
    all_holidays = fields.Boolean(string=u'كل الإجازة')
    max_days = fields.Float(string=u'الحد الاقصى لأيام الإجازة')
    nationality = fields.Boolean(string=u'غير سعودي')
    contract = fields.Boolean(string=u'متعاقد')
    evaluation_condition = fields.Boolean(string=u'يطبق شرط تقييم الأداء')
    years_progress = fields.Integer(string=u'عدد سنوات التقييم')
    evaluation_required = fields.Many2many('hr.evaluation.result.foctionality', string=u'التقييمات المطلوبة')
    include_members = fields.Boolean(string=u'تشمل اعضاء الهيئة')
    years = fields.Integer(string=u'السن')
