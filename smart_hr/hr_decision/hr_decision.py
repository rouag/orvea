# -*- coding: utf-8 -*-


from openerp import models, fields, api, _
from openerp.addons.smart_base.util.umalqurra import *
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
        type = False
        if self.decision_type_id:
            self.text = self.replace_text(self.employee_id, self.date, self.decision_type_id.id, 'employee')

    @api.multi
    def button_done(self):
        for decision in self:
            decision.state = 'done'

    def replace_text(self, employee_id, date, decision_type_id, object_type):

        decision_text = ''
        decision_type_line = self.env['hr.decision.type'].search([('id', '=', decision_type_id)])
        if decision_type_line.text:
            decision_text = decision_type_line.text
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
            # information employee  old job
            job_id = employee_id.job_id.name.name or ""
            number = employee_id.number or ""
            code = employee_id.job_id.number or ""
            department_id = employee_id.department_id.name or ""
            type_job_id = employee_id.type_id.name or ""
            grade_id = employee_id.grade_id.name or ""
            degree_id = employee_id.degree_id.name or ""
            salary_grid_id, basic_salary = employee_id.get_salary_grid_id(False)
            salary = salary_grid_id.net_salary or ""

            rel_text = decision_type_line.text

            decision_text = decision_text.replace('EMPLOYEE', unicode(employee))
            decision_text = decision_text.replace('BIRTHDAY', unicode(birthday))
            decision_text = decision_text.replace('DATE', unicode(dattz))
            decision_text = decision_text.replace('CARTEID', unicode(carte_id))
            decision_text = decision_text.replace('NUMBER', unicode(number))
            decision_text = decision_text.replace('BASICSALAIRE', unicode(salary))
            decision_text = decision_text.replace('NUMERO', unicode(numero))
            decision_text = decision_text.replace('JOB', unicode(job_id))
            decision_text = decision_text.replace('CODE', unicode(code))
            decision_text = decision_text.replace('DEGREE', unicode(degree_id))
            decision_text = decision_text.replace('GRADE', unicode(grade_id))
            decision_text = decision_text.replace('DEPARTEMENT', unicode(department_id))

            if type == 'holidays':
                holidays_line = self.env['hr.holidays'].search(
                    [('employee_id', '=', employee_id.id), ('state', '=', 'done')], limit=1)
                if holidays_line:
                    duration = holidays_line.duration or ""
                    if holidays_line.date_from:
                        date_from = self._get_hijri_date(holidays_line.date_from, '-')
                        date_from = str(date_from).split('-')
                        date_from = date_from[2] + '-' + date_from[1] + '-' + date_from[0] or ""
                    fromdate = date_from or ""
                    decision_text = decision_text.replace('DURATION', unicode(duration))
                    decision_text = decision_text.replace('FROMDET', unicode(fromdate))

            if type == 'appoint':
                appoint_line = self.env['hr.decision.appoint'].search(
                    [('employee_id', '=', employee_id.id), ('state', '=', 'done')], limit=1)
                if appoint_line:
                    emp_job_id = appoint_line.emp_job_id.name.name or ""
                    emp_number_job = appoint_line.emp_number_job or ""
                    emp_code = appoint_line.emp_code or ""
                    emp_department_id = appoint_line.emp_department_id.name or ""
                    emp_type_id = appoint_line.emp_type_id.name or ""
                    emp_grade_id = appoint_line.emp_grade_id.name or ""
                    emp_degree_id = appoint_line.emp_degree_id.name or ""
                    emp_basic_salary = appoint_line.emp_basic_salary or ""

                    decision_text = decision_text.replace('job', unicode(emp_job_id))
                    decision_text = decision_text.replace('code', unicode(emp_code))
                    decision_text = decision_text.replace('numero', unicode(emp_number_job))
                    decision_text = decision_text.replace('degree', unicode(emp_degree_id))
                    decision_text = decision_text.replace('grade', unicode(emp_grade_id))
                    decision_text = decision_text.replace('basicsalaire', unicode(emp_basic_salary))
                    decision_text = decision_text.replace('department', unicode(emp_department_id))

        return decision_text


class HrDecisionType(models.Model):
    _name = 'hr.decision.type'
    _description = u'نوع القرار'

    name = fields.Char(string='المسمى', required=1)
    code = fields.Char(string='الرمز')
    note = fields.Text(string='ملاحظات')
    text = fields.Html(string='نص القرار')
