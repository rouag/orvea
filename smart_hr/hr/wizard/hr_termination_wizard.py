# -*- coding: utf-8 -*-

import time
from openerp import api, fields, models, _
from datetime import datetime, timedelta, time
from openerp.exceptions import ValidationError
from umalqurra.hijri_date import HijriDate
from openerp.addons.smart_base.util.time_util import float_time_convert
from openerp.addons.smart_base.util.time_util import time_float_convert
from openerp.addons.smart_base.util.time_util import float_time_convert_str
from openerp.addons.smart_base.util.umalqurra import *
from umalqurra.hijri import Umalqurra


class WizardHrTermination(models.TransientModel):
    _name = 'wizard.hr.termination'

    date_from = fields.Date(string='التاريخ من', required=1)
    date_to = fields.Date(string='إلى', required=1)
    is_member = fields.Boolean(string=u'عضو في الهيئة')

    @api.multi
    def print_report(self):
        report_action = self.env['report'].get_action(self, 'smart_hr.hr_termination_retraite_reportt')
        data = {'ids': [],'form': self.read([])[0]}
        report_action['data'] = data
        return report_action