# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from dateutil.relativedelta import relativedelta
from openerp.exceptions import ValidationError
from datetime import date, datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT


class HrEmployeeCommissioning(models.Model):
    _name = 'hr.employee.commissioning'
    _description = u'طلب تكليف موظف'
    _rec_name = 'employee_id'

    @api.multi
    def _get_default_company(self):
        print self.env['res.company']._company_default_get('smart_hr')
        return self.env['res.company']._company_default_get('smart_hr').id

    create_date = fields.Datetime(string=u'تاريخ الطلب', default=fields.Datetime.now(), readonly=1)
    demand_owner_id = fields.Many2one('hr.employee', string='صاحب الطلب', default=lambda self: self.env['hr.employee'].search([('user_id', '=', self._uid)], limit=1), required=1, readonly=1)
    employee_id = fields.Many2one('hr.employee', string=u'الموظف', required=1, readonly=1, states={'new': [('readonly', 0)]})
    comm_type = fields.Many2one('hr.employee.commissioning.type', string=u'نوع التكليف', required=1, readonly=1, states={'new': [('readonly', 0)]})
    date_from = fields.Date(string=u'التاريخ من ', default=fields.Datetime.now(), readonly=1, states={'new': [('readonly', 0)]})
    date_to = fields.Date(string=u'التاريخ الى', compute='_compute_date_to', store=True)
    duration = fields.Integer(string=u'الأيام', required=1, readonly=1, states={'new': [('readonly', 0)]})
    state = fields.Selection([('new', u'طلب'),
                              ('pm', u'شؤون الموظفين'),
                              ('done', u'اعتمدت'),
                              ('refused', u'رفض'),
                              ], readonly=1, default='new', string=u'الحالة')
    governmental_entity = fields.Many2one('res.partner', string=u'الجهة الحكومية', domain=[('company_type', '=', 'governmental_entity')], default=_get_default_company)
    task_ids = fields.One2many('hr.employee.task', 'comm_id', string=u'المهام')
    note = fields.Text(string=u'ملاحظات')
    city = fields.Many2one('res.city', string=u'المدينة', required=1)

    @api.multi
    @api.depends('date_from', 'duration')
    def _compute_date_to(self):
        self.ensure_one()
        if self.date_from and self.duration:
            new_date_to = fields.Date.from_string(self.date_from) + timedelta(days=self.duration)
            self.date_to = new_date_to
        elif self.date_from:
                self.date_to = self.date_from

    @api.multi
    @api.constrains('employee_id')
    def check_constrains(self):
        self.ensure_one()
        hr_config = self.env['hr.setting'].search([], limit=1)
        if hr_config:
            # check if there is another commissiong for the employee
            comm_count = self.env['hr.employee.commissioning'].search_count([('state', '=', 'done'), ('employee_id', '=', self.employee_id.id), ('date_to', '>=', self.date_from)])
            if comm_count > 0:
                raise ValidationError(u"لا يمكن إنشاء إعارة قبل إتمام مدة أخر إعارة للموظف.")

    @api.multi
    def action_new(self):
        self.ensure_one()
        self.state = 'new'

    @api.multi
    def action_pm(self):
        self.ensure_one()
        self.state = 'pm'

    @api.multi
    def action_refused(self):
        self.ensure_one()
        self.state = 'pm'

    @api.multi
    def action_done(self):
        self.ensure_one()
        self.state = 'done'


class HrEmployeeCommissioningType(models.Model):
    _name = 'hr.employee.commissioning.type'
    _description = u'نوع التكليف'

    name = fields.Char(string=u'نوع التكليف')
