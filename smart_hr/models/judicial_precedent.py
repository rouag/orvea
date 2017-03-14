# -*- coding: utf-8 -*-


from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning


class JudicialPrecedent(models.Model):
    _name = 'judicial.precedent'
    _description = u'السوابق العدلية'
    name = fields.Char(string=u'الإسم', required=1)


class EmployeeJudicialPrecedent(models.Model):
    _name = 'employee.judicial.precedent'
    _description = u' السوابق العدلية'
    _rec_name = 'judicial_precident'

    judicial_precident = fields.Many2one('judicial.precedent', string=u'السابقة العدلية')
    date = fields.Date(string=u'التاريخ')
    periode = fields.Integer(string=u'المدة')
    employee_judicial_precedents = fields.Many2one('employee.judicial.precedent.order',
                                                   string=u'طلب إستسفار السوابق العدلية')


class EmployeeJudicialPrecedentOrdre(models.Model):
    _name = 'employee.judicial.precedent.order'
    _description = u'طلب إستسفار السوابق العدلية'
    _rec_name = 'employee'
    employee = fields.Many2one('hr.employee', string=u'الموظف', required=1)
    judicial_precedents = fields.One2many('employee.judicial.precedent', 'employee_judicial_precedents',
                                          string=u'السوابق العدلية')
