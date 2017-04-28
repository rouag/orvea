# -*- coding: utf-8 -*-

from openerp import fields, models, api


class HrScholarshipextendWizard(models.TransientModel):

    _name = "hr.scholarship.extend.wizard"
    _description = "Scholarship extend Wizard"

    date_from = fields.Date(string=u'تاريخ من', required=1, readonly=1)
    date_to = fields.Date(string=u'تاريخ إلى', required=1)
    duration = fields.Integer(string=u'عدد الأيام ', required=1, compute='_compute_duration', readonly=1)
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
                          'duration': rec_id.duration + wiz.duration
                          })
            self.env['hr.scholarship.history'].create({'name': u'تمديد',
                                                        'scholarship_id': rec_id.id,
                                                        'order_number': wiz.order_number,
                                                        'order_date': wiz.order_date,
                                                        'file_decision': wiz.file_decision,
                                                        'date_from': wiz.date_from,
                                                        'duration': wiz.duration,
                                                        'date_to':wiz.date_to
                                                       })
    @api.one
    @api.depends('date_from', 'date_to')
    def _compute_duration(self):
        if self.date_from and self.date_to:
            self.duration = self.env['hr.smart.utils'].compute_duration(self.date_from, self.date_to)