# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import Warning
from openerp.exceptions import ValidationError
from openerp.exceptions import UserError
from datetime import date, datetime, timedelta


class HrSanction(models.Model):
    _name = 'hr.sanction'
    _inherit = ['mail.thread']
    _order = 'id desc'
    _description = u'إجراء العقوبات'

    name = fields.Char(string='رقم القرار' ,readonly=1, related='decission_id.name')
    order_date = fields.Date(string='تاريخ القرار', readonly=1,related='decission_id.date' )
    sanction_text = fields.Text(string=u'محتوى العقوبة', readonly=1, states={'draft': [('readonly', 0)]})
    order_picture = fields.Binary(string='صورة القرار', readonly=1, states={'draft': [('readonly', 0)]},
                                  attachment=True)
    order_picture_name = fields.Char(string='صورة القرار', readonly=1, states={'draft': [('readonly', 0)]})
    type_sanction = fields.Many2one('hr.type.sanction', string=u' نوع العقوبة ', required=1, readonly=1,
                                    states={'draft': [('readonly', 0)]})
    date_sanction_start = fields.Date(string='تاريخ بدأ العقوبة', required=1, readonly=1,
                                      states={'draft': [('readonly', 0)]})
    date_sanction_end = fields.Date(string='تاريخ الإلغاء', readonly=1, states={'draft': [('readonly', 0)]})
    note = fields.Text(string=u'الملاحظات', readonly=1, states={'draft': [('readonly', 0)]})
    number_sanction = fields.Char(string='رقم الخطاب  ')
    date_sanction = fields.Date(string='تاريخ الخطاب ')
    file_sanction = fields.Binary(string='صورة الخطاب ', attachment=True)
    file_sanction_name = fields.Char(string='صورة الخطاب ')
    decission_id = fields.Many2one('hr.decision', string=u'القرارات')
    # update sanction
    difference_ids = fields.One2many('hr.sanction.ligne', 'sanction_id', string=u'العقوبات', readonly=1,
                                     states={'draft': [('readonly', 0)]})
    line_ids = fields.One2many('hr.sanction.ligne', 'sanction_id', string=u'العقوبات', readonly=1,
                               states={'draft': [('readonly', 0)]})
    history_ids = fields.One2many('hr.sanction.history', 'sanction_id', string='سجل التغييرات', readonly=1)
    state = fields.Selection([('draft', '  طلب'),
                              ('waiting', '  صاحب صلاحية العقوبات'),
                              ('extern', 'جهة خارجية'),
                              ('done', 'اعتمدت'),
                              ('update', 'تعديل'),
                              ('cancel', 'ملغاة')], string='الحالة', readonly=1, default='draft')



    @api.multi
    def button_deprivation_premium_sanction(self):
        decision_obj= self.env['hr.decision']
        if self.decission_id:
            decission_id = self.decission_id.id
        else :
            decision_type_id = 1
            decision_date = fields.Date.today() # new date
            if self.type_sanction:
                decision_type_id = self.env.ref('smart_hr.data_decision_deprivation_premium').id
            # create decission
            decission_val={
              #  'name': self.name,
                'decision_type_id':decision_type_id,
                'date':decision_date,
                'employee_id' :False}
            decision = decision_obj.create(decission_val)
            decision.text = decision.replace_text(False,decision_date,decision_type_id,'employee',args={'DATE':decision_date})
            decission_id = decision.id
            self.decission_id =  decission_id
        return {
            'name': u'قرار حرمان من العلاوة',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'hr.decision',
            'view_id': self.env.ref('smart_hr.hr_decision_wizard_form').id,
            'type': 'ir.actions.act_window',
            'res_id': decission_id,
            'target': 'new'
            }


   




    @api.multi
    def button_cancel_sanction(self):
        # TODO:
        sanction = self.search([('state', '=', 'done')])

    @api.multi
    def button_update_sanction(self):
        for sanction in self:
            sanction.state = 'update'

    @api.multi
    def action_update(self):
        for sanction in self:
            sanction.state = 'done'

    # TODO: check this function  always display this message خلل في تسلسل العقوبات
    @api.multi
    def action_draft(self):
        for rec in self:
            # previous_code = str(int(rec.type_sanction.code) - 1)
            # current_code = rec.type_sanction.code
            # employee_ids = []
            # if int(current_code) >= 1:
            #     sanction_ligne_ids = rec.env['hr.sanction.ligne'].search(['&', ('state', '=', 'done'),
            #                                                               '|', ('type_sanction.code', '=', previous_code),
            #                                                               ('type_sanction.code', '=', current_code),
            #                                                               ])
            #     employee_ids = [line.employee_id for line in sanction_ligne_ids]
            # # add employee tht dosent have any sanction yet
            # if int(current_code) == 1:
            #     employee_ids += rec.env['hr.employee'].search([('sanction_ids', '=', False)])
            # # add employee tht dosent have any sanction yet
            # for line in rec.line_ids:
            #     if line.employee_id not in employee_ids:
            #         raise ValidationError(u"لا يمكن تنفيذ هذه العقوبة للموظف  : "+ unicode(line.employee_id.display_name) +u" \n"+ u"-لخلل في تسلسل العقوبات.")
            rec.state = 'waiting'

    @api.multi
    def button_refuse(self):
        for sanction in self:
            sanction.state = 'draft'

    @api.multi
    def action_refuse_update(self):
        for sanction in self:
            sanction.state = 'done'

    @api.multi
    def action_waiting(self):
        for sanction in self:
            sanction.state = 'extern'

    @api.multi
    def action_extern(self):
        self.ensure_one()
        for rec in self.line_ids:
            rec.state = 'done'
        self.state = 'done'

    @api.multi
    def action_cancel(self):
        self.state = 'cancel'
        self.date_sanction_end = fields.Date.from_string(fields.Date.today())
        for line in self.line_ids:
            if line.deduction == True :
                raise ValidationError(u"لا يمكن إلغاء  العقوبة بعد تطبيق حسم على موظف")
            if self.date_sanction_end > self.date_sanction_start :
                raise ValidationError(u"لا يمكن إلغاء  العقوبة بعد تبدأ العقوبة")
            line.state = 'cancel'

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_(u'لا يمكن حذف العقوبة  إلا في حالة طلب !'))
        return super(HrSanction, self).unlink()


class HrSanctionLigne(models.Model):
    _name = 'hr.sanction.ligne'
    _description = u' العقوبات'

    sanction_id = fields.Many2one('hr.sanction', string=' العقوبات', ondelete='cascade')
    employee_id = fields.Many2one('hr.employee', string=u' إسم الموظف', required=1)
    type_sanction = fields.Many2one('hr.type.sanction', related='sanction_id.type_sanction', string=u'العقوبة')
    mast = fields.Boolean(string='سارية', default=True)
    deduction = fields.Boolean(string=u'حسم', default=False)
    days_number = fields.Integer(string='عدد أيام ')
    amount = fields.Integer(string='مبلغ')
    raison = fields.Char(string='السبب ')
    days_difference = fields.Integer(string='الفروقات بالأيام ')
    amount_difference = fields.Integer(string='الفروقات بالمبلغ ')
    state_sanction = fields.Selection(related='sanction_id.state', store=True, readonly=True, string='الحالة')
    state = fields.Selection([('waiting', 'في إنتظار العقوبة'),
                              ('excluded', 'مستبعد'),
                              ('done', 'تم العقوبة'),
                              ('cancel', 'ملغى')], string='الحالة', readonly=1, default='waiting')
 
    @api.onchange('employee_id')
    def onchange_employee_id(self):
        if not self.employee_id:
            res = {}
            grade_min = self.sanction_id.type_sanction.min_grade_id.code
            grade_max = self.sanction_id.type_sanction.max_grade_id.code
            employee_ids = self.env['hr.employee'].search(
                [('grade_id.code', '>=', grade_min), ('grade_id.code', '<=', grade_max)]).ids
            res['domain'] = {'employee_id': [('id', 'in', employee_ids)]}
            return res


class HrTypeSanction(models.Model):
    _name = 'hr.type.sanction'
    _description = u'أنواع العقوبات'

    name = fields.Char(string='المسمى', required=1)
    code = fields.Char(string='الرمز')
    min_grade_id = fields.Many2one('salary.grid.grade', string='المرتبة من ')
    max_grade_id = fields.Many2one('salary.grid.grade', string='إلى')
    deduction = fields.Boolean(string='تستوجب حسم')
    sanction_manager = fields.Boolean(string=u' صاحب صلاحية العقوبات ', default=True)
    sanction_responsable = fields.Boolean(string=u' مسؤول على العقوبات ', default=True)
    sanction_decider = fields.Boolean(string=u' موافقة المقام السامي  ', default=False)


class HrSanctionHistory(models.Model):
    _name = 'hr.sanction.history'

    name = fields.Char(string='رقم القرار')
    sanction_id = fields.Many2one('hr.sanction', string=' العقوبات', ondelete='cascade')
    employee_id = fields.Many2one('hr.employee', string=' الموظف')
    action = fields.Char(string='الإجراء')
    reason = fields.Char(string='السبب')
    order_date = fields.Date(string='تاريخ القرار')
