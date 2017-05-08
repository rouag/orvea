# -*- coding: utf-8 -*-


from openerp import models, fields, api, _


class Contry(models.Model):
    _inherit = 'res.country'
    _description = u'البلدان'

    code = fields.Text(string='الرمز')
    code_nat = fields.Text(string='الرمز', )
    national = fields.Char(string='الجنسية', )

    @api.multi
    def name_get(self):
        if u'compute_name' in self._context:
            return getattr(self, self._context[u'compute_name'])()
        else:
            return super(Contry, self).name_get()

    def _get_natinality(self):
        res = []
        for record in self:
            if record.national:
                res.append((record.id, record.national))
        return res


class Region(models.Model):

    _inherit = 'city.side'
    _description = u'الجهات'

    contry = fields.Many2one('res.country', string='البلاد')
