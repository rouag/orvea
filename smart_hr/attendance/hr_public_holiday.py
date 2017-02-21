# -*- coding: utf-8 -*-


from openerp import models, fields, api, _
from datetime import timedelta
import math
from openerp.exceptions import ValidationError

HOURS_PER_DAY = 7


class HrPublicHoliday(models.Model):
    _name = 'hr.public.holiday'

    name = fields.Char(string='العيد/العطلة', required=1)
    date_from = fields.Date(string='من', required=1)
    date_to = fields.Date(string=' إلى', required=1)
    number_of_days = fields.Float(string=' المدة', required=1)
    state = fields.Selection([('draft', u'طلب'),
                              ('hrm', u'مدير شؤون الموظفين'),
                              ('done', u'اعتمدت'),
                              ], string=u'الحالة', default='draft', advanced_search=True)

    @api.one
    @api.constrains('date_from', 'date_to')
    def _check_date(self):
        for holiday in self.search([]):
            domain = [
                ('date_from', '<=', holiday.date_to),
                ('date_to', '>=', holiday.date_from),
                ('id', '!=', holiday.id),
            ]
            nholidays = self.search_count(domain)
            if nholidays:
                raise ValidationError(u"هناك تداخل في التواريخ مع عيد/عطلة سابقة")

    @api.one
    @api.constrains('date_from', 'date_to')
    def check_dates_periode(self):

        if self.date_from > self.date_to:
            raise ValidationError(u"تاريخ من يجب ان يكون أصغر من تاريخ الى")

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
    
    
    @api.multi
    def button_send_request(self):
        self.ensure_one()
        self.state = 'hrm'
        
    @api.multi
    def button_accept_hrm(self):
        self.ensure_one()
        self.state = 'done'

    @api.multi
    def button_refuse_hrm(self):
        self.ensure_one()
        self.state = 'draft'
        
        
    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise ValidationError(u'لا يمكن حذف عيد/عطلة فى هذه المرحلة يرجى مراجعة مدير النظام')
        return super(HrPublicHoliday, self).unlink()
    
              