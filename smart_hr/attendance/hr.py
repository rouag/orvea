# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.addons.smart_base.util.time_util import time_float_convert


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    calendar_id = fields.Many2one('resource.calendar' ,string=u'الورديّات')

    def get_authorization_by_date(self, date, first_time=False, latest_time=False):
        '''
        :param date:
        :param first_time: must be a float
        :param latest_time: must be a float
        '''
        # search in طلبات الإستئذان
        authorization_obj = self.env['hr.authorization']
        domain = [('state', '=', 'done'), ('date', '=', date), ('employee_id', '=', self.id)]
        if first_time and latest_time:
            domain.append(('hour_from', '>=', first_time))
            domain.append(('hour_to', '<=', latest_time))
        authorization_ids = authorization_obj.search(domain)
        return authorization_ids

    def get_holidays_by_date(self, date):
        holidays_obj = self.env['hr.holidays']
        holidays_ids = holidays_obj.search([('state', '=', 'done'),
                                            ('employee_id', '=', self.id),
                                            ('date_from', '<=', date),
                                            ('date_to', '>=', date)])

        return holidays_ids

    def get_training_by_date(self, date):
        trainingobj = self.env['hr.candidates']
        training_ids = trainingobj.search([('state', '=', 'done'),
                                           ('employee_id', '=', self.id),
                                           ('date_from', '<=', date),
                                           ('date_to', '>=', date)])

        return training_ids
