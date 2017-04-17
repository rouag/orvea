from openerp import models


class res_users(models.Model):
    _inherit = 'res.users'

    def datepicker_localization(self, cr, uid, context={}):
        user_brow_obj = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        res_lang_obj = self.pool.get('res.lang')
        lang_ids = res_lang_obj.search(cr, uid, [('code', '=', user_brow_obj.lang)])
        date_format = '%m/%d/%Y'
        lang = 'en'
        if lang_ids:
            langs = res_lang_obj.browse(cr, uid, lang_ids[0], context=context).code
            lang = langs[:2]
            date_format = res_lang_obj.browse(cr, uid, lang_ids[0], context).date_format
        return {
            'lang': str(lang) or '',
            'date_format': date_format
        }
