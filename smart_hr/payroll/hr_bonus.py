# -*- coding: utf-8 -*-

from openerp import models, api, fields, _
from openerp.exceptions import ValidationError


class hrBonus(models.Model):
    _name = 'hr.bonus'
    _inherit = ['mail.thread']
    _order = 'id desc'
    _description = u'المزايا المالية'

    name = fields.Char(string=' المسمى', required=1, readonly=1, states={'new': [('readonly', 0)]})
    number_decision = fields.Char(string='رقم القرار', required=1, readonly=1, states={'new': [('readonly', 0)]})
    date_decision = fields.Date(string=' تاريخ القرار', required=1, readonly=1, states={'new': [('readonly', 0)]})
    date = fields.Date(string=' التاريخ ', required=1, readonly=1, states={'new': [('readonly', 0)]})
    date_from = fields.Date(string='تاريخ من', required=1, readonly=1, states={'new': [('readonly', 0)]})
    date_to = fields.Date(string='إلى', required=1, readonly=1, states={'new': [('readonly', 0)]})
    type = fields.Selection([('allowance', 'بدل'), ('reward', 'مكافأة'), ('indemnity', 'تعويض')], string='النوع', required=1, readonly=1, states={'new': [('readonly', 0)]})
    allowance_id = fields.Many2one('hr.allowance.type', string='البدل', readonly=1, states={'new': [('readonly', 0)]})
    reward_id = fields.Many2one('hr.reward.type', string='المكافأة', readonly=1, states={'new': [('readonly', 0)]})
    indemnity_id = fields.Many2one('hr.indemnity.type', string='التعويض', readonly=1, states={'new': [('readonly', 0)]})
    state = fields.Selection([('new', 'طلب'),
                              ('waiting', 'في إنتظار الإعتماد'),
                              ('cancel', 'مرفوض'),
                              ('done', 'اعتمدت')], string='الحالة', readonly=1, default='new')
    line_ids = fields.One2many('hr.bonus.line', 'bonus_id', string='التفاصيل', readonly=1, states={'new': [('readonly', 0)]})
    history_ids = fields.One2many('hr.bonus.history', 'bonus_id', string='سجل التغييرات', readonly=1)

    @api.onchange('date_from', 'date_to')
    def onchange_date(self):
        if self.date_from and self.date_to and self.date_from >= self.date_to:
            self.date_to = False
            warning = {'title': _('تحذير!'), 'message': _(u'تاريخ من يجب ان يكون أصغر من تاريخ الى')}
            return {'warning': warning}

    @api.one
    def action_waiting(self):
        self.state = 'waiting'

    @api.multi
    def action_done(self):
        self.state = 'done'

    @api.one
    def action_refuse(self):
        self.state = 'cancel'


class hrBonusLine(models.Model):
    _name = 'hr.bonus.line'
    _description = u'تفاصيل المزايا المالية'

    bonus_id = fields.Many2one('hr.bonus', string='المزايا المالية', ondelete='cascade')
    employee_id = fields.Many2one('hr.employee', string='الموظف', required=1)
    number = fields.Char(related='employee_id.number', store=True, readonly=True, string=' الرقم الوظيفي')
    job_id = fields.Many2one(related='employee_id.job_id', store=True, readonly=True, string=' الوظيفة')
    department_id = fields.Many2one(related='employee_id.department_id', store=True, readonly=True, string=' القسم')
    type = fields.Selection(related='bonus_id.type', store=True, string='النوع')
    state = fields.Selection(related='bonus_id.state', store=True, string='الحالة')
    allowance_id = fields.Many2one('hr.allowance.type', string='البدل')
    reward_id = fields.Many2one('hr.reward.type', string='المكافأة')
    indemnity_id = fields.Many2one('hr.indemnity.type', string='التعويض')
    date_from = fields.Date(string='تاريخ من')
    date_to = fields.Date(string='إلى')
    amount = fields.Float(string='القيمة')
    percentage = fields.Float(string='النسبة')
    compute_method = fields.Selection([('amount', 'مبلغ'),
                                       ('percentage', 'نسبة من الراتب الأساسي'),
                                       ('salary_grid', 'تحتسب من سلم الرواتب'),
                                       ('job', 'تحتسب من  الوظيفة'),
                                       ('job_location', 'تحتسب  حسب مكان العمل')], string='طريقة الإحتساب', required=1)
    bonus_state = fields.Selection([('progress', 'ساري'),
                                    ('stop', 'إيقاف'),
                                    ('expired', 'منتهي')
                                    ], string='الحالة', readonly=1, default='progress')


class hrBonusHistory(models.Model):
    _name = 'hr.bonus.history'

    bonus_id = fields.Many2one('hr.bonus', string='المزايا المالية', ondelete='cascade')
    employee_id = fields.Many2one('hr.employee', string=' الموظف', required=1)
    action = fields.Char(string='الإجراء')
    reason = fields.Char(string='السبب', required=1,)
    number_decision = fields.Char(string='رقم القرار')
    date_decision = fields.Date(string='تاريخ القرار')