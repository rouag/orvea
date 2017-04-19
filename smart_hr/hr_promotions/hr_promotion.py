# -*- coding: utf-8 -*-

from openerp import models, fields, api, _, SUPERUSER_ID
from openerp.exceptions import Warning
from dateutil.relativedelta import relativedelta
from openerp.exceptions import ValidationError
from datetime import date, datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT


class HrPromotion(models.Model):
    _name = 'hr.promotion'
    _order = 'id desc'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = 'Promotion Decision'

    name = fields.Char(string=u'رقم محضر الترقيات', )
    date = fields.Date(string=u'التاريخ ', default=fields.Datetime.now())
    date_reponse_employee = fields.Date(string=u'تاريخ الأقصى لموافقة الموظف ', )
    speech_number = fields.Char(string=u'رقم الخطاب')
    speech_date = fields.Date(string=u'تاريخ الخطاب')
    speech_file = fields.Binary(string=u'نسخة الخطاب', attachment=True)
    data_name_speech = fields.Char(string='الملف')

    decision_number = fields.Char(string=u'رقم قرار الترقية')
    message = fields.Char(string=u'سبب الرفض')
    dicision_date = fields.Date(string=u'تاريخ القرار')
    dicision_file = fields.Binary(string=u'نسخة القرار', attachment=True)
    data_name_decision = fields.Char(string='الملف')

    employee_promotion_line_ids = fields.One2many('hr.promotion.employee', 'promotion_id', string=' قائمة الموظفين', )
    job_promotion_line_ids = fields.One2many('hr.promotion.job', 'promotion_id', string='قائمة الوظائف', )
    employee_job_promotion_line_ids = fields.One2many('hr.promotion.employee.job', 'promotion_id',
                                                      string=' قائمة الترشيحات', )

    emplyoee_state = fields.Boolean(string='قرار الموظف', )
    state = fields.Selection([('promotion_type', u'نوع الترقية'),
                              ('draft', u'طلب'),
                              ('job_promotion', u'الوظائف المحجوزة للترقية'),
                              ('manager', u'صاحب صلاحية التعين'),
                              ('minister', u'وزارة الخدمة المدنية'),
                              ('hrm', u'شؤون الموظفين'),
                              ('done', u'اعتمدت'),
                              ('cancel', u'ملغاة'),
                              ], string=u'الحالة', default='promotion_type', )
    department_level1_id = fields.Many2one('hr.department', string='الفرع', readonly=1, states={'promotion_type': [('readonly', 0)]})
    department_level2_id = fields.Many2one('hr.department', string='القسم', readonly=1, states={'promotion_type': [('readonly', 0)]})
    department_level3_id = fields.Many2one('hr.department', string='الشعبة', readonly=1, states={'promotion_type': [('readonly', 0)]})
    salary_grid_type_id = fields.Many2one('salary.grid.type', string='الصنف', readonly=1, states={'promotion_type': [('readonly', 0)]},)
    employee_ids = fields.Many2many('hr.employee', string='الموظفين', compute='_compute_employee_ids')

    @api.multi
    def _compute_employee_ids(self):
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
            employee_ids += dapartment.member_ids.ids
            for child in dapartment.all_child_ids:
                employee_ids += child.member_ids.ids
        if not employee_ids:
            # get all employee
            employee_ids = employee_obj.search([('employee_state', '=', 'employee')]).ids
        # filter by type
        if self.salary_grid_type_id:
            employee_ids = employee_obj.search([('id', 'in', employee_ids), ('type_id', '=', self.salary_grid_type_id.id)]).ids
        self.employee_ids = employee_ids

    @api.model
    def create(self, vals):
        ret = super(HrPromotion, self).create(vals)
        # Sequence
        vals = {}
        vals['name'] = self.env['ir.sequence'].get('hr.employee.promotion.seq')
        ret.write(vals)
        return ret

    @api.multi
    def button_confirmed(self):
        for promo in self:
            self.state = 'job_promotion'
            employee_line_list = []
            for employee_line in self.employee_promotion_line_ids:
                emp_id = self.env['hr.promotion.employee.job'].create({'employee_id': employee_line.employee_id.id,
                                                                       'old_job_id': employee_line.old_job_id.id,
                                                                       'old_number_job': employee_line.old_number_job,
                                                                       'emp_department_old_id': employee_line.emp_department_old_id.id,
                                                                       'emp_grade_id_old': employee_line.emp_grade_id_old.id,
                                                                       'promotion_id': employee_line.promotion_id.id if employee_line.promotion_id else False,
                                                                       'point_seniority': employee_line.point_seniority,
                                                                       'point_education': employee_line.point_education,
                                                                       'point_training': employee_line.point_training,
                                                                       'point_functionality': employee_line.point_functionality,
                                                                       'demande_promotion_id': employee_line.demande_promotion_id.id if employee_line.demande_promotion_id else False,
                                                                       'sum_point': employee_line.sum_point,
                                                                       })
                sanctions = self.env['hr.sanction'].search(
                    [('state', '=', 'done'), ('date_sanction_start', '>', datetime.now() + relativedelta(days=-709))])
                days = 0
                emp_id.employee_job_ids = emp_id.change_employee_id()
                if employee_line.employee_id.type_id.id == self.env.ref('smart_hr.data_salary_grid_type').id:
                    if employee_line.employee_id.sanction_ids:
                        for sanction in sanctions:
                            if sanction.state == "done":
                                for line in sanction.line_ids:
                                    if line.state == 'done':
                                        if line.employee_id.id == employee_line.employee_id.id:
                                            days_numbers = days + line.days_number
                        if days < 15:
                            emp_id.promotion_supp = True

                employee_line_list.append(emp_id.id)

        self.employee_job_promotion_line_ids = employee_line_list

    @api.one
    def button_employee_promotion(self):
        self.state = 'employee_promotion'

    @api.multi
    def button_promotion_type(self):
        employee_promotion = []
        employee_promotion_job = []
        employees = self.employee_ids
        for emp in employees:
            if emp.job_id.grade_id:
                # determiner si l'employer a une suspension
                suspend = self.env['hr.suspension'].search(
                    [('state', '=', 'done'),('employee_id', '=', emp.id), ('suspension_date', '<', date.today()),
                     ('suspension_end_id.release_date', '>', date.today())])
                # ‫استثانائية‬ ‫إجازة‬‫‬
                holidays_status_exceptiona = self.env['hr.holidays'].search(
                    [('state', '=', 'done'),('employee_id', '=', emp.id), ('date_from', '<=', date.today()), ('date_to', '>=', date.today()),
                     ('holiday_status_id.id', '=', self.env.ref('smart_hr.data_hr_holiday_status_exceptional').id)])
                # ‫دراسية‬ ‫إجازة
                holidays_status_study = self.env['hr.holidays'].search(
                    [('state', '=', 'done'),('employee_id', '=', emp.id), ('date_from', '<', date.today()), ('date_to', '<', date.today()),
                     ('holiday_status_id.id', '=', self.env.ref('smart_hr.data_hr_holiday_status_study').id),
                     ('duration', '>', 180)])
#                 مبتعث
                scholarship = self.env['hr.scholarship'].search(
                    [('state', '=', 'done'),('employee_id', '=', emp.id), ('date_from', '<', date.today()), ('date_to', '<', date.today()),
                     ('duration', '>', 180)])
#                  ‫بدورة‬‫ ‫تدريبية‬  
                training = self.env['hr.candidates'].search(
                    [('state', '=', 'done'),('employee_id', '=', emp.id), ('date_from', '<', date.today()), ('date_to', '<', date.today()),
                     ('number_of_days', '>', 180)])
                sanctions = self.env['hr.sanction.ligne'].search(
                    [('employee_id', '=', emp.id),('state', '=', 'done'), ('sanction_id.date_sanction_start', '>', datetime.now() + relativedelta(days=-354)),
                     ('type_sanction.code', '=', '3')])
                todayDate = date.today()
                deprivation_premium = False
                deprivation_premium_ids = self.env['hr.deprivation.premium.ligne'].search(
                    [('employee_id', '=', emp.id),('state', '=', 'done')])
                if deprivation_premium_ids:
                    for dep in deprivation_premium_ids:
                        dep_start_year = fields.Date.from_string(dep.deprivation_id.years_id.date_start).year
                        dep_stop_year = fields.Date.from_string(dep.deprivation_id.years_id.date_stop).year
                        if dep_start_year == todayDate.year -1 or dep_start_year == todayDate.year -1:
                            deprivation_premium = True
                            break
                days = 0
                if sanctions:
                    for sanction in sanctions:
                        days = days + sanction.days_number
                bad_evaluation = False
                employee_evaluation_id = self.env['hr.employee.evaluation.level'].search([('employee_id', '=', emp.id), ('year', '=', date.today().year - 1)], limit=1)
                if employee_evaluation_id:
                    if employee_evaluation_id.degree_id.id == self.env.ref('smart_hr.assessment_hr_bad').id:
                        bad_evaluation = True

                if not suspend and not holidays_status_exceptiona and not holidays_status_study and not scholarship and not training and days < 15 and not deprivation_premium and not bad_evaluation:
                    if emp.promotion_duration / 354 > emp.job_id.grade_id.years_job:
                            employee_promotion.append(emp)

        for emp_promotion in employee_promotion:
            regle_point = self.env['hr.evaluation.point'].search([('grade_id', '=', emp_promotion.grade_id.id)])
            demande_promotion_id = self.env['hr.promotion.employee.demande'].search(
                [('employee_id', '=', emp_promotion.id)])
            point_seniority = 0
            education_point = 0
            trining_point = 0
            point_functionality = 0
            years_supp = (emp_promotion.service_duration / 354) - emp_promotion.grade_id.years_job
            if years_supp > 0:
                for year in xrange(1, years_supp):
                    for seniority in regle_point.seniority_ids:
                        if (year >= seniority.year_from) and (year <= seniority.year_to):
                            point_seniority = point_seniority + (seniority.point)
                            point_seniority = point_seniority if point_seniority<regle_point.max_point_seniority else regle_point.max_point_seniority
            try:
                education_level_job = emp_promotion.job_id.serie_id.hr_classment_job_ids[
                    0].level_education_id.nomber_year_education
            except:
                education_level_job = False
            if education_level_job:
                for education_level_emp in emp_promotion.education_level_ids:
                    if education_level_emp.level_education_id.nomber_year_education - education_level_job > 0:
                        if education_level_emp.job_specialite:
                            if education_level_emp.level_education_id.secondary:
                                for education in regle_point.education_ids:
                                    if education.nature_education == 'after_secondry' and education.type_education == "in_speciality_job":
                                        education_point += education.year_point * (education_level_emp.nomber_year_education - education_level_job)
                                        education_point = education_point if education_point<regle_point.max_point_education else regle_point.max_point_education,
                            else:
                                for education in regle_point.education_ids:
                                    if education.nature_education == 'before_secondry' and education.type_education == "in_speciality_job":
                                        education_point += education.year_point * (education_level_emp.nomber_year_education - education_level_job)
                                        education_point = education_point if education_point<regle_point.max_point_education else regle_point.max_point_education,
                        else:
                            if education_level_emp.level_education_id.secondary:
                                for education in regle_point.education_ids:
                                    if education.nature_education == 'after_secondry' and education.type_education == "not_speciality_job":
                                        education_point += education.year_point * (education_level_emp.nomber_year_education - education_level_job)
                                        education_point = education_point if education_point<regle_point.max_point_education else regle_point.max_point_education,
                            else:
                                for education in regle_point.education_ids:
                                    if education.nature_education == 'before_secondry' and education.type_education == "not_speciality_job":
                                        education_point += education.year_point * (education_level_emp.nomber_year_education - education_level_job)
                                        education_point = education_point if education_point<regle_point.max_point_education else regle_point.max_point_education,
            trainings = self.env['hr.candidates'].search(
                [('employee_id', '=', emp_promotion.id), ('state', '=', 'done')])
            for training in trainings:
                if training.experience == 'experience_directe':
                    for trainig in regle_point.training_ids:
                        if trainig.type_training == 'direct_experience' and training.number_of_days>trainig.day_number:
                            trining_point = trining_point + trainig.point
                            trining_point = trining_point if trining_point<regle_point.max_point_training else regle_point.max_point_training
                elif training.experience == 'experience_in_directe' :
                    for trainig in regle_point.training_ids:
                        if trainig.type_training == 'indirect_experience' and training.number_of_days>trainig.day_number:
                            trining_point = trining_point + trainig.point
                            trining_point = trining_point if trining_point < regle_point.max_point_training else regle_point.max_point_training
            employee_evaluation_id1 = self.env['hr.employee.evaluation.level'].search([('employee_id', '=', emp.id), ('year', '=', date.today().year - 1)], limit=1)
            employee_evaluation_id2 = self.env['hr.employee.evaluation.level'].search([('employee_id', '=', emp.id), ('year', '=', date.today().year - 2)], limit=1)
            for eval in employee_evaluation_id1:
                for functionality in regle_point.functionality_ids:
                    if eval.degree_id.id == functionality.degree_id.id:
                        point_functionality += functionality.point
                        point_functionality =  point_functionality if point_functionality<regle_point.max_point_functionality else regle_point.max_point_functionality
            for eval in employee_evaluation_id2:
                for functionality in regle_point.functionality_ids:
                    if eval.degree_id.id == functionality.degree_id.id:
                        point_functionality += functionality.point
                        point_functionality =  point_functionality if point_functionality<regle_point.max_point_functionality else regle_point.max_point_functionality

            id_emp = self.env['hr.promotion.employee'].create({'employee_id': emp_promotion.id,
                                                                       'old_job_id': emp_promotion.job_id.id,
                                                                       'old_number_job': emp_promotion.job_id.number,
                                                                       'emp_department_old_id': emp_promotion.department_id.id,
                                                                       'emp_grade_id_old': emp_promotion.job_id.grade_id.id,
                                                                       'demande_promotion_id': demande_promotion_id[
                                                                           0].id if demande_promotion_id else False,
                                                                       'point_seniority': point_seniority,
                                                                       'point_education': education_point,
                                                                       'point_training': trining_point,
                                                                       'point_functionality': point_functionality,
                                                                       'sum_point': education_point + trining_point + point_seniority + point_functionality,
                                                                       })
            employee_promotion_job.append(id_emp.id)
        self.employee_promotion_line_ids = [(6, 0, employee_promotion_job)]
        if not employee_promotion_job:
            raise ValidationError(u"لا يوجد موظفون مؤهلون للترقية")
        job_promotion = []
        for job in self.env['hr.job'].search([('state', '=', 'unoccupied')]):
            id_job = self.env['hr.promotion.job'].create(
                {'new_job_id': job.id, 'emp_grade_id_new': job.grade_id.id, 'new_number_job': job.number})
            job_promotion.append(id_job.id)
        self.job_promotion_line_ids = [(6, 0, job_promotion)]
        if not job_promotion:
            raise ValidationError(u"لا توجد وظائف شاغرة")
        self.state = 'draft'

    @api.one
    def button_job_promotion(self):
        for promo in self:
            self.state = 'manager'
            for job in self.job_promotion_line_ids:
                if not job.job_state:
                    self.job_promotion_line_ids = [(3, job.id)]
                else:
                    job.new_job_id.occupied_promotion = True
                if not self.job_promotion_line_ids:
                    raise ValidationError(u"لم يقع إحتجاز أي وظيفة")

    @api.one
    def button_transfer_employee(self):
        self.emplyoee_state = True

        for promotion in self.employee_job_promotion_line_ids:
            if not promotion.new_job_id:
                self.employee_job_promotion_line_ids = [(3, promotion.id)]

        if not self.employee_job_promotion_line_ids:
            raise ValidationError(u"لم يقع أي إختيار وظيفة جديدة للموظف")
        if self.employee_job_promotion_line_ids:
            for promotion in self.employee_job_promotion_line_ids:
                promotion.state = "employee_confirmed"

    @api.one
    def button_transfer_minister(self):
        for promo in self:
            date_now = datetime.now()
            employee_job_promotion_line_ids = promo.employee_job_promotion_line_ids.ids
            not_answered = self.env['hr.promotion.employee.job'].search_count([('state', '=', 'employee_confirmed'), ('id', 'in', employee_job_promotion_line_ids)])
            if datetime.today().strftime('%Y-%m-%d') < self.date_reponse_employee and not_answered:
                raise ValidationError(u"يجب انتهاء فترة موافقة الموظف")
            else:
                promo.state = 'minister'
        for promotion in self.employee_job_promotion_line_ids:
            if not promotion.done:
                self.employee_job_promotion_line_ids = [(3, promotion.id)]

        if not self.employee_job_promotion_line_ids:
            raise ValidationError(u"لم يوافق أي موظف على الترقية")

    @api.one
    def button_transfer_hrm(self):
        for promo in self:
            self.state = 'hrm'

    @api.one
    @api.constrains('speech_date')
    def check_order_chek_date(self):
        if self.speech_date > datetime.today().strftime('%Y-%m-%d'):
            raise ValidationError(u"تاريخ الخطاب  يجب ان يكون أصغر من تاريخ اليوم")

    @api.multi
    def button_done(self):
            self.state = 'done'
            for emp in self.employee_job_promotion_line_ids:
                employee_hilday = self.env['hr.holidays'].search(
                    [('employee_id', '=', emp.employee_id.id), ('date_from', '<=', date.today()),
                     ('date_to', '>=', date.today())])
                if employee_hilday:
                    emp.date_direct_action = employee_hilday.date_to
                if emp.employee_id.type_id.is_member is True:
                    appoint_type = self.env.ref('smart_hr.data_hr_promotion_member').id
                else:
                    appoint_type = self.env.ref('smart_hr.data_hr_promotion_agent').id
                apoint = self.env["hr.decision.appoint"].create({'name': self.speech_number,
                                                                 'order_date': self.speech_date,
                                                                 'date_direct_action': emp.date_direct_action,
                                                                 'job_id': emp.new_job_id.id,
                                                                 'grade_id': emp.emp_grade_id_new.id,
                                                                 'type_appointment': appoint_type,
                                                                 'order_picture': self.dicision_file,
                                                                 'depend_on_test_periode': True,
                                                                 'employee_id': emp.employee_id.id,
                                                                 'promotion_id':emp.id,
                                                                 'degree_id': emp.employee_id.degree_id.id
                                                                 })
                apoint._onchange_employee_id()
                apoint._onchange_job_id()
                apoint._onchange_degree_id()
                apoint.action_done()
                #             create history_line
                self.env['hr.employee.history'].sudo().add_action_line(emp.employee_id, self.decision_number, self.date, "ترقية")
                self.env['base.notification'].create({'title': u'إشعار بالترقية',
                                                      'message': u'لقد تم ترقيتكم على وظيفة جديدة',
                                                      'user_id': emp.employee_id.user_id.id,
                                                      'show_date': datetime.now().strftime(
                                                          DEFAULT_SERVER_DATETIME_FORMAT),
                                                      'notif': True,
                                                      'res_id': self.id,
                                                      'res_action': 'smart_hr.action_hr_decision_appoint', })
                emp.employee_id.job_id.write({'state': 'unoccupied', 'category': 'unoccupied_promotion' ,'employee': False})
                for job in self.job_promotion_line_ids:
                    job.new_job_id.occupied_promotion = False

    @api.one
    def button_refuse(self):
        for promo in self:
            self.state = 'draft'
            self.employee_job_promotion_line_ids = False

    @api.one
    def button_conceled(self):
        for promo in self:
            self.state = 'draft'

    @api.multi
    def create_report_promotion(self):
        self.env['report'].get_pdf(self, 'smart_hr.hr_promotion_report')

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state not in ['draft', 'promotion_type'] and self._uid != SUPERUSER_ID:
                raise ValidationError(u'لا يمكن حذف قرار الترقية في هذه المرحلة يرجى مراجعة مدير النظام')
        return super(HrPromotion, self).unlink()


class HrPromotionLigneEmployee(models.Model):
    _name = 'hr.promotion.employee'
    _order = 'id desc'
    
    employee_id = fields.Many2one('hr.employee', string=u'الموظف')
    promotion_id = fields.Many2one('hr.promotion', string=u'الترقية ')
    demande_promotion_id = fields.Many2one('hr.promotion.employee.demande', string=u'طلب الترقية  ')
    old_job_id = fields.Many2one('hr.job', string=u'الوظيفة الحالية')
    old_number_job = fields.Char(string='رقم الوظيفة', store=True, readonly=1)
    emp_department_old_id = fields.Many2one('hr.department', string='الادارة', store=True, readonly=1)
    emp_grade_id_old = fields.Many2one('salary.grid.grade', string='المرتبةالحالية ', store=True, readonly=1)
    point_seniority = fields.Integer(string=u'نقاط الأقدمية', )
    point_education = fields.Integer(string=u'نقاط التعليم', )
    point_training = fields.Integer(string=u'نقاط التدريب', )
    point_functionality = fields.Integer(string=u'نقاط  الإداء الوظيفي', )
    sum_point = fields.Integer(string=u'المجموع', )
    emplyoee_state = fields.Boolean(string='تأجيل', )
    state = fields.Selection([('draft', u'طلب'),
                              ('done', u'اعتمدت'),
                              ], string=u'حالة', default='draft', )

    identification_id = fields.Char(string=u'رقم الهوية', related="employee_id.identification_id", readonly=1)
    begin_work_date = fields.Date(related="employee_id.begin_work_date", readonly=1)
    decision_appoint_date = fields.Date(string=u'تاريخ التحاقه بها', readonly=1,
                                        compute='_compute_decision_appoint_date')

    @api.depends('old_job_id')
    def _compute_decision_appoint_date(self):
        for promotion in self:
            appoint_id = self.env['hr.decision.appoint'].search(
                [('employee_id.id', '=', promotion.employee_id.id), ('job_id', '=', promotion.old_job_id.id)], limit=1)
            if appoint_id:
                promotion.decision_appoint_date = appoint_id.date_direct_action

    @api.multi
    def employee_pause(self):
        self.emplyoee_state = True


class HrPromotionLigneJobs(models.Model):
    _name = 'hr.promotion.job'
    _order = 'id desc'

    new_job_id = fields.Many2one('hr.job', string=u'الوظيفة المرقى عليها', domain=[('state', '=', 'unoccupied')])
    new_number_job = fields.Char(string='رقم الوظيفة', store=True, readonly=1)
    promotion_id = fields.Many2one('hr.promotion', string=u'الترقية ')
    department = fields.Many2one('hr.department', string='الادارة', store=True, readonly=1)
    emp_grade_id_new = fields.Many2one('salary.grid.grade', string='المرتبة ', store=True, readonly=1)
    job_state = fields.Boolean(string='محجوزة', )

    @api.onchange('new_job_id')
    def onchange_job_id(self):
        if self.new_job_id:
            self.emp_grade_id_new = self.new_job_id.grade_id.id
            self.new_number_job = self.new_job_id.number

    @api.multi
    def job_reserved(self):
        if self.new_job_id:
            self.job_state = True

    @api.multi
    def job_in_reserved(self):
        if self.new_job_id:
            self.job_state = False


class HrPromotionLigneEmployeeJob(models.Model):
    _name = 'hr.promotion.employee.job'
    _inherit = ['mail.thread']

    _order = 'id desc'

    @api.model
    def _getUserGroupId(self):
        job_ids = self.env['hr.job'].search(
            [('grade_id.code', '=', int(self.emp_grade_id_old.code) + 1), ('occupied_promotion', '=', True)]).ids
        job = self.env['hr.job'].search([('occupied_promotion', '=', True)])
        return [('id', 'in', job_ids)]

    employee_id = fields.Many2one('hr.employee', string=u'الموظف')
    job_promotion_id = fields.Many2one('hr.promotion.job', string=u'الوظيفة المرقى عليها', )
    promotion_id = fields.Many2one('hr.promotion', string=u'الترقية ')
    old_job_id = fields.Many2one('hr.job', string=u'الوظيفة الحالية')
    old_number_job = fields.Char(string='رقم الوظيفة', store=True, readonly=1)
    emp_department_old_id = fields.Many2one(related='employee_id.department_id', string='الادارة', store=True,
                                            readonly=1)
    emp_grade_id_old = fields.Many2one('salary.grid.grade', string='المرتبةالحالية ', store=True, readonly=1)
    point_seniority = fields.Integer(string=u'نقاط الأقدمية', )
    point_education = fields.Integer(string=u'نقاط التعليم', )
    point_training = fields.Integer(string=u'نقاط التدريب', )
    point_functionality = fields.Integer(string=u'نقاط  الإداء الوظيفي', )
    sum_point = fields.Integer(string=u'المجموع', )
    demande_promotion_id = fields.Many2one('hr.promotion.employee.demande', string=u'طلب الترقية  ')
    city_fovorite = fields.Many2one(related='demande_promotion_id.city_fovorite', string=u'المدينة المفضلة')
    employee_job_ids = fields.One2many('hr.job', 'promotion_employee_id', string=' قائمة الوظائف', )
    new_job_id = fields.Many2one('hr.job', string=u'الوظيفة المرقى عليها', )
    new_number_job = fields.Char(string='رقم الوظيفة', related='new_job_id.number')
    new_department = fields.Many2one(related='new_job_id.department_id', string='الادارة',)
    emp_grade_id_new = fields.Many2one(string='المرتبة ',related='new_job_id.grade_id')
    promotion_supp = fields.Boolean(string='علاوة إضافية', )
    date_direct_action = fields.Date(string='تاريخ مباشرة العمل', related='promotion_id.dicision_date')
    create_date = fields.Datetime(string=u'تاريخ الطلب', default=fields.Datetime.now(), )
    done = fields.Boolean(string='موافقة الموظف', )
    new_city_jobs = fields.Many2one(related='new_department.dep_city', string=u'المدينة ')
    state = fields.Selection([
        ('employee_confirmed', u' في إنتظار قرار الموظف'),
        ('done', u'موافقة'),
        ('refuse', u'رفض'),
        ('cancel', u'الغاء'),
    ], string=u'حالة', )
    emplyoee_state = fields.Boolean(related= 'promotion_id.emplyoee_state')
    done_date = fields.Date(string='تاريخ التفعيل')
    defferential_is_paied = fields.Boolean(string='defferential is paied', default=False)

    @api.multi
    def promotion_confirmed(self):
        if self.new_job_id:
            self.state = "done"
            self.done = True

    @api.multi
    def button_refuse(self):
        if self.new_job_id:
            self.new_job_id.state = 'unoccupied'
        self.state = "refuse"

    @api.multi
    def promotion_cancel(self):
        self.state = "cancel"
        appoint_id = self.env['hr.decision.appoint'].search([('promotion_id', '=', self.id)], limit=1)
        appoint_id.state = 'cancel'

    @api.onchange('employee_id')
    def change_employee_id(self):
        if self.employee_id:
            job_ids = self.env['hr.job'].search([('grade_id.code', '=', int(self.emp_grade_id_old.code) + 1)]).ids
            return job_ids

    @api.onchange('new_job_id')
    def onchange_new_job_id(self):
        res = {}

        if not self.new_job_id:
            job_ids = self.env['hr.job'].search([('grade_id.code', '=', int(self.emp_grade_id_old.code) + 1)]).ids
            res['domain'] = {'new_job_id': [('id', 'in', job_ids)]}
            return res
        if self.new_job_id:
            if int(self.new_job_id.grade_id.code) <= int(self.emp_grade_id_old.code):
                self.new_job_id = False
                warning = {'title': _('تحذير!'), 'message': _(u'يجب أن تكون المرتبة أكبر من المرتبة  الحالية')}
                return {'warning': warning}
            if int(self.new_job_id.grade_id.code) > int(self.emp_grade_id_old.code) + 1:
                self.new_job_id = False
                warning = {'title': _('تحذير!'), 'message': _(u'يجب أن تكون المرتبة أكبر من المرتبة  الحالية مباشرة ')}
                return {'warning': warning,}
            self.new_job_id.state = 'reserved'
            self.occupied_promotion = False


class HrPromotionType(models.Model):
    _name = 'hr.promotion.type'

    name = fields.Char(string=u'نوع الترقية', )
    code = fields.Char(string=u'الرمز')
    hr_allowance_type_id = fields.Many2one('hr.allowance.type', string='أنواع البدلات', )
    percent_salaire = fields.Float(string=u' علاوة إضافية نسبة من الراتب  ', )


class HrPromotionDemande(models.Model):
    _name = 'hr.promotion.employee.demande'
    _order = 'id desc'


    create_date = fields.Date(string=u'تاريخ الطلب', default=fields.Date.today())
    employee_id = fields.Many2one('hr.employee', string='صاحب الطلب',required=1, readonly=1,
                                  domain=[('emp_state', 'not in', ['suspended','terminated']), ('employee_state', '=', 'employee')],
                                  default=lambda self: self.env['hr.employee'].search([('user_id', '=', self._uid), ('emp_state', 'not in', ['suspended','terminated'])], limit=1),)
    name = fields.Char(string=u'رقم الطلب', )
    city_fovorite = fields.Many2one('res.city', string=u'المدينة المفضلة')
    hr_allowance_type_id = fields.Boolean(string='بدل طبيعة عمل', )
    old_job_id = fields.Many2one(related='employee_id.job_id', store=True, readonly=True, string=u'الوظيفة الحالية', )
    department_id = fields.Many2one(related='employee_id.department_id',readonly=True, string='الادارة', )
    state = fields.Selection([('new', u'طلب'),
                              ('waiting', 'في إنتظار الإعتماد'),
                              ('cancel', 'رفض'),
                              ('done', 'اعتمدت')], string='الحالة', readonly=1, default='new')
    done_date = fields.Date(string='تاريخ التفعيل')
    desire_ids = fields.One2many('hr.employee.promotion.desire', 'demande_promotion_id', required=1, string=u'رغبات الموظف', readonly=1, states={'new': [('readonly', 0)]})

    @api.model
    def create(self, vals):
        ret = super(HrPromotionDemande, self).create(vals)
        scholarship_ids = self.env['hr.scholarship'].search([('employee_id', '=', ret.employee_id.id),
                                                             ('date_to', '>=', fields.Date.today()),
                                                             ('state', '=', 'done')
                                                             ])
        if scholarship_ids:
            raise ValidationError(u"لا يمكن إنشاء طلب ترقية مع وجود ابتعاث ساري!") 
        # Sequence
        vals = {}
        vals['name'] = self.env['ir.sequence'].get('hr.employee.demande.promotion.seq')
        ret.write(vals)
        return ret

    @api.multi
    def button_confirmed(self):
        for promo in self:
            self.state = 'waiting'
