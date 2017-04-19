# -*- coding: utf-8 -*-

from openerp.exceptions import UserError
from openerp import models, fields, api, _
from openerp.exceptions import Warning
from dateutil.relativedelta import relativedelta
from openerp.exceptions import ValidationError
from datetime import date, datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT


class HrDecisionAppoint(models.Model):
    _name = 'hr.decision.appoint'
    _order = 'id desc'
    _inherit = ['mail.thread']
    _description = u'قرار تعيين'

    name = fields.Char(string='رقم الخطاب', required=1, states={'draft': [('readonly', 0)]})
    order_date = fields.Date(string='تاريخ الخطاب')
    date_hiring = fields.Date(string='تاريخ الطلب', default=fields.Datetime.now())
    date_hiring_end = fields.Date(string=u'تاريخ إنتهاء التعيين')
    date_direct_action = fields.Date(string='تاريخ مباشرة العمل')
    instead_exchange = fields.Boolean(string='صرف بدل تعيين')
    is_started = fields.Boolean(string=u'مباشر', default=False)
    # info about employee
    employee_id = fields.Many2one('hr.employee', string='الموظف', required=1)
    contract_id = fields.Many2one('hr.contract', string='العقد', Domain=[('state', '!=', 'close')])
    number = fields.Char(related='employee_id.number', store=True, readonly=True, string=u'الرقم الوظيفي')
    emp_code = fields.Char(string=u'رمز الوظيفة ', readonly=1)
    country_id = fields.Many2one(related='employee_id.country_id', store=True, readonly=True, string='الجنسية')
    emp_job_id = fields.Many2one('hr.job', string='الوظيفة', store=True, readonly=1)
    emp_number_job = fields.Char(string='رقم الوظيفة', store=True, readonly=1)
    emp_type_id = fields.Many2one('salary.grid.type', string='الصنف', store=True, readonly=1)
    emp_department_id = fields.Many2one('hr.department', string='الادارة', store=True, readonly=1)
    emp_grade_id = fields.Many2one('salary.grid.grade', string='المرتبة', store=True, readonly=1)
    emp_far_age = fields.Float(string=' السن الاقصى', store=True, readonly=1)
    emp_basic_salary = fields.Float(string='الراتب الأساسي', store=True, readonly=1)
    emp_degree_id = fields.Many2one('salary.grid.degree', string='الدرجة', store=True, readonly=1)
    # info about job
    job_id = fields.Many2one('hr.job', string='الوظيفة', required=1, Domain=[('state', '=', 'unoccupied')])
    passing_score = fields.Float(string=u'الدرجة المطلوبه')
    number_job = fields.Char(string='رقم الوظيفة', readonly=1)
    code = fields.Char(string=u'رمز الوظيفة ', readonly=1)
    type_id = fields.Many2one('salary.grid.type', string='الصنف', readonly=1)
    department_id = fields.Many2one('hr.department', string='الادارة', readonly=1)
    grade_id = fields.Many2one('salary.grid.grade', string='المرتبة', readonly=1)
    far_age = fields.Float(string=' السن الاقصى', readonly=1)
    basic_salary = fields.Float(string='الراتب الأساسي', readonly=1)
    transport_allow = fields.Float(string='بدل النقل', readonly=1)
    retirement = fields.Float(string='المحسوم للتقاعد', readonly=1)
    net_salary = fields.Float(string='صافي الراتب', readonly=1)
    salary_recent = fields.Float(string=' أخر راتب شهري ')
    transport_alocation = fields.Boolean(string='بدل نقل')
    transport_car = fields.Boolean(string='سيارة')
    first_appoint = fields.Boolean(string='أول تعين بالهيئة')
    option_contract = fields.Boolean(string='قرار التعاقد')
    degree_id = fields.Many2one('salary.grid.degree', string='الدرجة', required=1)
    royal_decree_number = fields.Char(string=u'رقم الأمر الملكي')
    royal_decree_date = fields.Date(string=u'تاريخ الأمر الملكي ')
    # other info
    type_appointment = fields.Many2one('hr.type.appoint', string=u'نوع التعيين', required=1,)
    description = fields.Text(string=' ملاحظات ')
    state_appoint = fields.Selection([
        ('active', u'مفعل'),
        ('close', u'مغلق'),
        ('refuse', u'مرفوض'),
        ('new', u'في الاجراء'),
    ], string=u' حالةالتعيين ', default='new',)
    state = fields.Selection([
        ('draft', u'طلب'),
        ('audit', u'تدقيق'),
        ('waiting', u'مقابلة شخصية'),
        ('manager', u'صاحب صلاحية التعين'),
        ('budget', u'رئيس الهيئة'),
        ('hrm', u'شؤون الموظفين'),
        ('civil', u'وزارة الخدمة المدنية'),
        ('direct', u'إدارة الموظف'),
        ('done', u'اعتمدت'),
        ('refuse', u'رفض'),
        ('cancel', u'ملغاة'),
    ], string=u'حالة', default='draft',)

    # attachments files
    order_picture = fields.Binary(string='صورة الخطاب',attachment=True)
    order_picture_name = fields.Char(string='صورة الخطاب')
    medical_examination_file = fields.Binary(string='وثيقة الفحص الطبي', attachment=True)
    date_medical_examination = fields.Date(string='تاريخ الفحص الطبي')
    medical_examination_name = fields.Char(string='وثيقة الفحص الطبي')
    order_enquiry_file = fields.Binary(string='طلب الاستسفار', attachment=True)
    file_salar_recent = fields.Binary(string='تعهد من الموظف', attachment=True)
    file_engagement = fields.Many2many('ir.attachment', string='إرفاق مزيد من الوثائق')
    # file_engagement = fields.Binary(string = 'تعهد من المترشح')
    number_appoint = fields.Char(string='رقم قرار التعين ')
    date_appoint = fields.Date(string='تاريخ قرار  التعين')
    file_appoint = fields.Binary(string='صورة قرار التعين', attachment=True)

    number_direct_appoint = fields.Char(string='رقم قرار المباشرة ')
    date_direct_appoint = fields.Date(string='تاريخ قرار المباشرة')
    file_direct_appoint = fields.Binary(string='صورة قرار المباشرة', attachment=True)
    file_direct_appoint_name = fields.Char(string='صورة قرار المباشرة')

    order_enquiry_file_name = fields.Char(string=' طلب الاستسفار')
    file_salar_recent_name = fields.Char(string=' تعهد من الموظف')
    file_appoint_name = fields.Char(string='اسم قرار التعين')
    degree_interview = fields.Char(string='درجة المقابلة')
    note_interview = fields.Text(string='الملاحظات')
    score = fields.Float(string=u'نتيجة المترشح')
    depend_on_test_periode = fields.Boolean(string=u'مدة التجربة', required=1, readonly=1,
                                            states={'draft': [('readonly', 0)]}, default=False)
    testing_date_from = fields.Date(string=u'مدة التجربة (من)')
    testing_date_to = fields.Date(string=u'مدة التجربة (إلى)')
    max_pension = fields.Boolean(string=u'الحد الأقصى لراتب نسبة التقاعد', related="type_appointment.max_pension",
                                 readonly=1)
    max_pension_ratio = fields.Float(string=u'نسبة الحد الأقصى (%)', related="type_appointment.max_pension_ratio",
                                     readonly=1)
    is_contract = fields.Boolean(string=u'يتطلب إنشاء عقد', related="type_appointment.is_contract")
    pension_ratio = fields.Float(string=u'نسبة التقاعد (%)')
    job_allowance_ids = fields.One2many('decision.appoint.allowance', 'job_decision_appoint_id', string=u'بدلات الوظيفة')
    decision_apoint_allowance_ids = fields.One2many('decision.appoint.allowance', 'decision_decision_appoint_id', string=u'بدلات التعين')
    location_allowance_ids = fields.One2many('decision.appoint.allowance', 'location_decision_appoint_id', string=u'بدلات المنطقة')
    is_enterview_manager = fields.Boolean(string=u'مقابلة شخصية',related="type_appointment.enterview_manager")
    defferential_is_paied = fields.Boolean(string='defferential is paied', default=False)
    done_date = fields.Date(string='تاريخ التفعيل')
    is_recrutment_decider = fields.Boolean(string='recrutment_decider', default=False)
    transfer_id = fields.Many2one('hr.employee.transfert')
    promotion_id = fields.Many2one('hr.promotion.employee.job')
    decission_id = fields.Many2one('hr.decision', string=u'القرارات')

    @api.multi
    def open_decission_appoint(self):
        decision_obj= self.env['hr.decision']
        if self.decission_id:
            decission_id = self.decission_id.id
        else :
            decision_type_id = 1
            decision_date = fields.Date.today() # new date
            if self.employee_id.gender == 'male':
                decision_type_id = self.env.ref('smart_hr.data_decision_type').id 
            if self.employee_id.gender == 'female':
                decision_type_id = self.env.ref('smart_hr.data_decision_type1').id


            # create decission
            decission_val={
                'name': self.env['ir.sequence'].get('hr.decision.appoint.seq'),
                'decision_type_id':decision_type_id,
                'date':decision_date,
                'employee_id' :self.employee_id.id }
            decision = decision_obj.create(decission_val)
            decision.text = decision.replace_text(self.employee_id,decision_date,decision_type_id,'appoint')
            decission_id = decision.id
            self.decission_id =  decission_id
        return {
            'name': _(u'قرار التعيين'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'hr.decision',
            'view_id': self.env.ref('smart_hr.hr_decision_wizard_form').id,
            'type': 'ir.actions.act_window',
            'res_id': decission_id,
            'target': 'new'
            }

    @api.multi
    @api.onchange('type_appointment')
    def _onchange_type_appointment(self):
        # get list of employee depend on type_appointment
        res = {}
        if self.type_appointment:
            type_ids = self.type_appointment.type_ids.ids
            job_ids=[]
            if self.type_appointment.id == self.env.ref('smart_hr.data_hr_new_agent_public').id: 
                employee_ids = self.env['hr.employee'].search([('type_id', 'in', type_ids), ('employee_state', 'in', ['done'])])
            else:
                employee_ids = self.env['hr.employee'].search([('type_id', 'in', type_ids), ('employee_state', 'in', ['done', 'employee'])])
            jobs = self.env['hr.job'].search([('type_id', 'in', type_ids), ('state', '=', 'unoccupied')])
            if jobs:
                job_ids = jobs.ids
            res['domain'] = {'employee_id': [('id', 'in', employee_ids.ids)], 'job_id': [('id', 'in', job_ids)]}
            return res

    @api.multi
    @api.onchange('type_appointment', 'employee_id')
    def _onchange_type_appointment_employee_id(self):
        if self.type_appointment and self.employee_id and self.type_appointment.max_pension:
            # get current basic salary of the employee (the employee have an old ta3yin)
            self.pension_ratio = self.max_pension_ratio
            salary_grid_id, basic_salary = self.employee_id.get_salary_grid_id(False)
            if salary_grid_id:
                self.basic_salary = basic_salary * self.pension_ratio / 100.0

    @api.onchange('pension_ratio')
    def _onchange_pension_ratio(self):
        if self.pension_ratio:
            if self.pension_ratio > self.max_pension_ratio:
                raise ValidationError(u"لا يمكنك تجاوز الحد الأقصى.")
            salary_grid_id, basic_salary = self.employee_id.get_salary_grid_id(False)
            if salary_grid_id:
                self.basic_salary = basic_salary * self.pension_ratio / 100.0

    @api.one
    @api.constrains('score', 'passing_score')
    def check_score(self):
        self.ensure_one()
        if self.score < self.passing_score:
            raise ValidationError(u"لا يمكن تعين عضو دون الدرجة المطلوبة")

    @api.multi
    def send_appoint_request(self):
        self.ensure_one()

        if self.type_appointment.audit:
            self.message_post(u"تم إرسال الطلب من قبل '" + u"' إلى مدقق طلبات التعين")
            self.state = 'audit'

        elif self.type_appointment.enterview_manager:
            self.message_post(u"تم إرسال الطلب من قبل '" + u"' إلى مسؤول على مقابلة شخصية")
            self.state = 'waiting'
        elif self.type_appointment.recrutment_manager:
            self.message_post(u"تم إرسال الطلب من قبل '" + u"' إلى صاحب صلاحية التعين")
            self.state = 'manager'
        elif self.type_appointment.personnel_hr:
            self.message_post(u"تم إرسال الطلب من قبل '" + u"' إلى فريق الموارد البشرية")
            self.state = 'hrm'
        elif self.type_appointment.recrutment_decider:
            self.message_post(u"تم إرسال الطلب من قبل '" + u" إلى رئيس الهئية ")
            self.state = 'budget'
        elif self.type_appointment.recrutment_decider:
            self.message_post(u"تم إرسال الطلب من قبل '" + u" إلى رئيس الهئية ")
            self.state = 'budget'
        elif self.type_appointment.direct_manager:
            self.message_post(u"تم إرسال الطلب من قبل '" + u" إلى رئيس الهئية ")
            self.state = 'direct'
        #             elif self.type_appointment == self.env.ref('sm

    # control audit group_audit_appointment
    @api.multi
    def button_accept_audit(self):
        self.ensure_one()
        if self.type_appointment.audit and self.type_appointment.enterview_manager:
            self.state = 'waiting'
        elif self.type_appointment.audit and self.type_appointment.recrutment_manager:
            self.state = 'manager'
        elif self.type_appointment.audit and self.type_appointment.recrutment_decider:
            self.state = 'budget'
        elif self.type_appointment.audit and self.type_appointment.ministry_civil:
            self.state = 'civil'
        elif self.type_appointment.audit and self.type_appointment.direct_manager:
            self.state = 'direct'


    @api.multi
    def button_refuse_audit(self):
        self.ensure_one()
        if self.type_appointment.audit:
            self.state = 'draft'

    @api.multi
    def button_accept_civil(self):
        self.ensure_one()
        if self.type_appointment.ministry_civil and self.type_appointment.personnel_hr:
            self.option_contract = True
            self.state = 'hrm'
        elif self.type_appointment.ministry_civil and self.type_appointment.direct_manager :
            self.state = 'direct'
        elif self.type_appointment.ministry_civil:
            self.action_done()

    @api.multi
    def button_refuse_civil(self):
        self.ensure_one()
        if self.type_appointment.ministry_civil:
            self.state = 'manager'

    # control enterview manager  group_enterview_manager
    @api.multi
    def button_accept_enterview_manager(self):
        self.ensure_one()
        if self.type_appointment.enterview_manager and self.type_appointment.recrutment_manager :
            self.state = 'manager'
        elif self.type_appointment.enterview_manager and self.type_appointment.recrutment_decider :
            self.state = 'budget'
        elif self.type_appointment.enterview_manager and self.type_appointment.personnel_hr :
            self.state = 'hrm'
        elif self.type_appointment.enterview_manager and self.type_appointment.ministry_civil :
            self.state = 'civil'
        elif self.type_appointment.enterview_manager and self.type_appointment.direct_manager :
            self.state = 'direct'
       
        user = self.env['res.users'].browse(self._uid)
        self.message_post(u"تمت الموافقة من قبل '" + unicode(user.name) + u"'")

    @api.multi
    def button_refuse_enterview_manager(self):
        self.ensure_one()
        if self.type_appointment.enterview_manager:
            self.state = 'refuse'

        user = self.env['res.users'].browse(self._uid)
        self.message_post(u"تم الرفض من قبل '" + unicode(user.name) + u"'")
        # # control recrutment group_recrutment_manager

    @api.multi
    def button_accept_recrutment_manager(self):
        self.ensure_one()
        if self.type_appointment.recrutment_manager and self.type_appointment.recrutment_decider:
            self.state = 'budget'
        elif self.type_appointment.recrutment_manager and self.type_appointment.personnel_hr:
            self.state = 'hrm'
        elif self.type_appointment.recrutment_manager and self.type_appointment.ministry_civil :
            self.state = 'civil'
        elif self.type_appointment.recrutment_manager and self.type_appointment.direct_manager :
            self.state = 'direct'


        user = self.env['res.users'].browse(self._uid)
        self.message_post(u"تمت الموافقة من قبل '" + unicode(user.name) + u"'")
        # if self.employee_id.age > 60 :
        #  raise ValidationError(u"الرجاء التثبت من سن المترشح تجاوز 60)")

    @api.multi
    def button_refuse_recrutment_manager(self):
        self.ensure_one()
        if self.type_appointment.recrutment_manager:
            if self.type_appointment.id == self.env.ref('smart_hr.data_hr_recrute_agent_utilisateur'):
                group_id = self.env.ref('smart_hr.group_personnel_hr')
                self.send_notification_refuse_to_group(group_id)
            if self.type_appointment.id == self.env.ref('smart_hr.data_hr_recrute_public_retraite'):
                group_id = self.env.ref('smart_hr.group_personnel_hr')
                self.send_notification_refuse_to_group(group_id)
            self.state = 'refuse'

        user = self.env['res.users'].browse(self._uid)
        self.message_post(u"تم الرفض من قبل '" + unicode(user.name) + u"'")

    @api.multi
    def button_accept_recrutment_decider(self):
        self.ensure_one()
        if self.type_appointment.recrutment_decider and self.type_appointment.personnel_hr:
            self.state = 'hrm'
            self.is_recrutment_decider = True
        elif self.type_appointment.recrutment_decider and self.type_appointment.ministry_civil :
            self.state = 'civil'
        elif self.type_appointment.recrutment_decider and self.type_appointment.direct_manager :
            self.state = 'direct'
        elif self.type_appointment.recrutment_decider:
            self.action_done()
      
        # Add to log
        user = self.env['res.users'].browse(self._uid)
        self.message_post(u"تمت الموافقة من قبل '" + unicode(user.name) + u"'")

    @api.multi
    def button_refuse_recrutment_decider(self):
        self.ensure_one()
        if self.type_appointment.recrutment_decider:
            self.state = 'refuse'
        # Add to log
        user = self.env['res.users'].browse(self._uid)
        self.message_post(u"تم الرفض من قبل '" + unicode(user.name) + u"'")

    # contyrol hr group_personnel_hr
    @api.multi
    def button_accept_personnel_hr(self):
        self.ensure_one()

        if self.type_appointment.personnel_hr and self.type_appointment.recrutment_decider and self.is_recrutment_decider == False :
            self.state = 'budget'
        elif self.type_appointment.personnel_hr and self.type_appointment.ministry_civil and not self.option_contract:
            self.state = 'civil'
        elif self.type_appointment.personnel_hr and self.type_appointment.ministry_civil and self.option_contract:
            self.state = 'direct'
        elif self.type_appointment.personnel_hr and self.type_appointment.direct_manager:
            self.state = 'direct'
        elif self.type_appointment.personnel_hr:
            self.action_done()
        user = self.env['res.users'].browse(self._uid)
        self.message_post(u"تمت الموافقة من قبل '" + unicode(user.name) + u"'")

    @api.multi
    def button_refuse_personnel_hr(self):
        self.ensure_one()
        if self.type_appointment.personnel_hr:
            self.state = 'refuse'
        # Add to log
        user = self.env['res.users'].browse(self._uid)
        self.message_post(u"تم الرفض من قبل شؤون الموظفين)")

    @api.multi
    def button_accept_direct(self):
        self.ensure_one()
        if self.type_appointment.direct_manager:
            self.action_done()
        user = self.env['res.users'].browse(self._uid)
        self.message_post(u"تمت الموافقة من قبل '" + unicode(user.name) + u"'")

    @api.model
    def control_test_periode_employee(self):
        today_date = fields.Date.from_string(fields.Date.today())
        appoints = self.env['hr.decision.appoint'].search(
            [('state', '=', 'done'), ('is_started', '=', True), ('testing_date_to', '=', today_date)])
        for line in appoints:
            title = u"' إشعار نهاية مدة التجربة'"
            msg = u"' إشعار نهاية مدة التجربة'" + unicode(line.employee_id.name) + u"'"
            group_id = self.env.ref('smart_hr.group_department_employee')
            self.send_test_periode_group(group_id, title, msg)

    @api.model
    def control_test_years_employee(self):
        today_date = fields.Date.from_string(fields.Date.today())
        employees = []
        hr_employee_configuration_id = self.env['hr.employee.configuration'].search([], limit=1)
        if hr_employee_configuration_id:
            age_member = hr_employee_configuration_id.age_member
            age_nomember = hr_employee_configuration_id.age_nomember
            for employee in self.env['hr.employee'].search([('employee_state', '=', 'employee')]):
                if employee.is_member and employee.age == age_member:
                    employees.append(employee)
                if not employee.is_member and employee.age == age_nomember:
                    employees.append(employee)
            group_id = self.env.ref('smart_hr.group_department_employee')
            for line in employees:
                title = u" إشعار بلوغ سن التقاعد" 
                msg = u"' إشعار ببلوغ الموظف   '" + unicode(line.display_name) + u"'" + u"عمر" + str(line.age) + u"'"
                self.send_test_periode_group(group_id, title, msg)
                for recipient in group_id.users:
                    self.env['base.notification'].create({'title': title,
                                                  'message': msg,
                                                  'user_id': recipient.id,
                                                  'show_date': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                                  'res_id': line.id,
                                                  'res_action': 'smart_hr.action_hr_employee_form',
                                                  'notif': True
                                                  })
    def send_test_periode_group(self, group_id, title, msg):
        '''
        @param group_id: res.groups
        '''
        for recipient in group_id.users:
            self.env['base.notification'].create({'title': title,
                                                  'message': msg,
                                                  'user_id': recipient.id,
                                                  'show_date': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                                  'res_id': self.id,
                                                  'res_action': 'smart_hr.action_hr_decision_appoint',
                                                  'notif': True
                                                  })

#     @api.model
#     def control_prensence_employee(self):
#         today_date = fields.Date.from_string(fields.Date.today())
#         appoints = self.env['hr.decision.appoint'].search(
#             [('state', '=', 'done'), ('is_started', '=', False)])
#         for appoint in appoints:
#             direct_appoint_period = appoint.type_appointment.direct_appoint_period
#             prev_days_end = fields.Date.from_string(appoint.date_direct_action) + relativedelta(
#                 days=direct_appoint_period)
#             sign_days = self.env['hr.attendance'].search_count(
#                 [('employee_id', '=', appoint.employee_id.id), ('name', '<=', str(prev_days_end))])
#             today_date = str(today_date)
#             prev_days_end = str(prev_days_end)
#             if sign_days != 0 or (today_date < prev_days_end):
#                 directs = self.env['hr.direct.appoint'].search(
#                     [('employee_id', '=', appoint.employee_id.id), ('state', '=', 'waiting')], limit=1)
#                 if directs:
#                     for rec in directs:
#                         rec.write({'state_direct': 'confirm'})
#                         group_id = self.env.ref('smart_hr.group_personnel_hr')
#                         self.send_notification_to_group(group_id)
# 
#             if sign_days == 0 or (today_date > prev_days_end):
#                 directs = self.env['hr.direct.appoint'].search(
#                     [('employee_id', '=', appoint.employee_id.id), ('state', '=', 'waiting')], limit=1)
#                 if directs:
#                     for rec in directs:
#                         rec.write({'state_direct': 'cancel'})
#                         group_id = self.env.ref('smart_hr.group_personnel_hr')
#                         self.send_notification_refuse_to_group(group_id)

    @api.model
    def update_appoint_direct_action(self):
        today_date = fields.Date.from_string(fields.Date.today())
        for appoint in self.search([('state', '=', 'done'), ('state_appoint', '=', 'active')]):
            if appoint.date_direct_action:
                if fields.Date.from_string(appoint.date_direct_action) == today_date:
                    title = u" إشعار بحلول تاريخ مباشرة تعيين"
                    msg = u" تاريخ مباشرة" + unicode(appoint.employee_id.display_name) + u"حل"
                    group_id = self.env.ref('smart_hr.group_department_employee')
                    self.send_appoint_group(group_id, title, msg)
  
    @api.multi
    def button_refuse_direct(self):
        self.ensure_one()
        if self.type_appointment.direct_manager:
            self.state = 'refuse'
        # Add to log
        user = self.env['res.users'].browse(self._uid)
        self.message_post(u"تم الرفض  من قبل '" + unicode(user.name) + u"'")

    @api.multi
    def action_done(self):
        self.ensure_one()
        self.state = 'done'
        # send notification to hr personnel
        user = self.env['res.users'].browse(self._uid)
        self.message_post(u"تمت إحداث تعين جديد '" + unicode(user.name) + u"'")

    @api.multi
    def action_activate(self):
        # create payroll changement history for the employee
        changement_id = self.env['hr.employee.payroll.changement'].create({'employee_id': self.employee_id.id,
                                                           'date': fields.Date.today(),
                                                           'type_id': self.type_id.id,
                                                           'grade_id': self.grade_id.id,
                                                           'degree_id': self.degree_id.id})
        grid_id, basic_salary = self.employee_id.get_salary_grid_id(False)
        if not grid_id:
            raise ValidationError(u"يجب إنشاء سلم رواتب موافق لبيانات عمل الموظف!")
        self.env['hr.holidays']._init_balance(self.employee_id)
        grade_id = int(self.emp_job_id.grade_id.code)
        new_grade_id = int(self.grade_id.code)
        # remettre compteur à 0 si sollam a changé ou martaba a changé ou kén 3odhw asb7a idéri
        if self.job_id.type_id != self.emp_job_id.type_id or (grade_id != new_grade_id):
            self.employee_id.promotion_duration = 0
            holiday_balance = self.env['hr.employee.holidays.stock'].search([('employee_id', '=', self.employee_id.id),
                                                                             ('holiday_status_id', '=', self.env.ref('smart_hr.data_hr_holiday_status_normal').id),],limit=1)
            if holiday_balance:
                holiday_balance.holidays_available_stock = 0
                holiday_balance.token_holidays_sum = 0
                if holiday_balance.period_id:
                    holiday_balance.period_id.holiday_stock = 0
        self.employee_id.write({'employee_state': 'employee',
                                'job_id': self.job_id.id,
                                'department_id': self.department_id.id,
                                'degree_id': self.degree_id.id,
                                'type_id': self.type_id.id,
                                'grade_id': self.grade_id.id,
                                'royal_decree_number': self.royal_decree_number,
                                'royal_decree_date': self.royal_decree_date,

                                })
        # check if the employee have allready a number 
        if not self.employee_id.number:
            number_id = self.env['hr.employee.configuration'].search([], limit=1)
            if number_id:
                number = number_id.number + 1
                self.employee_id.write({'number': number})
                number_id.write({'number': number})
        if self.date_medical_examination:
            self.employee_id.write({'medical_exam': self.date_medical_examination})
        if self.type_appointment.id in (self.env.ref('smart_hr.data_hr_promotion_agent').id, self.env.ref('smart_hr.data_hr_promotion_member').id):
            category = "occupied_promotion"
        elif self.type_appointment.id in [self.env.ref('smart_hr.data_hr_recrute_from_transfert').id]:
            category = "occupied_transfer"
        else:
            category = "occupied_appoint"
        self.job_id.write(
            {'state': 'occupied', 'employee': self.employee_id.id, 'occupied_date': fields.Datetime.now(), 'category': category})
        if self.max_pension:
            self.employee_id.write({'basic_salary': self.basic_salary})
        else:
            self.employee_id.write({'basic_salary': 0.0})
        self.done_date = fields.Date.today()
        # close last active appoint for the employee
        last_appoint = self.employee_id.decision_appoint_ids.search(
            [('state_appoint', '=', 'active'), ('is_started', '=', True)], limit=1)
        if last_appoint:
            last_appoint.write({'state_appoint': 'close', 'date_hiring_end': fields.Datetime.now()})

        # update holidays balance for the employee
        self.env['hr.employee.history'].sudo().add_action_line(self.employee_id, self.name, self.date_hiring, "تعيين")
        # add allowance to the employee
        for rec in self.job_allowance_ids:
            self.env['hr.employee.allowance'].create({'employee_id': self.employee_id.id,
                                                      'allowance_id': rec.allowance_id.id,
                                                      'amount': rec.amount,
                                                      'salary_grid_detail_id': grid_id.id,
                                                      'date': fields.Date.from_string(fields.Date.today())
                                                      })
        for rec in self.location_allowance_ids:
            self.env['hr.employee.allowance'].create({'employee_id': self.employee_id.id,
                                                      'allowance_id': rec.allowance_id.id,
                                                      'amount': rec.amount,
                                                      'salary_grid_detail_id': grid_id.id,
                                                      'date': fields.Date.from_string(fields.Date.today())
                                                      })

        self.done_date = fields.Date.today()
        if grade_id < new_grade_id:
            today_date = fields.Date.from_string(fields.Date.today())
            employee_lend = self.env['hr.employee.lend'].search([('employee_id', '=', self.employee_id.id),('insurance_entity.company_type','!=','inter_reg_org'),('state','=','done'),('date_to','<',today_date)],limit=1)
            if employee_lend:
                employee_lend.state = 'sectioned'
        self.is_started = True
        self.state_appoint = 'active'

    def send_notification_refuse_to_group(self, group_id):
        for recipient in group_id.users:
            self.env['base.notification'].create({'title': u'إشعار بعدم مباشرة التعين',
                                                  'message': u'لقد تم إشعار بعدم مباشرة التعين',
                                                  'user_id': recipient.id,
                                                  'show_date': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                                  'res_id': self.id,
                                                  'res_action': 'smart_hr.action_hr_decision_appoint',
                                                  'notif': True
                                                  })

    def send_notification_to_group(self, group_id):
        '''
        @param group_id: res.groups
        '''
        for recipient in group_id.users:
            self.env['base.notification'].create({'title': u' إشعار بمباشرة التعين  ',
                                                  'message': u'لقد تم  المباشرة ',
                                                  'user_id': recipient.id,
                                                  'show_date': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                                  'res_id': self.id,
                                                  'res_action': 'smart_hr.action_hr_decision_appoint',
                                                  'notif': True
                                                  })

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        if self.employee_id.number:
            self.number = self.employee_id.number
        self.country_id = self.employee_id.country_id
        self.emp_job_id = self.employee_id.job_id.id
        self.emp_code = self.employee_id.job_id.name.number
        self.emp_number_job = self.employee_id.job_id.number
        self.emp_type_id = self.employee_id.type_id.id
        self.emp_far_age = self.employee_id.type_id.far_age
        self.emp_grade_id = self.employee_id.grade_id.id
        self.emp_degree_id = self.employee_id.degree_id.id
        self.emp_department_id = self.employee_id.department_id.id

    @api.onchange('job_id')
    def _onchange_job_id(self):
            self.number_job = self.job_id.number
            self.code = self.job_id.name.number
            self.type_id = self.job_id.type_id.id
            self.far_age = self.job_id.type_id.far_age
            self.grade_id = self.job_id.grade_id.id
            self.department_id = self.job_id.department_id.id
            location_allowance_ids = []
            for rec in self.department_id.dep_side.allowance_ids:
                location_allowance_ids.append({'location_decision_appoint_id': self.id,
                                               'allowance_id': rec.id,
                                               'compute_method': 'amount',
                                               'amount': 0.0})
            self.location_allowance_ids = location_allowance_ids
            job_allowance_ids = []
            for rec in self.job_id.serie_id.allowanse_ids:
                job_allowance_ids.append({'decision_appoint_id': self.id,
                                          'allowance_id': rec.id,
                                          'compute_method': 'amount',
                                          'amount': 0.0})
            self.job_allowance_ids = job_allowance_ids

    @api.onchange('degree_id')
    def _onchange_degree_id(self):
        if self.degree_id:
            salary_grid_line = self.env['salary.grid.detail'].search([('type_id', '=', self.type_id.id),
                                                                      ('grade_id', '=', self.grade_id.id),
                                                                      ('degree_id', '=', self.degree_id.id)
                                                                      ])
            if not salary_grid_line:
                raise ValidationError(u"يجب تحديد سلم الرواتب المناسب لصنف و المرتبة و الدرجة")
            salary_grid_line = salary_grid_line[0]
            if salary_grid_line and not self.type_appointment.max_pension:
                self.basic_salary = salary_grid_line.basic_salary
                self.transport_allow = salary_grid_line.transport_allowance_amout
                self.retirement = self.basic_salary * salary_grid_line.retirement / 100.0
                self.net_salary = salary_grid_line.net_salary

    @api.onchange('date_direct_action')
    @api.constrains('date_direct_action')
    def _onchange_date_direct_action(self):
        if self.date_direct_action:
            if self.date_hiring > self.date_direct_action:
                raise ValidationError(u"تاريخ مباشرة العمل يجب ان يكون أكبر من تاريخ التعيين")
            is_holiday = self.env['hr.smart.utils'].check_holiday_weekend_days(self.date_direct_action, self.employee_id)
            if is_holiday:
                if is_holiday == "official holiday":
                    raise ValidationError(u"هناك تداخل فى تاريخ المباشرة مع اعياد و عطل رسمية")
                elif is_holiday == "weekend":
                    raise ValidationError(u"هناك تداخل فى تاريخ المباشرة مع عطلة نهاية الاسبوع")
                elif is_holiday == "holiday":
                    raise ValidationError(u"هناك تداخل فى تاريخ المباشرة مع يوم إجازة")        

    @api.onchange('date_hiring_end')
    def _onchange_date_hiring_end(self):
        if self.date_hiring_end:
            if self.date_hiring > self.date_hiring_end:
                raise ValidationError(u"تاريخ إنتهاء التعيين يجب ان يكون أكبر من تاريخ التعيين")

    @api.one
    @api.constrains('order_date')
    def check_order_date(self):
        if self.order_date > datetime.today().strftime('%Y-%m-%d'):
            raise ValidationError(u"تاريخ الخطاب  يجب ان يكون أصغر من تاريخ اليوم")
    

    @api.one
    @api.constrains('date_direct_action', 'date_hiring')
    def check_dates_periode(self):
        if self.date_direct_action:
            if self.date_hiring > self.date_direct_action:
                raise ValidationError(u"تاريخ مباشرة العمل يجب ان يكون أكبر من تاريخ التعيين")

    @api.one
    @api.constrains('date_hiring', 'date_hiring_end')
    def check_dates_end(self):
        if self.date_hiring_end:
            if self.date_hiring > self.date_hiring_end:
                raise ValidationError(u"تاريخ إنتهاء التعيين يجب ان يكون أكبر من تاريخ التعيين")

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_(u'لا يمكن حذف قرار  التعين  إلا في حالة طلب !'))
            
        return super(HrDecisionAppoint, self).unlink()


class HrTypeAppoint(models.Model):
    _name = 'hr.type.appoint'
    _description = u'أنواع التعين'

    name = fields.Char(string='النوع', required=1)
    date_test = fields.Char(string='فترة التجربة')
    code = fields.Char(string='الرمز')
    audit = fields.Boolean(string=u'تدقيق')
    show_in_apoint = fields.Boolean(string=u'إظهار في تعيين', default=True)
    is_contract = fields.Boolean(string=u'يتطلب إنشاء عقد', default=False)
    recrutment_manager = fields.Boolean(string=u'موافقة صاحب صلاحية التعين ')
    enterview_manager = fields.Boolean(string=u'مقابلة شخصية')
    personnel_hr = fields.Boolean(string=u'شؤون الموظفين')
    direct_manager = fields.Boolean(string=u'  موافقة إدارة الموظف ')
    recrutment_decider = fields.Boolean(string=u' موافقة رئيس الهيئة  ')
    ministry_civil = fields.Boolean(string=u' موافقة وزارة الخدمة المدنية')
    can_be_cancelled = fields.Boolean(string=u'يمكن الغاؤها')
    hr_allowance_appoint_id = fields.One2many('hr.allowance.appoint', 'appoint_type_id', string='البدلات')
    direct_appoint_period = fields.Float(string=u'فترة مهلة المباشرة')
    max_pension = fields.Boolean(string=u'الحد الأقصى لراتب نسبة التقاعد', default=False)
    max_pension_ratio = fields.Float(string=u'نسبة الحد (%)', default=40)
    type_ids = fields.Many2many('salary.grid.type', string=u'الاصناف')


class HrAllowanceAppoint(models.Model):
    _name = 'hr.allowance.appoint'
    _description = u'بدل التعين'
    hr_allowance_type_id = fields.Many2one('hr.allowance.type', string=u'بدل التعيين')
    salary_number = fields.Float(string=u'عدد الرواتب')
    appoint_type_id = fields.Many2one('hr.type.appoint', string=u'نوع التعين')


class DecisionAppointAllowance(models.Model):
    _name = 'decision.appoint.allowance'
    _description = u'بدلات التعين والوظيفة'

    job_decision_appoint_id = fields.Many2one('hr.decision.appoint', string='التعين', ondelete='cascade')
    decision_decision_appoint_id = fields.Many2one('hr.decision.appoint', string='التعين', ondelete='cascade')
    location_decision_appoint_id = fields.Many2one('hr.decision.appoint', string='التعين', ondelete='cascade')
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
        appoint_id = self.job_decision_appoint_id
        if self.decision_decision_appoint_id:
            appoint_id = self.decision_decision_appoint_id
        if self.location_decision_appoint_id:
            appoint_id = self.location_decision_appoint_id

        employee = appoint_id.employee_id
        ttype = employee.job_id.type_id
        grade = employee.job_id.grade_id
        degree = employee.degree_id
        amount = 0.0
        # search the correct salary_grid for this employee
        if employee:
            if appoint_id.type_id:
                type_id = appoint_id.type_id
            else:
                raise ValidationError(_(u' الرجاء ادخال الصنف  !'))
            if appoint_id.degree_id:
                degree_id = appoint_id.degree_id
            else:
                raise ValidationError(_(u' الرجاء ادخال الدرجة  !'))
            grade_id = appoint_id.grade_id
            salary_grids, basic_salary = self.get_salary_grid_id(employee, type_id, grade_id, degree_id, False)
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
        else:
            raise ValidationError(_(u'لا يوجد موظف. !'))

