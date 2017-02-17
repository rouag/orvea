# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------
#
#    Copyright (C) 2014  .
#    Coded by: Borni DHIFI  (dhifi.borni@gmail.com)
#
#----------------------------------------------------------------------------

import base64
from openerp.osv import osv, fields
from openerp import tools,netsvc
from tempfile import TemporaryFile
import csv
from openerp.tools.translate import _


class import_csv(osv.osv):
    
    AVAILABLE_STATES = [
                      ('draft', 'Brouillon'),
                      ('failure', 'Echec'),
                       ('done', u'Traité'),
                     ]
    
    _name = 'import.import'
    _inherit = ['mail.thread']  
    _description = 'Import Tools' 
    _order = 'id desc' 
    
    _columns = {
        'name': fields.char(u'Nom de la pièce jointe', size=128),
        'description': fields.text('Description de fichier'),
        'data': fields.binary('Fichier', required=True),
        'create_uid': fields.many2one('res.users', u'Importé par', readonly=True),
        'create_date': fields.datetime(u"Date d'importation"),
        'state': fields.selection(AVAILABLE_STATES, 'Etat', select=True, readonly=True,) 
        }
    
    _defaults = {  
        'state' : 'draft'
        }
   
   
        
    def import_file(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        this = self.browse(cr, uid, ids[0])   
        quotechar='"'
        delimiter=';'
        fileobj = TemporaryFile('w+')
        sourceEncoding = 'windows-1252'
        targetEncoding = "utf-8"   
        
        fileobj.write((base64.decodestring(this.data)))   
        fileobj.seek(0)                                    
        reader = csv.DictReader(fileobj, quotechar=str(quotechar), delimiter=str(delimiter))         

        salary_grid_level = self.pool.get('salary.grid.degree')
        move_id=''
        all_move_ids=[]
        for row  in reader :  
            salary_grid_levele_val={
                            'name':row['name'],
                            'code':str(row['code']),
                            'sequence':str(row['code'])
                            }
            
            salary_grid_level.create(cr, uid, salary_grid_levele_val,context=context)
          
            
         
        
        return True
    
    def import_contry(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        this = self.browse(cr, uid, ids[0])   
        quotechar='"'
        delimiter=';'
        fileobj = TemporaryFile('w+')
        sourceEncoding = 'windows-1252'
        targetEncoding = "utf-8"   
        
        fileobj.write((base64.decodestring(this.data)))   
        fileobj.seek(0)                                    
        reader = csv.DictReader(fileobj, quotechar=str(quotechar), delimiter=str(delimiter))         

        country = self.pool.get('res.country')
         
        move_id=''
        all_move_ids=[]
        for row  in reader :  
            #create move line
            code = row['code']
            if code =='0001':
                code = 'SA'
            if code ==0001:
                code = 'SA'
            country_line_val={
                            'name':row['name'],
                            'code_nat':code,
                            }
            
            country.create(cr, uid, country_line_val,context=context)
            
    def import_region(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        this = self.browse(cr, uid, ids[0])   
        quotechar='"'
        delimiter=';'
        fileobj = TemporaryFile('w+')
        sourceEncoding = 'windows-1252'
        targetEncoding = "utf-8"   
        
        fileobj.write((base64.decodestring(this.data)))   
        fileobj.seek(0)                                    
        reader = csv.DictReader(fileobj, quotechar=str(quotechar), delimiter=str(delimiter))         

        city = self.pool.get('city.side')
        country = self.pool.get('res.country')
        move_id=''
        all_move_ids=[]
        for row  in reader :  
            countryname = str(row['COUNTRY_NO'])
            if countryname=='0001':
                countryname="SA"
            country_id=country.search(cr, uid, [('code_nat', '=',countryname)])
            city_line_val={
                            'name':row['name'],
                            'code':str(row['code']),
                            'contry':country_id[0]
                            }
            
            city.create(cr, uid, city_line_val,context=context)
          
            
         
        
        return True


    def import_region(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        this = self.browse(cr, uid, ids[0])   
        quotechar='"'
        delimiter=';'
        fileobj = TemporaryFile('w+')
        sourceEncoding = 'windows-1252'
        targetEncoding = "utf-8"   
        
        fileobj.write((base64.decodestring(this.data)))   
        fileobj.seek(0)                                    
        reader = csv.DictReader(fileobj, quotechar=str(quotechar), delimiter=str(delimiter))         

        city = self.pool.get('res.city')
        city_side = self.pool.get('city.side')
        move_id=''
        all_move_ids=[]
        for row  in reader : 
            side_id=False 
            
           
            print row
            
            side_ids=city_side.search(cr, uid, [('code', '=',str(row['side']))])
            if side_ids :
                    side_id=side_ids[0]
           
            
            print 'side_id',side_id
            city_line_val={
                            'name':row['name'],
                            'code':str(row['code']),
                            'city_side':side_id
                            }
            
            city.create(cr, uid, city_line_val,context=context)
          
            
         
        
        return True 
    
    def import_education_level(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        this = self.browse(cr, uid, ids[0])   
        quotechar='"'
        delimiter=';'
        fileobj = TemporaryFile('w+')
        sourceEncoding = 'windows-1252'
        targetEncoding = "utf-8"   
        
        fileobj.write((base64.decodestring(this.data)))   
        fileobj.seek(0)                                    
        reader = csv.DictReader(fileobj, quotechar=str(quotechar), delimiter=str(delimiter))         

        education_level = self.pool.get('hr.employee.education.level')
        move_id=''
        all_move_ids=[]
        for row  in reader :  
            education_levele_val={
                            'name':row['name'],
                            'code':str(row['code']),
                            'sequence':str(row['code'])
                            }
            
            education_level.create(cr, uid, education_levele_val,context=context)
          
            
         
        
        return True    
            
import_csv()

