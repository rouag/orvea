# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.addons.smart_base.util.time_util import time_float_convert


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    calendar_id = fields.Many2one('resource.calendar', 'جدول ساعات العمل')

    def get_authorization_by_date(self, date, first_time, latest_time):
        '''
        :param date:
        :param first_time: must be a float
        :param latest_time: must be a float
        '''
        # search in طلبات الإستئذان
        authorization_obj = self.env['hr.authorization']
        authorization_ids = authorization_obj.search([('state', '=', 'done'),
                                                      ('date', '=', date),
                                                      ('employee_id', '=', self.id),
                                                      ('hour_from', '>=', first_time),
                                                      ('hour_to', '<=', latest_time)])

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