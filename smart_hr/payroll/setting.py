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

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            name = '[%s] %s' % (record.code, record.name)
            result.append((record.id, name))
        return result

    @api.multi
    def unlink(self):
        self.ensure_one()
        if self.env.ref('smart_hr.hr_allowance_type_01') == self:
            raise ValidationError(u"لا يمكن حذف هذا النوع! ")
        return super(HrAllowanceType, self).unlink()


class HrRewardType(models.Model):
    _name = 'hr.reward.type'
    _description = u'أنواع المكافآت‬'

    name = fields.Char(string='المسمى', required=1)
    code = fields.Char(string='الرمز')
    note = fields.Text(string='ملاحظات')
    sequence = fields.Integer(string='الترتيب')

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

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            name = '[%s] %s' % (record.code, record.name)
            result.append((record.id, name))
        return result


class HrInsuranceType(models.Model):
    _name = 'hr.insurance.type'
    _description = u'أنواع التأمين'

    name = fields.Char(string='المسمى', required=1)
    code = fields.Char(string='الرمز')
    note = fields.Text(string='ملاحظات')

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            name = '[%s] %s' % (record.code, record.name)
            result.append((record.id, name))
        return result


class HrIncrease(models.Model):
    _name = 'hr.increase.type'
    _description = u'أنواع العلاوة'

    name = fields.Char(string='المسمى', required=1)
    code = fields.Char(string='الرمز')
    note = fields.Text(string='ملاحظات')

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            name = '[%s] %s' % (record.code, record.name)
            result.append((record.id, name))
        return result
    
    