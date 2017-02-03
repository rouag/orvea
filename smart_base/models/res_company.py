# -*- coding: utf-8 -*-


from openerp import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    report_header = fields.Binary(string=' صورة رأس الصفحة ', attachment=1)
    report_footer = fields.Binary(string=' صورة أخر الصفحة ', attachment=1)
    report_header_speech = fields.Binary(string=' صورة رأس الصفحة ', attachment=1)
    report_footer_speech = fields.Binary(string=' صورة أخر الصفحة ', attachment=1)
    company_president = fields.Many2one('res.users', string=' الرئيس' )