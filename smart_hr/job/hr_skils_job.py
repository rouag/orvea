# -*- coding: utf-8 -*-


from openerp import models, fields, api, _
from openerp.exceptions import Warning
from dateutil.relativedelta import relativedelta
from openerp.exceptions import ValidationError
from datetime import date


class HrSkilsJob(models.Model):
    _name = 'hr.skils.job'
    _description = u'‫‫المهارات‬ ‫و‬ ‫القدرات‬‬‬'
    name = fields.Char(string=u'مسمى المهارات‬ ‫و‬ ‫القدرات‬‬‬ ', required=1)
    description =fields.Char(string=u'‫‬ شرح ',)
