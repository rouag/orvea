# -*- coding: utf-8 -*-

from openerp import fields, models, api, _


class ResourceCalendar(models.Model):
    _inherit = 'resource.calendar'

    date_from = fields.Date('تاريخ من')
    date_to = fields.Date('إلى')


class ResourceCalendarAttendance(models.Model):
    _inherit = 'resource.calendar.attendance'

    @api.onchange('dayofweek')
    def onchange_dayofweek(self):
        day = 'الأثنين'
        if self.dayofweek == '1':
            day = 'الثلاثاء'
        elif self.dayofweek == '2':
            day = 'الأربعاء'
        elif self.dayofweek == '3':
            day = 'الخميس'
        elif self.dayofweek == '4':
            day = 'الجمعة'
        elif self.dayofweek == '5':
            day = 'السبت'
        elif self.dayofweek == '6':
            day = 'الأحد'
        self.name = u'وردية يوم %s ' % day


class hr_attendance(models.Model):
    _inherit = 'hr.attendance'

    id_emprinte = fields.Char(string=u'رقم ')
    mac_id = fields.Char(string=u'الآلة ')
