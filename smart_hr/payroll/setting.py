# -*- coding: utf-8 -*-


from openerp import models, fields, api, _


class HrAllowance(models.Model):
    _name = 'hr.allowance'
    _description = u'البدلات'

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


class HrReward(models.Model):
    _name = 'hr.reward'
    _description = u'المكافآت‬'

    name = fields.Char(string='المسمى', required=1)
    code = fields.Char(string='الرمز')
    note = fields.Text(string='ملاحظات')
    sequence = fields.Integer(string='الترتيب')
    type_id = fields.Many2one('salary.grid.type', string='الصنف')
    min_degree_id = fields.Many2one('salary.grid.degree', string='الدرجة من ',) 
    max_degree_id = fields.Many2one('salary.grid.degree', string='إلى',) 
    nb_salary = fields.Float(string='عدد الرواتب') 
    note = fields.Text(string='ملاحظات')
    sequence = fields.Integer(string='الترتيب')
    
    @api.multi
    @api.constrains('min_degree_id','max_degree_id')
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
    _name = 'hr.indemnity'
    _description = u'التعويضات'

    name = fields.Char(string='المسمى', required=1)
    code = fields.Char(string='الرمز')
    note = fields.Text(string='ملاحظات')
    sequence = fields.Integer(string='الترتيب')
    type_id = fields.Many2one('salary.grid.type', string='الصنف')
    min_degree_id = fields.Many2one('salary.grid.degree', string='الدرجة من ') 
    max_degree_id = fields.Many2one('salary.grid.degree', string='إلى') 
    transport_allow = fields.Float(string='قيمة البدل') 
       
    @api.multi
    @api.constrains('min_degree_id','max_degree_id')
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
