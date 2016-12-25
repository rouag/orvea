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
        day = u'الأثنين'
        if self.dayofweek == '1':
            day = u'الثلاثاء'
        elif self.dayofweek == '2':
            day = u'الأربعاء'
        elif self.dayofweek == '3':
            day = u'الخميس'
        elif self.dayofweek == '4':
            day = u'الجمعة'
        elif self.dayofweek == '5':
            day = u'السبت'
        elif self.dayofweek == '6':
            day = u'الأحد'
        self.name = u'وردية يوم %s ' % day


class hr_attendance(models.Model):
    _inherit = 'hr.attendance'

    id_emprinte = fields.Char(string=u'رقم ')
    mac_id = fields.Char(string=u'الآلة ')
