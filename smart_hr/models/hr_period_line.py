# -*- coding: utf-8 -*-
####################################
### This Module Created by Slnee ###
####################################

from openerp import fields, models, api, _
from openerp.exceptions import ValidationError
from ..apis.datetime_func import daterange

class hr_period_line(models.Model):
    _name = 'hr.period.line'
    _description = 'Deputation and Training Period Lines'

    date_from = fields.Date(string=u'من')
    date_to = fields.Date(string=u'الى')
    duration = fields.Integer(string=u'المدة', compute='_compute_duration')
    deputation_id = fields.Many2one('hr.deputation', string='Deputation')
    training_id = fields.Many2one('hr.training', string='Training')
    state = fields.Selection([
        ('deputation', u'إنتداب'),
        ('training', u'تدريب'),
    ], string=u'الحالة')

    @api.depends('date_from', 'date_to')
    def _compute_duration(self):
        for rec in self:
            start_date = fields.Date.from_string(rec.date_from)
            end_date = fields.Date.from_string(rec.date_to)
            diff = end_date - start_date
            rec.duration = diff.days + 1