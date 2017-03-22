# -*- coding: utf-8 -*-

from openerp import fields, models, api


class HrScholarshipextendWizard(models.TransientModel):

    _name = "hr.scholarship.extend.wizard"
    _description = "Scholarship extend Wizard"

    date_from = fields.Date(string=u'تاريخ من', required=1, readonly=1)
    date_to = fields.Date(string=u'تاريخ إلى', required=1)
    order_number = fields.Char(string=u'رقم الخطاب', required=1)
    order_date = fields.Date(string=u'تاريخ الخطاب', required=1)
    file_decision = fields.Binary(string=u'الخطاب', attachment=True, required=1)
    file_decision_name = fields.Char(string=u'اسم الخطاب')

    @api.multi
    def button_add_history(self):
        cx = self.env.context or {}
        model_obj = self.env[cx.get('active_model')]
        rec_id = model_obj.browse(cx.get('active_id'))
        for wiz in self:
            rec_id.write({'date_to': wiz.date_to,
                          'is_extension': True,
                          'order_number': wiz.order_number,
                          'order_date': wiz.order_date,
                          'file_decision': wiz.file_decision
                          })
            self.env['hr.scholarship.history'].create({'name': u'تمديد',
                                                       'scholarship_id': rec_id.id
                                                       })
