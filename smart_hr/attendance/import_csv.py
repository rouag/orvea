# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------

import base64
from openerp.osv import osv
from openerp import fields, models, api, _
from tempfile import TemporaryFile
import csv
from openerp.tools.translate import _


class import_csv(osv.osv):
    
    _name = 'import.import'
    _inherit = ['mail.thread']  
    _description = 'Import Tools' 
    _order = 'id desc' 
    

    name= fields.Char(u'إسم الملف', size=128)
    description= fields.Text('Description de fichier')
    data = fields.Binary(u'الملف', required=True)
    create_uid = fields.Many2one('res.users', u'Importé par', readonly=True)
    create_date =fields.Datetime(u"Date d'importation")
    
    
   
   
   
    @api.multi
    def import_file(self):
        if self._context is None:
            context = {}
        this = self.browse(self._ids[0])   
        quotechar='"'
        delimiter=','
        fileobj = TemporaryFile('w+')
        sourceEncoding = 'windows-1252'
        targetEncoding = "utf-8"   
        
        fileobj.write((base64.decodestring(this.data)))   
        fileobj.seek(0)                                    
        reader = csv.DictReader(fileobj, quotechar=str(quotechar), delimiter=str(delimiter))  
        employee=self.env['hr.employee'].search([])
        print employee.number
        for row  in reader :  
            

            emp_id=self.env['hr.employee'].search([('number','=',str(row['empid'].strip(" ")))])
            
            ## all emp
            if emp_id:
                
            #create move line
                if str(row['TrnType'])=='1':
                    action='sign_in'
                else:
                    action='sign_out'
                    
                    
                hr_attendance_val={
                                'employee_id':emp_id.id,
                                'name':row['trndatetime2'],
                                'action':action,
                                'mac_id':row['MacName'],
                                }
                self.env['hr.attendance'].create( hr_attendance_val)
              
         
        
        return True


