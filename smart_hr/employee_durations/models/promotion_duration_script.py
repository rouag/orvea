# -*- coding: utf-8 -*-

from openerp import models, fields, api, _


class PromotionDuration(models.Model):
    _name = 'hr.employee.promotion.duration'
    _inherit = ['mail.thread']
    _description = u'حساب مدة الترقية'

    name = fields.Char(string=u'حساب مدة الترقية', readonly=1)
    employee_promotion_ids = fields.Many2many('hr.employee', string=u'الموظفون')
    date_last_execution = fields.Date(string=u'تاريخ  التنفيذ', readonly=1, default=fields.Datetime.now)
    state = fields.Selection([('draft', u'جديد'),
                              ('done', u'اعتمدت'),
                              ('cancel', u'ملغاة'),
                              ], string=u'الحالة', default='draft')

    @api.multi
    def action_done(self):
        for emp in self.employee_promotion_ids:
            if emp.date_last_promotion:
                today_date = fields.Date.from_string(fields.Date.today())
                date_direct_action = fields.Date.from_string(emp.date_last_promotion)
                promotion_days = (today_date - date_direct_action).days
                # مدّة غياب‬ ‫الموظف بدون‬ سند‬ ‫ن
                absence_days = self.env['hr.attendance.summary'].search([('employee_id', '=', emp.id), ('date', '<=', today_date),
                                                                         ('date', '>=', date_direct_action)])
                uncounted_absence_days = 0
                for absence in absence_days:
                    uncounted_absence_days += absence.absence
                promotion_days -= uncounted_absence_days
#                 مدة الاجازات
                uncounted_holidays_days = self.env['hr.holidays'].search([('employee_id', '=', emp.id), ('state', '=', 'done'), ('date_from', '<', today_date),
                                                                          ('date_from', '>', date_direct_action), ('holiday_status_id.promotion_deductible', '=', True)])
                for holiday in uncounted_holidays_days:
                    holiday_date_to = fields.Date.from_string(holiday.date_to)
                    if holiday_date_to <= today_date:
                        promotion_days -= holiday.duration
                    else:
                        duration = (today_date - holiday.date_from).days
                        promotion_days -= duration
#                 مدة الابتعاث
                uncounted_scholaship_days = self.env['hr.scholarship'].search([('employee_id', '=', emp.id), ('state', '=', 'finished'), ('result', '=', 'not_succeed'),
                                                                               ('date_from', '>=', date_direct_action), ('date_to', '<=', today_date)])
                for sholarship in uncounted_scholaship_days:
                    promotion_days -= sholarship.duration
#                 مدة  الدورات الدراسيّة
                uncounted_courses_days = self.env['courses.followup'].search([('employee_id', '=', emp.id), ('state', '=', 'done'), ('result', '=', 'not_succeed'),
                                                                              ('date_from', '>=', date_direct_action), ('date_to', '<=', today_date)])
                for course in uncounted_courses_days:
                    promotion_days -= course.duration
#                 مدة كف اليد عند الادانة
                uncounted_suspension_end_days = self.env['hr.suspension.end'].search([('employee_id', '=', emp.id), ('state', '=', 'done'), ('condemned', '=', True),
                                                                                      ('release_date', '>=', date_direct_action), ('release_date', '<=', today_date)])
                for suspension_end in uncounted_suspension_end_days:
                    suspension_date_from = fields.Date.from_string(suspension_end.suspension_id.suspension_date)
                    release_date_to = fields.Date.from_string(suspension_end.release_date)
                    if suspension_date_from >= date_direct_action:
                        promotion_days -= (release_date_to - suspension_date_from).days
                    else:
                        duration = (release_date_to - date_direct_action).days
                    promotion_days -= suspension_end.sentence
                emp.promotion_duration = promotion_days
            else:
                emp.promotion_duration = 0
        self.state = 'done'
        self.date_last_execution = fields.Date.today()
        self.name = self.date_last_execution

    @api.multi
    def action_cancel(self):
        self.state = 'cancel'
        self.date_last_execution = fields.Date.today()
        self.name = str(self.date_last_execution)


class EmployeesPromotionDuration(models.Model):
    _inherit = 'hr.employee'
    _description = u'حساب مدة الترقية'

    date_last_promotion = fields.Date(string=u'تاريخ آخر ترقية', compute='_compute_date_last_promotion', readonly=1)

    @api.multi
    def _compute_date_last_promotion(self):
        for rec in self:
                employee_decision_appoint = self.env['hr.decision.appoint'].search([('employee_id', '=', rec.id), ('is_started', '=', True), ('state', '=', 'done')], order='date_direct_action desc')
                for decision_appoint in employee_decision_appoint:
                    grade_id = int(decision_appoint.emp_job_id.grade_id.code)
                    new_grade_id = int(decision_appoint.grade_id.code)
                    if decision_appoint.date_direct_action:
                        if decision_appoint.job_id.type_id != decision_appoint.emp_job_id.type_id or (grade_id != new_grade_id) or (decision_appoint.job_id.name.members_job is False and decision_appoint.emp_job_id.name.members_job is True):
                            rec.date_last_promotion = decision_appoint.date_direct_action
                            break
                if not rec.date_last_promotion and employee_decision_appoint:
                    decision_appoint = employee_decision_appoint[len(employee_decision_appoint) - 1]
                    rec.date_last_promotion = decision_appoint.date_direct_action

