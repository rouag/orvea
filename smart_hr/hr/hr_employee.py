# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from dateutil.relativedelta import relativedelta
from datetime import date


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    @api.multi
    def name_get(self):
        res = []
        for emp in self:
            res.append((emp.id, "[%s] %s %s %s %s" % (emp.number or '', emp.name or '', emp.father_middle_name or '', emp.father_name or '', emp.family_name or '')))
        return res

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []
        recs = self.browse()
        print name
        if name:
            domain = [
                '|',
                '|',
                '|',
                '|',
                ('number', operator, name),
                ('name', operator, name),
                ('father_middle_name', operator, name),
                ('father_name', operator, name),
                ('family_name', operator, name),
            ]
            recs = self.search(domain + args, limit=limit)
        if not recs:
            recs = self.search([('name', operator, name)] + args, limit=limit)
        return recs.name_get()