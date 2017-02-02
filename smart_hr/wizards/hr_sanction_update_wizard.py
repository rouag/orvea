 # -*- coding: utf-8 -*-

from openerp import api, fields, models, _
    


class WizardSanctionUpdate(models.TransientModel):
    _name = 'wizard.sanction.update'
 
 
 
    name = fields.Char(string='رقم القرار', required=1 )
    order_date = fields.Date(string='تاريخ العقوبة',default=fields.Datetime.now(),readonly=1) 
    sanction_text = fields.Text(string=u'محتوى العقوبة' )
    order_picture = fields.Binary(string='صورة القرار', required=1) 
    order_picture_name = fields.Char(string='صورة القرار') 
   # line_ids = fields.One2many('wizard.hr.sanction.ligne', 'wizard_sanction_id', string=u'العقوبات')
    type_sanction = fields.Many2one('hr.type.sanction',string=u'العقوبة',required=1)
    date_sanction_start = fields.Date(string='تاريخ بدأ العقوبة') 
    date_sanction_end = fields.Date(string='تاريخ الإلغاء') 
    nb_days_new = fields.Integer(string=u'عدد أيام ')
     
    @api.depends('date_sanction_start', 'date_sanction_end')
    def _compute_delay_days(self):
        if self.date_sanction_start and self.date_sanction_end:
            date_sanction_start = fields.Date.from_string(self.date_sanction_start)
            date_sanction_end = fields.Date.from_string(self.date_sanction_end)
            if date_sanction_end < date_sanction_start:
                raise ValidationError(u"الرجاء التأكد من تاريخ الإلغاء.")
            nb_days = (date_sanction_end - date_sanction_start).days 
            
   
#
     
 
                         
    @api.multi
    def action_exclusion(self):
        ids=self._ids
        cr = self._cr
        uid = self._uid
        context = self._context
        model_name=context.get('active_model')
        form_id = context.get('active_id')
        obj = self.pool.get(model_name).browse(cr,uid,form_id,context)
      
        date_sanction_start_old =obj.date_sanction_start
        date_sanction_end_old = obj.date_sanction_end
        old_name = obj.name
        type_sanction_old = obj.type_sanction.id
        nb_days_old = obj.nb_days
        obj.name=self.name
        
        obj.nb_days = self.nb_days_new
        obj.type_sanction = self.type_sanction.id   
        obj.order_picture = self.order_picture
        obj.order_picture_name = self.order_picture_name
        obj.date_sanction_start = self.date_sanction_start    
        obj.date_sanction_end = self.date_sanction_end  
        
        
        sanction_line_id = self._context.get('active_id', False)
        if sanction_line_id:
            for rec in obj.line_ids:
                diff_sanction_obj = self.env['hr.difference.sanction']
                self.env['hr.difference.sanction'].create({
                                                        'name': old_name,
                                                        'order_new': self.name,
                                                        'date_sanction_start_old' : date_sanction_start_old,
                                                        'date_sanction_end_old' : date_sanction_end_old,
                                                        'type_sanction_new' : self.type_sanction.id,
                                                         'type_sanction_old'  : type_sanction_old,
                                                        'date_sanction_start_new' : self.date_sanction_start,
                                                        'date_sanction_end_new' : self.date_sanction_end,
                                                        'order_update' : self.order_date,
                                                        'employee_id' :rec.employee_id.id,
                                                        'nb_days_old' : nb_days_old,
                                                        'nb_days_new' : self.nb_days_new,
                                                        'state' :rec.state,
                                                        'order_picture' : self.order_picture,
                                                        'order_picture_name' : self.order_picture_name,
                                                
                                                  
                                                           })
             
#       
       