# -*- coding: utf-8 -*-

from openerp import fields, models, api


class HrScholarshipcutoffWizard(models.TransientModel):

    _name = "hr.scholarship.cutoff.wizard"
    _description = "Scholarship cutoff Wizard"

    date_cutoff = fields.Date(string=u'تاريخ القطع', required=1)

    @api.multi
    def button_add_history(self):
        cx = self.env.context or {}
        model_obj = self.env[cx.get('active_model')]
        rec_id = model_obj.browse(cx.get('active_id'))
        for wiz in self:
            rec_id.write({'date_to': wiz.date_cutoff,
                          'state': 'cutoff'
                          })
            rec_id.onchange_dates()
            self.env['hr.scholarship.history'].create({'name': u'قطع',
                                                       'scholarship_id': rec_id.id,
                                                       'date_from': rec_id.date_from,
                                                       'duration': rec_id.duration,
                                                       'date_to': wiz.date_cutoff
                                                       })
