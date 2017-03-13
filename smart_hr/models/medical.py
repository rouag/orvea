# -*- coding: utf-8 -*-


from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning


class MedicalCategory(models.Model):
    _name = 'medical.category'
    _description = u'الفحص الطبي'

    name = fields.Char(string=u'أسم الفحص بالعربية', required=1)
    name_en = fields.Char(string=u'أسم الفحص باﻷنقلزية')
    code = fields.Char(string=u'الرمز')
    exams = fields.One2many('medical.exam', 'category', string=u'اﻷختبارات')
    position = fields.Selection([('right', u'يمين'),
                                 ('left', u'يسار'),
                                 ('bottom', u'أسفل'),
                                 ], string=u"الموقع في التقرير", default='right')


class MedicalExam(models.Model):
    _name = 'medical.exam'
    _description = u' أختبار الفحص الطبي'

    name = fields.Char(string=u'أسم اﻷختبار بالعربية', required=1)
    name_en = fields.Char(string=u'أسم اﻷختبار باﻷنقلزية')
    code = fields.Char(string=u'الرمز', required=1)
    category = fields.Many2one('medical.category')


class MedicalExamResult(models.Model):
    _name = 'medical.exam.result'
    _description = u' أختبار الفحص الطبي'
    _rec_name = 'exam'

    exam = fields.Many2one('medical.exam', string=u'الاختبار')
    exam_en = fields.Char(string=u'أسم اﻷختبار باﻷنقلزية', related="exam.name_en")
    result = fields.Boolean(string=u'سليم')
    employee_exam = fields.Many2one('employee.medical.exam', string=u'أختبار الفحص الطبي')


class EmployeeMedicalExam(models.Model):
    _name = 'employee.medical.exam'
    _description = u' أختبار الفحص الطبي لموظف معين'
    _rec_name = 'employee'

    sequence = fields.Char(string=u'رقم الفحص', readonly=1)
    employee = fields.Many2one('hr.employee', string=u'الموظف', required=1)
    hospital = fields.Many2one('res.partner', string=u'المستشفى', required=1)
    job = fields.Many2one('hr.job', string=u'الوظيفة المرشح لها', compute='_get_job_employee', readonly=True)
    exams_results = fields.One2many('medical.exam.result', 'employee_exam', string=u'اﻷختبارات')
    exam_date = fields.Date(string=u'تاريخ الفحص')

    @api.depends('employee')
    def _get_job_employee(self):
        if self.employee:
            self.job = self.employee.job_id

    @api.onchange('exams_results')
    def onchange_exams_results(self):
        if len(self.exams_results) > 0:
            # get last added exam
            last_added_exam = self.exams_results[len(self.exams_results) - 1].exam
            # check if the last added exam exit only one time
            count = 0
            for rec in self.exams_results:
                if rec.exam == last_added_exam:
                    count += 1
                    if count > 1:
                        raise Warning(_(u'إختبار ' + last_added_exam.name + u' يوجد أكثر من مرة.'))

                    """TODO: remove duplicated exam from one2manty field"""

    @api.model
    def create(self, vals):
        code = self.env['ir.sequence'].sudo().next_by_code('seq.employee.medical.exam')
        vals['sequence'] = code
        return super(EmployeeMedicalExam, self).create(vals)
