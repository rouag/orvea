# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from dateutil.relativedelta import relativedelta
from openerp.exceptions import ValidationError
from datetime import date, datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT


class HrEmployeeLend(models.Model):
    _name = 'hr.employee.lend'
    _description = u'طلب إعارة موظف'
    _rec_name = 'employee_id'

    create_date = fields.Datetime(string=u'تاريخ الطلب', default=fields.Datetime.now(), readonly=1)
    employee_id = fields.Many2one('hr.employee', string='صاحب الطلب', required=1)
    insurance_entity = fields.Many2one('res.partner', string=u'الجهة المعار إليها', domain=[('company_type', '=', 'insurance')], required=1)
    decision_number = fields.Char(string=u"رقم القرار", required=1)
    decision_date = fields.Date(string=u'تاريخ القرار', required=1)
    decision_file = fields.Binary(string=u'نسخة القرار', required=1)
    date_from = fields.Date(string=u'التاريخ من ', default=fields.Datetime.now())
    date_to = fields.Date(string=u'التاريخ الى', compute='_compute_date_to', store=True)
    duration = fields.Integer(string=u'الأيام', required=1)
    state = fields.Selection([('new', u'طلب'),
                              ('waiting', u'صاحب الصلاحية'),
                              ('pm', u'شؤون الموظفين'),
                              ('commission_president', u'رئيس الجهة'),
                              ('done', u'اعتمدت'),
                              ('refused', u'رفض'),
                              ('cancelled', u'ملغى')
                              ], readonly=1, default='new', string=u'الحالة')

    @api.multi
    @api.depends('date_from', 'duration')
    def _compute_date_to(self):
        self.ensure_one()
        if self.date_from and self.duration:
            new_date_to = fields.Date.from_string(self.date_from) + timedelta(days=self.duration)
            self.date_to = new_date_to
        elif self.date_from:
                self.date_to = self.date_from

    @api.multi
    @api.constrains('duration')
    def check_constrains(self):
        self.ensure_one()
        hr_config = self.env['hr.setting'].search([], limit=1)
        if hr_config:
            # check duration
            if self.duration > hr_config.lend_duration:
                raise ValidationError(u"لقد تم تجاوز الحد الأقصى للإعارة في المرة الواحدة.")
            # check maximum lends duration in employee's service
            old_lends = self.env['hr.employee.lend'].search([('state', '=', 'done'), ('employee_id', '=', self.employee_id.id)])
            sum_duration = self.duration
            for lend in old_lends:
                sum_duration += lend.duration
            if sum_duration > 0 and hr_config.max_lend_duration_sum <= sum_duration / 365:
                raise ValidationError(u"لقد تم تجاوز الحد الأقصى للإعارة.")
            # check duration bettween accepted lend and new one
            for lend in old_lends:
                date_to = lend.date_to
                diff = relativedelta(fields.Date.from_string(fields.Datetime.now()), fields.Date.from_string(date_to)).years
                if diff >= hr_config.periode_between_lend:
                    raise ValidationError(u"لا يمكن طلب إعارة هذا الموظف الأن.")
