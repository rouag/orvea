# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


class HrAllowanceType(models.Model):
    _name = 'hr.allowance.type'
    _description = u'أنواع البدلات'

    name = fields.Char(string='المسمى', required=1)
    code = fields.Char(string='الرمز')
    note = fields.Text(string='ملاحظات')
    sequence = fields.Integer(string='الترتيب')
    compute_method = fields.Selection([('amount', 'مبلغ'),
                                       ('percentage', 'نسبة من الراتب الأساسي'),
                                       ('salary_grid', 'تحتسب من سلم الرواتب'),
                                       ('job', 'تحتسب من  الوظيفة'),
                                       ('job_location', 'تحتسب  حسب مكان العمل')], string='طريقة الإحتساب')
    amount = fields.Float(string='المبلغ')
    percentage = fields.Float(string='النسبة')

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            name = '[%s] %s' % (record.code, record.name)
            result.append((record.id, name))
        return result


class HrRewardType(models.Model):
    _name = 'hr.reward.type'
    _description = u'أنواع المكافآت‬'

    name = fields.Char(string='المسمى', required=1)
    code = fields.Char(string='الرمز')
    note = fields.Text(string='ملاحظات')
    sequence = fields.Integer(string='الترتيب')
    compute_method = fields.Selection([('amount', 'مبلغ'),
                                       ('percentage', 'نسبة من الراتب الأساسي'),
                                       ('salary_grid', 'تحتسب من سلم الرواتب'),
                                       ('job', 'تحتسب من  الوظيفة'),
                                       ('job_location', 'تحتسب  حسب مكان العمل')], string='طريقة الإحتساب')
    amount = fields.Float(string='المبلغ')
    percentage = fields.Float(string='النسبة')
    # TODO: whay type_id,min_degree_id,max_degree_id
    type_id = fields.Many2one('salary.grid.type', string='الصنف')
    min_degree_id = fields.Many2one('salary.grid.degree', string='الدرجة من ',)
    max_degree_id = fields.Many2one('salary.grid.degree', string='إلى',)

    @api.multi
    @api.constrains('min_degree_id', 'max_degree_id')
    def _check_degree(self):
        for obj in self:
            min_degree_id = obj.min_degree_id.sequence
            max_degree_id = obj.max_degree_id.sequence
            if min_degree_id > max_degree_id:
                raise ValidationError(u'الرجاء التثبت من الدرجات الدرجة من تكون أصغر من درجة إلى ')
            return True

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            name = '[%s] %s' % (record.code, record.name)
            result.append((record.id, name))
        return result


class HrIndemnity(models.Model):
    _name = 'hr.indemnity.type'
    _description = u'أنواع التعويضات'

    name = fields.Char(string='المسمى', required=1)
    code = fields.Char(string='الرمز')
    note = fields.Text(string='ملاحظات')
    sequence = fields.Integer(string='الترتيب')
    compute_method = fields.Selection([('amount', 'مبلغ'),
                                       ('percentage', 'نسبة من الراتب الأساسي'),
                                       ('salary_grid', 'تحتسب من سلم الرواتب'),
                                       ('job', 'تحتسب من  الوظيفة'),
                                       ('job_location', 'تحتسب  حسب مكان العمل')], string='طريقة الإحتساب')
    amount = fields.Float(string='المبلغ')
    percentage = fields.Float(string='النسبة')
    # TODO: whay type_id,min_degree_id,max_degree_id
    type_id = fields.Many2one('salary.grid.type', string='الصنف')
    min_degree_id = fields.Many2one('salary.grid.degree', string='الدرجة من ')
    max_degree_id = fields.Many2one('salary.grid.degree', string='إلى')
    transport_allow = fields.Float(string='قيمة البدل')

    @api.multi
    @api.constrains('min_degree_id', 'max_degree_id')
    def _check_degree(self):
        for obj in self:
            min_degree_id = obj.min_degree_id.sequence
            max_degree_id = obj.max_degree_id.sequence
            if min_degree_id > max_degree_id:
                raise ValidationError(u'الرجاء التثبت من الدرجات الدرجة من تكون أصغر من درجة إلى ')
            return True

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            name = '[%s] %s' % (record.code, record.name)
            result.append((record.id, name))
        return result
