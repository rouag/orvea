# -*- coding: utf-8 -*-


from openerp import models, fields, api, _
from openerp.addons.smart_base.util.umalqurra import *
from openerp.exceptions import ValidationError
from umalqurra.hijri_date import HijriDate


class HrDecision(models.Model):
    _name = 'hr.decision'
    _inherit = ['mail.thread']
    _description = u'القرار'

    name = fields.Char(string='قرار إداري رقم', readonly=1)
    decision_type_id = fields.Many2one('hr.decision.type', string='نوع القرار', required=1, readonly=1, states={'draft': [('readonly', 0)]})
    date = fields.Date(string='بتاريخ', required=1, readonly=1, states={'draft': [('readonly', 0)]})
    employee_id = fields.Many2one('hr.employee', string='الموظف', readonly=1, states={'draft': [('readonly', 0)]})
    text = fields.Html(string='نص القرار', readonly=1, states={'draft': [('readonly', 0)]})
    num_speech = fields.Char(string='رقم الخطاب', readonly=1, states={'draft': [('readonly', 0)]})
    date_speech = fields.Date(string='تاريخ الخطاب', readonly=1, states={'draft': [('readonly', 0)]})
    employee_ids = fields.Many2many('hr.employee', string='الاعضاء المرقين')
    state = fields.Selection([('draft', u'جديد'),
                              ('done', u'اعتمدت'),
                              ('cancel', u'ملغاة'),
                              ], string=u'حالة', default='draft')

    #     @api.onchange('num_speech', 'date_speech', 'name', 'date')
    #     def onchange_fileds(self):
    #         self.onchange_decision_type_id()
    #
    #     @api.onchange('date_speech')
    #     def onchange_date_speech(self):
    #         self.onchange_decision_type_id()

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise ValidationError(u'لا يمكن حذف القرار فى هذه المرحلة يرجى مراجعة مدير النظام')
        return super(HrDecision, self).unlink()

    def _get_hijri_date(self, date, separator):
        '''
        convert georging date to hijri date
        :return hijri date as a string value
        '''
        if date:
            date = fields.Date.from_string(date)
            hijri_date = HijriDate(date.year, date.month, date.day, gr=True)
            return str(int(hijri_date.year)) + separator + str(int(hijri_date.month)).zfill(2) + separator + str(
                int(hijri_date.day)).zfill(2)
        return None

    @api.onchange('decision_type_id')
    def onchange_decision_type_id(self):
        type= False
        if self.decision_type_id in [self.env.ref('smart_hr.data_decision_type6'),
                                    self.env.ref('smart_hr.data_decision_type8'),
                                    self.env.ref('smart_hr.data_decision_type10')]:
            object_type = 'employee'
            self.text = self.replace_text(self.employee_id, self.date,self.decision_type_id.id,'employee')

        if self.decision_type_id in [self.env.ref('smart_hr.data_hr_ending_service_death'),
                                     self.env.ref('smart_hr.data_decision_type11'),
                                     self.env.ref('smart_hr.data_decision_type14'),
                                     self.env.ref('smart_hr.data_decision_type19'),
                                     self.env.ref('smart_hr.data_decision_type17'),
                                     self.env.ref('smart_hr.data_decision_type22'),
                                     self.env.ref('smart_hr.data_decision_type24'),
                                     self.env.ref('smart_hr.data_decision_type18'),
                                     self.env.ref('smart_hr.data_decision_type23'),
                                    self.env.ref('smart_hr.data_decision_type35'),
                                    self.env.ref('smart_hr.data_decision_type15'),
                                     ]:

   
            object_type = 'termination'
            self.text = self.replace_text(self.employee_id, self.date,self.decision_type_id.id,'termination')

        if self.decision_type_id in [self.env.ref('smart_hr.data_normal_leave'),
                                    self.env.ref('smart_hr.data_exceptionnel_leave'),
                                    self.env.ref('smart_hr.data_leave_satisfactory'),
                                    self.env.ref('smart_hr.data_leave_escort'),
                                    self.env.ref('smart_hr.data_leave_sport'),
                                    self.env.ref('smart_hr.data_leave_motherhood')

                                             ]:
            object_type= 'holidays'
            self.text = self.replace_text(self.employee_id, self.date,self.decision_type_id.id,'holidays')

        if self.decision_type_id in [self.env.ref('smart_hr.data_decision_type45'),
                                                self.env.ref('smart_hr.data_decision_type44'),
                                            ]:
            object_type = 'holidays_cancellation'
            self.text = self.replace_text(self.employee_id, self.date, self.decision_type_id.id, 'holidays_cancellation')

        if self.decision_type_id:
            object_type = 'appoint'
            self.text = self.replace_text(self.employee_id, self.date,self.decision_type_id.id,'appoint')

        if self.decision_type_id in [self.env.ref('smart_hr.data_employee_commissioning'),
                                            ]:
            object_type = 'commissioning'
            self.text = self.replace_text(self.employee_id, self.date, self.decision_type_id.id, 'commissioning')

        if self.decision_type_id in [self.env.ref('smart_hr.data_employee_scholarship'),
                                            ]:
            object_type = 'scholarship'
            self.text = self.replace_text(self.employee_id, self.date, self.decision_type_id.id, 'scholarship')

        if self.decision_type_id in [self.env.ref('smart_hr.data_employee_trasfert'),
                                            ]:
            object_type = 'transfert'
            self.text = self.replace_text(self.employee_id, self.date, self.decision_type_id.id, 'transfert')

        if self.decision_type_id in [self.env.ref('smart_hr.data_decision_type7'),
                                    self.env.ref('smart_hr.data_decision_type9'),
                                            ]:
            object_type = 'improve'
            self.text = self.replace_text(self.employee_id, self.date, self.decision_type_id.id, 'improve')

        if self.decision_type_id in [self.env.ref('smart_hr.data_employee_lend'),
                          ]:
            object_type = 'lend'
            self.text = self.replace_text(self.employee_id, self.date, self.decision_type_id.id, 'lend')





    @api.multi
    def button_done(self):
        self.name = self.env['ir.sequence'].get('hr.decision.seq')
        self.state = 'done'

    @api.multi
    def button_refuse(self):
        return True

    def replace_text(self, employee_id, date, decision_type_id , object_type ,args={}):

        decision_text =''
        decision_type_line = self.env['hr.decision.type'].search([('id', '=', decision_type_id)])
        if decision_type_line.text:
            decision_text = decision_type_line.text
            numero = self.name or ""  
            decision_text = decision_text.replace('NUMERO', unicode(numero))
            for key, values in args.items():
                if key =="DATE":
                    date = values
                    if date:
                        hijri_date = self._get_hijri_date(date, '-')
                        date = str(hijri_date).split('-')
                        date = date[2] + '-' + date[1] + '-' + date[0] or ""   
                    decision_text = decision_text.replace(key, unicode(date))
                else :
                    decision_text = decision_text.replace(key, unicode(values))

            if employee_id :
                if date:
                    hijri_date = self._get_hijri_date(date, '-')
                    dates = str(hijri_date).split('-')
                    dattz = dates[2] + '-' + dates[1] + '-' + dates[0] or ""
                employee = employee_id.display_name or ""
                carte_id = employee_id.identification_id or ""
                if employee_id.birthday:
                    birthday_hijri = self._get_hijri_date(employee_id.birthday, '-')
                    birthdays = str(birthday_hijri).split('-')
                    birthday = birthdays[2] + '-' + birthdays[1] + '-' + birthdays[0] or ""
                emp_city = employee_id.dep_city.name or ""
                numero = self.name or ""
                num_speech = self.num_speech or ""
                #information employee  old job
                job_id = employee_id.job_id.name.name or ""
                number = employee_id.job_id.name_number or ""
                code = employee_id.job_id.number or ""
                department_id = employee_id.department_id.name or ""
                type_job_id = employee_id.type_id.name or ""
                grade_id = employee_id.grade_id.name or ""
                degree_id = employee_id.degree_id.name or ""
                salary_grid_id, basic_salary = employee_id.get_salary_grid_id(False)
                salary = salary_grid_id.net_salary  or ""

                rel_text = decision_type_line.text

                decision_text = decision_text.replace('EMPLOYEE', unicode(employee))
                decision_text = decision_text.replace('BIRTHDAY', unicode(birthday))
                decision_text = decision_text.replace('DATE', unicode(dattz))
                decision_text = decision_text.replace('CARTEID', unicode(carte_id))
                decision_text = decision_text.replace('NUMBER',unicode(number))
                decision_text = decision_text.replace('BASICSALAIRE',unicode(salary))
                decision_text = decision_text.replace('NUMERO', unicode(numero))
                decision_text = decision_text.replace('JOB', unicode(job_id))
                decision_text = decision_text.replace('CODE', unicode(code))
                decision_text = decision_text.replace('DEGREE', unicode(degree_id))
                decision_text = decision_text.replace('GRADE', unicode(grade_id))
                decision_text = decision_text.replace('DEPARTEMENT', unicode(department_id))

                if object_type == 'holidays' :
                    
                    holidays_line = self.env['hr.holidays'].search([('employee_id', '=', employee_id.id), ('state', '=', 'done')], limit=1)
                    if holidays_line :
                        duration = holidays_line.duration or ""
                        if holidays_line.date_from:
                            date_from = self._get_hijri_date(holidays_line.date_from, '-')
                            date_from = str(date_from).split('-')
                            date_from = date_from[2] + '-' + date_from[1] + '-' + date_from[0] or ""
                        fromdate = date_from or ""
                        if holidays_line.date_to:
                            date_to = self._get_hijri_date(holidays_line.date_to, '-')
                            date_to = str(date_to).split('-')
                            date_to = date_to[2] + '-' + date_to[1] + '-' + date_to[0] or ""
                        date_to = date_to or ""
                        decision_text = decision_text.replace('DURATION', unicode(duration))
                        decision_text = decision_text.replace('FROMDET', unicode(fromdate))
                        decision_text = decision_text.replace('ENDDET', unicode(date_to))

                if object_type == 'holidays_cancellation' :
                    holidays_line = self.env['hr.holidays.cancellation'].search([('employee_id', '=', employee_id.id), ('state', '=', 'done')], limit=1)
                    if holidays_line :
                        duration = holidays_line.duration or ""
                        type_holidays = holidays_line
                        if holidays_line.date_from:
                            date_from = self._get_hijri_date(holidays_line.date_from, '-')
                            date_from = str(date_from).split('-')
                            date_from = date_from[2] + '-' + date_from[1] + '-' + date_from[0] or ""
                        fromdate = date_from or ""
                        if holidays_line.date_to:
                            date_to = self._get_hijri_date(holidays_line.date_to, '-')
                            date_to = str(date_to).split('-')
                            date_to = date_to[2] + '-' + date_to[1] + '-' + date_to[0] or ""
                        date_to = date_to or ""
                        decision_text = decision_text.replace('DURATION', unicode(duration))
                        decision_text = decision_text.replace('FROMDET', unicode(fromdate))
                        decision_text = decision_text.replace('ENDDET', unicode(date_to)) 





                if object_type == 'lend' :
                    lend_line = self.env['hr.employee.lend'].search([('employee_id', '=', employee_id.id), ('state', '=', 'done')], limit=1)
                    if lend_line :
                        duration = lend_line.duration or ""
                        decision_text = decision_text.replace('DURATION', unicode(duration))

                if object_type == 'termination' :
                    termination_line = self.env['hr.termination'].search([('employee_id', '=', employee_id.id), ('state', '=', 'done')], limit=1)
                    if termination_line :

                        if termination_line.date_termination:
                            date_termination = self._get_hijri_date(termination_line.date_termination, '-')
                            date_termination = str(date_termination).split('-')
                            date_termination = date_termination[2] + '-' + date_termination[1] + '-' + date_termination[0] or ""
                        date_termination = date_termination or ""
                        decision_text = decision_text.replace('TERMINATION', unicode(date_termination))

                if object_type == 'commissioning' :
                    commissioning_line = self.env['hr.employee.commissioning'].search([('employee_id', '=', employee_id.id),('state', '=', 'done')], limit=1)
                    if commissioning_line :
                        duration = commissioning_line.duration or ""
                        job_id = commissioning_line.commissioning_job_id.name.name or ""
                        code = commissioning_line.commissioning_job_id.number or ""
                        department_id = commissioning_line.commissioning_job_id.department_id.name or ""
                        type_id = commissioning_line.type_id.name or ""
                        grade_id = commissioning_line.grade_id.name or ""
                        decision_text = decision_text.replace('job', unicode(job_id))
                        decision_text = decision_text.replace('code', unicode(code))
                        decision_text = decision_text.replace('grade', unicode(grade_id))
                        decision_text = decision_text.replace('DURATION', unicode(duration))
                        
                if object_type == 'scholarship' :
                    scholarship_line = self.env['hr.scholarship'].search([('employee_id', '=', employee_id.id),('state', '=', 'done')], limit=1)
                    if scholarship_line :
                        diplom_id = scholarship_line.diplom_id.name or ""
                        faculty_id = scholarship_line.faculty_id.name or ""
                        country_id = scholarship_line.faculty_id.country_id.name or ""
                        duration = scholarship_line.duration or ""
                        if scholarship_line.date_from:
                            date_from = self._get_hijri_date(scholarship_line.date_from, '-')
                            date_from = str(date_from).split('-')
                            date_from = date_from[2] + '-' + date_from[1] + '-' + date_from[0] or ""
                        fromdate = date_from or ""
                        if scholarship_line.date_to:
                            date_to = self._get_hijri_date(scholarship_line.date_to, '-')
                            date_to = str(date_to).split('-')
                            date_to = date_to[2] + '-' + date_to[1] + '-' + date_to[0] or ""
                        date_to = date_to or ""
    
                        decision_text = decision_text.replace('DIPLOME', unicode(diplom_id))
                        decision_text = decision_text.replace('FACULTY', unicode(faculty_id))
                        decision_text = decision_text.replace('CONTRY', unicode(country_id))
                        decision_text = decision_text.replace('DURATION', unicode(duration))
                        decision_text = decision_text.replace('FROMDET', unicode(fromdate))
                        decision_text = decision_text.replace('ENDDET', unicode(date_to))
    
    
    
                if object_type =='appoint':
                    appoint_line = self.env['hr.decision.appoint'].search([('employee_id', '=', employee_id.id),('state', '=', 'done')], limit=1)
                    if appoint_line :
                        emp_job_id = appoint_line.emp_job_id.name.name or ""
                        emp_number_job = appoint_line.emp_number_job or ""
                        emp_code = appoint_line.emp_code or ""
                        emp_department_id = appoint_line.emp_department_id.name or ""
                        emp_type_id = appoint_line.emp_type_id.name or ""
                        emp_grade_id = appoint_line.emp_grade_id.name or ""
                        emp_degree_id = appoint_line.emp_degree_id.name or ""
                        emp_basic_salary = appoint_line.emp_basic_salary   or ""
                        decision_text = decision_text.replace('job', unicode(emp_job_id))
                        decision_text = decision_text.replace('code', unicode(emp_code))
                        decision_text = decision_text.replace('numero', unicode(emp_number_job))
                        decision_text = decision_text.replace('degree', unicode(emp_degree_id))
                        decision_text = decision_text.replace('grade', unicode(emp_grade_id))
                        decision_text = decision_text.replace('basicsalaire', unicode(emp_basic_salary))
                        decision_text = decision_text.replace('department', unicode(emp_department_id))
    
                if object_type == 'improve':
                    improve_line = self.env['hr.improve.situation'].search([('employee_id', '=', employee_id.id), ('state', '=', 'done')], limit=1)
                    if improve_line :
                        new_job_id = improve_line.new_job_id.name.name or ""
                        new_code = improve_line.new_job_id.number or ""
                        new_department_id = improve_line.department_id1.name or ""
                        new_grade_id = improve_line.grade_id1.name or ""
                        new_degree_id = improve_line.degree_id1.name or ""
                        job_id = improve_line.job_id.name.name or ""
                        number = improve_line.job_id.number or ""
                        code = improve_line.job_id.number or ""
                        department_id = improve_line.department_id.name or ""
                        grade_id = improve_line.grade_id.name or ""
                        degree_id = improve_line.degree_id.name or ""
                        #decision_text = decision_text.replace('TERMINATION', unicode(date_termination))
                        decision_text = decision_text.replace('JOB', unicode(new_job_id))
                        decision_text = decision_text.replace('CODE', unicode(new_code))
                        decision_text = decision_text.replace('DEGREE', unicode(new_degree_id))
                        decision_text = decision_text.replace('GRADE', unicode(new_grade_id))
                        decision_text = decision_text.replace('DEPARTEMENT', unicode(new_department_id))
                        decision_text = decision_text.replace('job', unicode(job_id))
                        decision_text = decision_text.replace('code', unicode(code))
                        decision_text = decision_text.replace('degree', unicode(degree_id))
                        decision_text = decision_text.replace('grade', unicode(grade_id))
                        decision_text = decision_text.replace('department', unicode(department_id))
                if object_type == 'transfert':
                    transfert_line = self.env['hr.employee.transfert'].search([('employee_id', '=', employee_id.id), ('state', '=', 'done')], limit=1)
                    if transfert_line :
                        job_id = transfert_line.job_id.name.name or ""
                        code = transfert_line.job_id.number or ""
                        department_id = transfert_line.department_id.name or ""
                        grade_id = transfert_line.grade_id.name or ""
                        degree_id = transfert_line.degree_id.name or ""
                        new_job_id = transfert_line.new_job_id.name.name or ""
                        new_code = transfert_line.new_job_id.number or ""
                        new_department_id = transfert_line.new_job_id.department_id.name or ""
                        new_grade_id = transfert_line.new_job_id.grade_id.name or ""
                        new_degree_id = transfert_line.new_degree_id.name or ""
    
                        decision_text = decision_text.replace('JOB', unicode(job_id))
                        decision_text = decision_text.replace('CODE', unicode(code))
                        decision_text = decision_text.replace('DEGREE', unicode(degree_id))
                        decision_text = decision_text.replace('GRADE', unicode(grade_id))
                        decision_text = decision_text.replace('DEPARTEMENT', unicode(department_id))
                        decision_text = decision_text.replace('job', unicode(new_job_id))
                        decision_text = decision_text.replace('code', unicode(new_code))
                        decision_text = decision_text.replace('degree', unicode(new_degree_id))
                        decision_text = decision_text.replace('grade', unicode(new_grade_id))
                        decision_text = decision_text.replace('department', unicode(new_department_id))

        return decision_text

class HrDecisionType(models.Model):
    _name = 'hr.decision.type'
    _description = u'نوع القرار'

    name = fields.Char(string='المسمى', required=1)
    code = fields.Char(string='الرمز')
    note = fields.Text(string='ملاحظات')
    text = fields.Html(string='نص القرار')
