# -*- coding: utf-8 -*-

from openerp import models, fields, api, _


class serviceDuration(models.Model):
    _name = 'hr.employee.service.duration'
    _inherit = ['mail.thread']
    _description = u'حساب مدة الخدمة'

    name = fields.Char(string=u'حساب مدة الخدمة', readonly=1)
    employee_service_ids = fields.Many2many('hr.employee', string=u'الموظفون')
    date_last_execution = fields.Date(string=u'تاريخ  التنفيذ', readonly=1)
    state = fields.Selection([('draft', u'جديد'),
                              ('done', u'اعتمدت'),
                              ('cancel', u'ملغاة'),
                              ], string=u'الحالة', default='draft')

    @api.multi
    def action_done(self):
        for emp in self.employee_service_ids:
            if emp.begin_work_date:
                today_date = fields.Date.from_string(fields.Date.today())
                date_direct_action = fields.Date.from_string(emp.begin_work_date)
                service_days = (today_date - date_direct_action).days
                # مدّة غياب‬ ‫الموظف بدون‬ سند‬ ‫ن
                absence_days = self.env['hr.attendance.summary'].search([('employee_id', '=', emp.id), ('date', '<=', today_date),
                                                                         ('date', '>=', date_direct_action)])
                uncounted_absence_days = 0
                for absence in absence_days:
                    uncounted_absence_days += absence.absence
                service_days -= uncounted_absence_days
#                 مدة الاجازات
                uncounted_holidays_days = self.env['hr.holidays'].search([('employee_id', '=', emp.id), ('state', '=', 'done'), ('date_from', '<', today_date),
                                                                          ('date_from', '>', date_direct_action), ('holiday_status_id.deductible_duration_service', '=', True)])
                for holiday in uncounted_holidays_days:
                    holiday_date_to = fields.Date.from_string(holiday.date_to)
                    if holiday_date_to <= today_date:
                        service_days -= holiday.duration
                    else:
                        duration = (today_date - holiday.date_from).days
                        service_days -= duration
#                 مدة الابتعاث
                uncounted_scholaship_days = self.env['hr.scholarship'].search([('employee_id', '=', emp.id), ('state', '=', 'finished'), ('result', '=', 'not_succeed'),
                                                                               ('date_from', '>=', date_direct_action), ('date_to', '<=', today_date)])
                for sholarship in uncounted_scholaship_days:
                    service_days -= sholarship.duration
#                 مدة  الدورات الدراسيّة
                uncounted_courses_days = self.env['courses.followup'].search([('employee_id', '=', emp.id), ('state', '=', 'done'), ('result', '=', 'not_succeed'),
                                                                              ('date_from', '>=', date_direct_action), ('date_to', '<=', today_date)])
                for course in uncounted_courses_days:
                    service_days -= course.duration
#                 مدة كف اليد عند الادانة
                uncounted_suspension_end_days = self.env['hr.suspension.end'].search([('employee_id', '=', emp.id), ('state', '=', 'done'), ('condemned', '=', True),
                                                                                      ('release_date', '>=', date_direct_action), ('release_date', '<=', today_date)])
                for suspension_end in uncounted_suspension_end_days:
                    suspension_date_from = fields.Date.from_string(suspension_end.suspension_id.suspension_date)
                    release_date_to = fields.Date.from_string(suspension_end.release_date)
                    if suspension_date_from >= date_direct_action:
                        service_days -= (release_date_to - suspension_date_from).days
                    else:
                        duration = (release_date_to - date_direct_action).days
                    service_days -= suspension_end.sentence
#                 i3ara ereste a faire monadhamet dowalia
                lend_obj = self.env['hr.employee.lend']
                lend_uncounted_days = lend_obj.search_count([('employee_id', '=', emp.id), ('state', '=', 'done'), ('date_from', '<=', today_date), ('date_from', '>', date_direct_action)])
                for lend in lend_uncounted_days:
                    service_days -= lend.duration
                emp.service_duration = service_days
            else:
                emp.service_duration = 0
        self.state = 'done'
        self.date_last_execution = fields.Date.today()
        self.name = self.date_last_execution

    @api.multi
    def action_cancel(self):
        self.state = 'cancel'
        self.date_last_execution = fields.Date.today()
        self.name = self.date_last_execution

