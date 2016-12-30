# -*- coding: utf-8 -*-


from openerp import models, fields


class BaseNotification(models.Model):
    _name = 'base.notification'

    user_id = fields.Many2one('res.users', string='employee')
    show_date = fields.Datetime(string='show date')
    message = fields.Char(string='Message')
    title = fields.Char(string='Title')
    to_read = fields.Boolean(string='To read')
    res_model = fields.Many2one('ir.model', string='Object')
    res_id = fields.Integer(string='Res ID')
