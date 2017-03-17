# -*- coding: utf-8 -*-


from openerp import models, fields, api, _
from datetime import date, datetime, timedelta
from datetime import datetime, timedelta, time
from openerp.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
from openerp.exceptions import UserError
from openerp.addons.smart_base.util.umalqurra import *
from umalqurra.hijri_date import HijriDate
from umalqurra.hijri import Umalqurra


class HrDecision(models.Model):
    _name = 'hr.decision'
    _inherit = ['mail.thread']
    _description = u'القرار'

   
    name = fields.Char(string='قرار إداري رقم', required=1)
    decision_type_id = fields.Many2one('hr.decision.type', string='نوع القرار', required=1)
    date = fields.Date(string='بتاريخ', required=1)
    employee_id = fields.Many2one('hr.employee', string='الموظف')
    text = fields.Html(string='نص القرار')
    num_speech = fields.Char(string='رقم الخطاب')
    date_speech = fields.Date(string='تاريخ الخطاب' )
    employee_ids = fields.Many2many('hr.employee',string='الاعضاء المرقين')
     
    @api.onchange('num_speech', 'date_speech', 'name', 'date')
    def onchange_fileds(self):
        self.onchange_decision_type_id()

    @api.onchange('date_speech')
    def onchange_date_speech(self):
        self.onchange_decision_type_id()



    @api.onchange('decision_type_id')
    def onchange_decision_type_id(self):
       
        if self.decision_type_id not in [self.env.ref('smart_hr.data_decision_type6'),
                                    self.env.ref('smart_hr.data_decision_type7'),
                                    self.env.ref('smart_hr.data_decision_type8'),
                                    self.env.ref('smart_hr.data_decision_type9'),
                                    self.env.ref('smart_hr.data_decision_type10'),
                                     ]:
            employee_line = self.env['hr.employee'].search([('id', '=', self.employee_id.id), ('state', '=', 'done')], limit=1)
            if employee_line :
                
                dates = str(self.date).split('-')
                dattz = dates[2]+'-'+dates[1]+'-'+dates[0] or ""
                employee = self.employee_id.display_name or ""
                carte_id = self.employee_id.identification_id or ""
                birthday = self.employee_id.birthday or ""
                emp_city = self.employee_id.dep_city.name or ""
                numero = self.name or ""
                num_speech = self.num_speech or ""
                date_speech = self.date_speech or ""
                decision_type_line = self.env['hr.decision.type'].search([('id', '=', self.decision_type_id.id)])
                current_year = datetime.now().year
                employee_ids_len = len(self.employee_ids.ids)
                #information employee  old job

                job_id = employee_line.job_id.name.name or ""
                number = employee_line.number or ""
                code = employee_line.job_id.number or ""
                department_id = employee_line.department_id.name or ""
                type_job_id = employee_line.type_id.name or ""
                grade_id = employee_line.grade_id.name or ""
                degree_id = employee_line.degree_id.name or ""
                salary_grid_id, basic_salary = employee_line.get_salary_grid_id(False)
                salary = salary_grid_id.net_salary  or ""
                rel_text = decision_type_line.text
     #           transport_allow = employee_line.get_salary_grid_id(False)[0].transport_allow or ""
    #             retirement = employee_line.retirement or ""
               # net_salary = employee_line.net_salary or ""
                if decision_type_line.text:
                    #rel_text = decision_type_line.text
                    rep_text = rel_text.replace('EMPLOYEE', unicode(employee))
                    rep_text = rep_text.replace('BIRTHDAY', unicode(birthday))
                    rep_text = rep_text.replace('DATE', unicode(dattz))
                    rep_text = rep_text.replace('CARTEID', unicode(carte_id))
                    rep_text = rep_text.replace('NUMERO', unicode(numero))
                    rep_text = rep_text.replace('DATESTARTINCREASE', unicode(current_year))
                    rep_text = rep_text.replace('CITY', unicode(emp_city))
                    rep_text = rep_text.replace('NumSpeech', unicode(num_speech))
                    rep_text = rep_text.replace('DateSpeech', unicode(date_speech))
                    employee_ids_len = rep_text.replace('NUMBEREMPLOYEES', unicode(employee_ids_len))
                    rep_text = rep_text.replace('NUMBER',unicode(number))
                    rep_text = rep_text.replace('JOB',unicode(job_id))
                    rep_text = rep_text.replace('CODE',unicode(code))
                    rep_text = rep_text.replace('DEGREE',unicode(degree_id))
                    rep_text = rep_text.replace('GRADE',unicode(grade_id))
                    rep_text = rep_text.replace('BASICSALAIRE',unicode(salary))
                    rep_text = rep_text.replace('DEPARTEMENT',unicode(department_id))

                    self.text = rep_text
        else :
            appoint_line = self.env['hr.decision.appoint'].search([('employee_id', '=', self.employee_id.id), ('state', '=', 'done')], limit=1)
            dates = str(self.date).split('-')
            dattz = dates[2]+'-'+dates[1]+'-'+dates[0] or ""
            employee = self.employee_id.name or ""
            carte_id = self.employee_id.identification_id or ""
            birthday = self.employee_id.birthday or ""
            emp_city = self.employee_id.dep_city.name or ""
            numero = self.name or ""
            num_speech = self.num_speech or ""
            date_speech = self.date_speech or ""
            salary_grid_id, basic_salary = self.employee_id.get_salary_grid_id(False)
            salary = salary_grid_id.net_salary  or ""
            decision_type_line = self.env['hr.decision.type'].search([('id', '=', self.decision_type_id.id)])
            current_year = datetime.now().year
            employee_ids_len = len(self.employee_ids.ids)
            rel_text = decision_type_line.text

            if decision_type_line.text:
                rep_text = rel_text.replace('EMPLOYEE', unicode(employee))
                rep_text = rep_text.replace('BIRTHDAY', unicode(birthday))
                rep_text = rep_text.replace('DATE', unicode(dattz))
                rep_text = rep_text.replace('CARTEID', unicode(carte_id))
                rep_text = rep_text.replace('NUMERO', unicode(numero))
                rep_text = rep_text.replace('DATESTARTINCREASE', unicode(current_year))
                rep_text = rep_text.replace('CITY', unicode(emp_city))
                rep_text = rep_text.replace('NumSpeech', unicode(num_speech))
                rep_text = rep_text.replace('DateSpeech', unicode(date_speech))
                rep_text = rep_text.replace('BASICSALAIRE',unicode(salary))
                employee_ids_len = rep_text.replace('NUMBEREMPLOYEES', unicode(employee_ids_len))
                if appoint_line:
                    if decision_type_line:
                    #information employee  old job
                        emp_job_id = appoint_line.emp_job_id.name.name or ""
                        emp_number_job = appoint_line.emp_number_job or ""
                        emp_code = appoint_line.emp_code or ""
                        emp_department_id = appoint_line.emp_department_id.name or ""
                        emp_type_id = appoint_line.emp_type_id.name or ""
                        emp_grade_id = appoint_line.emp_grade_id.name or ""
                        emp_degree_id = appoint_line.emp_degree_id.name or ""
                        emp_basic_salary = appoint_line.emp_basic_salary   or ""
                    #information employee  new job  
                        job_id = appoint_line.job_id.name.name or ""
                        number = appoint_line.number_job or ""
                        code = appoint_line.code or ""
                        department_id = appoint_line.department_id.name or ""
                        type_job_id = appoint_line.type_id.name or ""
                        grade_id = appoint_line.grade_id.name or ""
                        degree_id = appoint_line.degree_id.name or ""
                        #salary = appoint_line.basic_salary  or ""
                      #  transport_allow = appoint_line.transport_allow or ""
                      #  retirement = appoint_line.retirement or ""
                        #net_salary = appoint_line.net_salary or ""
                    if decision_type_line.text:
                            rep_text = rep_text.replace('NUMBER',unicode(number))
                            rep_text = rep_text.replace('JOB',unicode(job_id))
                            rep_text = rep_text.replace('CODE',unicode(code))
                            rep_text = rep_text.replace('DEGREE',unicode(degree_id))
                            rep_text = rep_text.replace('GRADE',unicode(grade_id))

                            rep_text = rep_text.replace('DEPARTEMENT',unicode(department_id))
                            rep_text = rep_text.replace('job',unicode(emp_job_id))
                            rep_text = rep_text.replace('code',unicode(emp_code))
                            rep_text = rep_text.replace('numero',unicode(emp_number_job))
                            rep_text = rep_text.replace('degree',unicode(emp_degree_id))
                            rep_text = rep_text.replace('grade',unicode(emp_grade_id))
                            rep_text = rep_text.replace('basicsalaire',unicode(emp_basic_salary))
                            rep_text = rep_text.replace('department',unicode(emp_department_id))
                            self.text = rep_text

class HrDecisionType(models.Model):
    _name = 'hr.decision.type'
    _description = u'نوع القرار'

    name = fields.Char(string='المسمى', required=1)
    code = fields.Char(string='الرمز')
    note = fields.Text(string='ملاحظات')
    text = fields.Html(string='نص القرار')


