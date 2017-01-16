# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.addons.smart_base.util.time_util import time_float_convert


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            name = '[%s] %s' % (record.number, record.name)
            result.append((record.id, name))
        return result