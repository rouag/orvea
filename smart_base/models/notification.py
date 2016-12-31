# -*- coding: utf-8 -*-


from openerp import models, fields


class BaseNotification(models.Model):
    _name = 'base.notification'
    _rec_name = 'title'

    user_id = fields.Many2one('res.users', string='employee')
    show_date = fields.Datetime(string='show date')
    message = fields.Char(string='Message')
    title = fields.Char(string='Title')
    to_read = fields.Boolean(string='To read')
    res_model = fields.Char(string='model name')
    res_id = fields.Integer(string='Res ID')
    res_action = fields.Char(string='action name (module_name.action_name)')
