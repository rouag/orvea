# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from dateutil.relativedelta import relativedelta
from datetime import date


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

#     @api.multi
#     def name_get(self):
#         result = []
#         for record in self:
#             name = '[%s] %s' % (record.number, record.name)
#            
#             result.append((record.id, name))
#         return result
