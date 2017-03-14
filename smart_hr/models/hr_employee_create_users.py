# -*- coding: utf-8 -*-
from openerp import models, fields, api, _


class HrEmployeeCreateUsers(models.Model):
    _name = 'hr.employee.create.users'
    _description = u'انشاء مستخدم' 

    name = fields.Char(string=u'الرقم')
    employee_ids = fields.Many2many('hr.employee', string=u'الموظف', required=1)
    date = fields.Date(string=u'التاريخ ', default=fields.Datetime.now(), readonly=1)
    state = fields.Selection([('draft', u'مسودة'),
                              ('done', u'تم')], default='draft', readonly=1)

    @api.multi
    def button_done(self):
        self.ensure_one()
        for emp in self.employee_ids:
            if emp.work_email:
                user = self.env['res.users'].create({'name': emp.display_name,
                                                     'login': emp.work_email,
                                                     'email': emp.work_email,
                                                     'lang': 'ar_SY',
                                                     })
                emp.user_id = user
            else:
                raise Warning(_('الرجاء تعبئة البريد الإلكتروني.'))

        self.state = 'done'

    @api.model
    def create(self, vals):
        res = super(HrEmployeeCreateUsers, self).create(vals)
        vals['name'] = self.env['ir.sequence'].get('hr.employee.create.users.seq')
        res.write(vals)
        return res
