# -*- coding: utf-8 -*-


from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
from datetime import datetime, timedelta
import math
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from openerp.exceptions import ValidationError

HOURS_PER_DAY = 7


class HrTraining(models.Model):
    _name = 'hr.training'
    _description = u'التدريب'

    @api.one
    @api.depends('line_ids')
    def _compute_info(self):
        self.number_participant = len(self.line_ids)

    name = fields.Char(string=' المسمى', required=1, states={'new': [('readonly', 0)]})
    number = fields.Char(string='رقم القرار', required=1, states={'new': [('readonly', 0)]})
    date = fields.Date(string=' تاريخ القرار', required=1, states={'new': [('readonly', 0)]})
    date_from = fields.Date(string='تاريخ من', required=1, states={'new': [('readonly', 0)]})
    date_to = fields.Date(string=' إلى', required=1, states={'new': [('readonly', 0)]})
    number_of_days = fields.Float(string=' المدة', required=1, states={'new': [('readonly', 0)]})
    department = fields.Char(string=' الجهة', required=1, states={'new': [('readonly', 0)]})
    place = fields.Char(string=' المكان', required=1, states={'new': [('readonly', 0)]})
    number_place = fields.Integer(string='عدد المقاعد', required=1, states={'new': [('readonly', 0)]})
    number_participant = fields.Integer(string=' عدد المشتركين', store=True, readonly=True, compute='_compute_info')
    line_ids = fields.One2many('hr.candidates', 'training_id', string='المترشحين', required=1, states={'new': [('readonly', 0)]})
    state = fields.Selection([('new', 'جديد'),
                              ('candidat', 'الترشح'),
                              ('review', 'المراجعة'),
                              ('confirm', 'إعتمدت'),
                              ('done', 'تمت')], readonly=1, string='الحالة', default='new')
    job_trainings = fields.One2many('hr.job.training', 'type', string='job trainings')

    @api.onchange('date_from')
    def _onchange_date_from(self):
        date_from = self.date_from
        date_to = self.date_to

        # No date_to set so far: automatically compute one 8 hours later
        if date_from and not date_to:
            date_to_with_delta = fields.Datetime.from_string(date_from) + timedelta(hours=HOURS_PER_DAY)
            self.date_to = str(date_to_with_delta)

        # Compute and update the number of days
        if (date_to and date_from) and (date_from <= date_to):
            self.number_of_days = self._get_number_of_days(date_from, date_to)
        else:
            self.number_of_days = 0

    @api.onchange('date_to')
    def _onchange_date_to(self):
        """ Update the number_of_days. """
        date_from = self.date_from
        date_to = self.date_to

        # Compute and update the number of days
        if (date_to and date_from) and (date_from <= date_to):
            self.number_of_days = self._get_number_of_days(date_from, date_to)
        else:
            self.number_of_days = 0

    def _get_number_of_days(self, date_from, date_to):
        """ Returns a float equals to the timedelta between two dates given as string."""
        from_dt = fields.Datetime.from_string(date_from)
        to_dt = fields.Datetime.from_string(date_to)
        time_delta = to_dt - from_dt
        return math.ceil(time_delta.days + float(time_delta.seconds) / 86400) + 1

    @api.one
    def action_candidat(self):
        self.state = 'candidat'

    @api.one
    def action_review(self):
        self.state = 'review'

    @api.one
    def action_confirm(self):
        self.state = 'confirm'

    @api.one
    def action_done(self):
        self.state = 'done'

class HrTrainingType(models.Model):
    _name = 'hr.training.type'
    _description = u'أنواع التدريب'
    name = fields.Char(string=u'المسمى', required=True)


class HrCandidates(models.Model):
    _name = 'hr.candidates'
    _description = u'المترشحين'
    _rec_name = 'employee_id'

    employee_id = fields.Many2one('hr.employee', string=' إسم الموظف')
    number = fields.Char(related='employee_id.number', store=True, readonly=True, string=' الرقم الوظيفي')
    job_id = fields.Many2one(related='employee_id.job_id', store=True, readonly=True, string=' الوظيفة')
    department_id = fields.Many2one(related='employee_id.department_id', store=True, readonly=True, string=' القسم')
    training_id = fields.Many2one('hr.training', string=' الدورة')
    date_from = fields.Date(related='training_id.date_from', store=True, readonly=True)
    date_to = fields.Date(related='training_id.date_to', store=True, readonly=True)
    department = fields.Char(related='training_id.department', store=True, readonly=True)
    state = fields.Selection([('new', ' ارسال طلب'),
                             ('waiting', 'في إنتظار الإعتماد'),
                             ('cancel', 'رفض'),
                             ('done', 'اعتمدت')], string='الحالة', readonly=1, default='new')

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        if self.employee_id:
            self.number = self.employee_id.number
            self.job_id = self.employee_id.job_id.id
            self.department_id = self.employee_id.department_id.id

    @api.onchange('training_id')
    def _onchange_training_id(self):
        if self.training_id:
            self.date_from = self.date_from
            self.date_to = self.date_to
            self.department = self.department

    @api.one
    def action_waiting(self):
        self.state = 'waiting'

    @api.one
    def action_cancel(self):
        self.state = 'cancel'

    @api.one
    def action_done(self):
        self.state = 'done'

    @api.one
    def action_refuse(self):
        self.state = 'new'


# TODO: all conditions not work
#     @api.constrains('date_from', 'date_to')
#     def check_dates(self):
#         for train in self:
#             # Objects
#             dep_obj = self.env['hr.deputation']
#             train_obj = self.env['hr.training']
#             overtime_obj = self.env['hr.overtime']
#             hr_public_holiday_obj = self.env['hr.public.holiday']
#             # Variables
#             #days_before_after = train.city_id.days_before_after
#             # Calculate Effective Dates
#             effective_date_from = (datetime.strptime(train.date_from, DEFAULT_SERVER_DATE_FORMAT)).strftime(DEFAULT_SERVER_DATE_FORMAT)
#             effective_date_to = (datetime.strptime(train.date_to, DEFAULT_SERVER_DATE_FORMAT)).strftime(DEFAULT_SERVER_DATE_FORMAT)
#             # Check for incomplete data
#             if train.date_from > train.date_to:
#                 raise ValidationError(u'تاريخ بداية الدورة يجب ان يكون أصغر من تاريخ انتهاء الدورة')
#             # Check for eid
#             for public_holiday in hr_public_holiday_obj.search([]):
#                 if public_holiday.date_from <= effective_date_from <= public_holiday.date_to or \
#                         public_holiday.date_from <= effective_date_to <= public_holiday.date_to or \
#                         effective_date_from <= public_holiday.date_from <= effective_date_to or \
#                         effective_date_from <= public_holiday.date_to <= effective_date_to:
#                     raise ValidationError(u"هناك تداخل فى التواريخ مع اعياد و مناسبات رسمية")
#             # Check for any intersection with other decisions
#             for emp in train.employee_ids:
#                 # Overtime
#                 search_domain = [
#                     ('overtime_line_ids.employee_id', '=', emp.id),
#                     ('state', '!=', 'refuse'),
#                 ]
#                 for rec in overtime_obj.search(search_domain):
#                     for line in rec.overtime_line_ids:
#                         if (line.date_from <= effective_date_from <= line.date_to or \
#                                 line.date_from <= effective_date_to <= line.date_to or \
#                                 effective_date_from <= line.date_from <= effective_date_to or \
#                                 effective_date_from <= line.date_to <= effective_date_to) and \
#                                 line.employee_id == emp:
#                             raise ValidationError(u"هناك تداخل فى التواريخ مع قرار سابق فى خارج الدوام")
#                 # Leave
#                 search_domain = [
#                     ('employee_id', '=', emp.id),
#                     ('state', '!=', 'refuse'),
#                 ]
#                 # Training
#                 search_domain = [
#                     ('employee_ids', 'in', [emp.id]),
#                     ('id', '!=', train.id),
#                     ('state', '!=', 'refuse'),
#                 ]
#                 for rec in train_obj.search(search_domain):
#                     if rec.date_from <= effective_date_from <= rec.date_to or \
#                             rec.date_from <= effective_date_to <= rec.date_to or \
#                             effective_date_from <= rec.date_from <= effective_date_to or \
#                             effective_date_from <= rec.date_to <= effective_date_to:
#                         raise ValidationError(u"هناك تداخل فى التواريخ مع قرار سابق فى التدريب")
#                 # Deputation
#                 search_domain = [
#                     ('employee_id', '=', emp.id),
#                     ('state', '!=', 'refuse'),
#                 ]
#                 for rec in dep_obj.search(search_domain):
#                     if rec.date_from <= effective_date_from <= rec.date_to or \
#                             rec.date_from <= effective_date_to <= rec.date_to or \
#                             effective_date_from <= rec.date_from <= effective_date_to or \
#                             effective_date_from <= rec.date_to <= effective_date_to:
#                         raise ValidationError(u"هناك تداخل فى التواريخ مع قرار سابق فى الأنتداب")