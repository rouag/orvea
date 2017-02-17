# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from dateutil.relativedelta import relativedelta
from openerp.exceptions import ValidationError
from datetime import date, datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT


class HrEmployeeTask(models.Model):
    _name = 'hr.employee.task'
    _description = u'المهمة'

    name = fields.Char(string=u'إسم المهمة')
    date_from = fields.Date(string=u'التاريخ من ', default=fields.Datetime.now())
    date_to = fields.Date(string=u'التاريخ الى', compute='_compute_date_to', store=True)
    duration = fields.Integer(string=u'الأيام', required=1)
    comm_id = fields.Many2one('hr.employee.commissioning', string=u'طلب تكليف موظف')
    employee_id = fields.Many2one('hr.employee', string=u'صاحب المهمة', required=1)
    governmental_entity = fields.Many2one('res.partner', string=u'الجهة الحكومية', domain=['|',('company_type', '=', 'governmental_entity'),('company_type', '=', 'company')])
    description = fields.Text(string=u'الوصف')
    type_procedure = fields.Selection([('deputation', u'الإنتداب'),
                                       ('commission', u'تكليف'),
                                        ('overtime', u'خارج دوام'),
                                       ], default='deputation', string=u'نوع الاجراء')
    state = fields.Selection([('new', u'طلب'),
                              ('done', u'اعتمدت'),
                              ], readonly=1, default='new', string=u'الحالة')

    @api.multi
    @api.depends('date_from', 'duration')
    def _compute_date_to(self):
        for rec in self:
            if rec.date_from and rec.duration:
                new_date_to = fields.Date.from_string(rec.date_from) + timedelta(days=rec.duration)
                rec.date_to = new_date_to
            elif rec.date_from:
                    rec.date_to = rec.date_from

    @api.multi
    def action_done(self):
        self.ensure_one()
        self.state = "done"
        # create history_line
        self.env['hr.employee.history'].sudo().add_action_line(self.employee_id, False, False, self._description)
