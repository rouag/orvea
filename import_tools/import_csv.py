# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------
#
#    Copyright (C) 2014  .
#    Coded by: Borni DHIFI  (dhifi.borni@gmail.com)
#
#----------------------------------------------------------------------------
# encoding=utf8  
import sys  

reload(sys)  
sys.setdefaultencoding('utf8')
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
        terminated_type = self.pool.get('hr.termination.type')
        move_id=''
        all_move_ids=[]
        for row  in reader :  
            terminated_type_val={
                                'name':str(row['name']),
                                'code':str(row['code']),
                                }
            
            terminated_type.create(cr, uid, terminated_type_val,context=context)
              
           
        
    
            
        
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
            country_id=country.search(cr, uid, [('code_nat', '=',countryname)])[0]
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
    
    def import_salary_grid(self, cr, uid, ids, context=None):
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
    
    def import_diplome(self, cr, uid, ids, context=None):
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
        diplome = self.pool.get('hr.employee.diploma')
        move_id=''
        all_move_ids=[]
        for row  in reader : 
            if row['name']: 
                diplome.search(cr, uid, [('code', '=',row['code'])])
                if len(diplome.search(cr, uid, [('code', '=',row['code'])]))==0:
                    diplome_val={
                            'name':(row['name']).decode('utf-8').strip(),
                            'code':(row['code']).decode('utf-8').strip(),
                            }
          
                    diplome.create(cr, uid, diplome_val,context=context)
         
                
            
            
         
        
        return True
    
    def import_grade(self, cr, uid, ids, context=None):
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
        grade = self.pool.get('salary.grid.grade')
        move_id=''
        all_move_ids=[]
        for row  in reader : 
            if row['name']: 
                grade.search(cr, uid, [('code', '=',row['code'])])
                if len(grade.search(cr, uid, [('code', '=',row['code'])]))==0:
                    grade_val={
                            'name':(row['name']).decode('utf-8').strip(),
                            'code':(row['code']).decode('utf-8').strip(),
                            }
                    grade.create(cr, uid, grade_val,context=context)
                    
                    
    def import_type(self, cr, uid, ids, context=None):
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
        type = self.pool.get('salary.grid.type')
        move_id=''
        all_move_ids=[]
        for row  in reader : 
            if row['name']: 
                type.search(cr, uid, [('code', '=',row['code'])])
                if len(type.search(cr, uid, [('code', '=',row['code'])]))==0:
                    type_val={
                            'name':(row['name']).decode('utf-8').strip(),
                            'code':(row['code']).decode('utf-8').strip(),
                            }
          
                    type.create(cr, uid, type_val,context=context)
         
                
            
            
         
        
        return True
    
    
    def import_employee(self, cr, uid, ids, context=None):
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
        employee = self.pool.get('hr.employee')
        city=self.pool.get('res.city')
        city_side=self.pool.get('res.city')
        country = self.pool.get('res.country')
        religion=self.pool.get('religion.religion')
        education_level = self.pool.get('hr.employee.education.level')
        salary_grid_level = self.pool.get('salary.grid.degree')
        grade = self.pool.get('salary.grid.grade')
        diplome = self.pool.get('hr.employee.diploma')
        departement = self.pool.get('hr.department')
        type = self.pool.get('salary.grid.type')
        education_level_id=False
        grade_id=False
        diplome_id=False
        city_id=False
        id_recuiter = self.pool.get('recruiter.recruiter').search(cr, uid, [('name', '=','حكومي')])[0]
        country_id=False
        city_side = self.pool.get('city.side')
        insurance= self.pool.get('hr.insurance.type')  
        job_education_level= self.pool.get('hr.employee.job.education.level')
        move_id=''
        all_move_ids=[]
        for row  in reader : 
            if row['EMP_NO']: 
                if str(row['SEX_NO'])=='1':
                    sexe='male'
                else:
                    sexe='female'
                
                if str(row['MARITAL_STATUS'])=='00':
                    marital='other'
                if str(row['MARITAL_STATUS'])=='01':
                    marital='married'
                if str(row['MARITAL_STATUS'])=='02':
                    marital='single'
                if str(row['MARITAL_STATUS'])=='03':
                    marital='divorced'
                if str(row['MARITAL_STATUS'])=='4':
                    marital='mariie'
                if str(row['MARITAL_STATUS'])=='05':
                    marital='not_mariee'
                
                    
                    
                if str(row['BIRTH_PLACE']):
                    city_ids=city.search(cr, uid, [('code', '=',row['BIRTH_PLACE'])])
                    if city_ids:
                        city_name=city.browse(cr, uid, city_ids[0]).name
                if str(row['RELIGION_NO']):
                    religion_id=religion.search(cr, uid, [('code', '=',row['RELIGION_NO'])])[0]
                if str(row['NATIONALITY_NO']):
                    if str(row['NATIONALITY_NO'])=='0001':
                        country_id=country.search(cr, uid, [('code', '=','SA')])[0]
                    else:
                        country_ids=country.search(cr, uid, [('code', '=',row['NATIONALITY_NO'])])
                        if country_ids:
                            country_id=country_ids[0]
                    
                if str(row['DEGREE_NO']):
                    education_level_ids=education_level.search(cr, uid, [('code', '=',row['DEGREE_NO'])])
                    if education_level_ids:
                        education_level_id=education_level_ids[0]
                    
                    
                if str(row['EMP_STATUS_NO'])=='A' or  str(row['EMP_STATUS_NO'])=='AU':
                    state_employee='working'
                elif  str(row['EMP_STATUS_NO'])=='N' or  str(row['EMP_STATUS_NO'])=='OH':
                    state_employee='suspended'
                elif  str(row['EMP_STATUS_NO'])=='r' or  str(row['EMP_STATUS_NO'])=='T':
                    state_employee='terminated'
                    
                
                if str(row['CLASS_NO']):
                    print 'CLASS_NO',row['CLASS_NO']
                    salary_grid_level_id = salary_grid_level.search(cr, uid, [('code', '=',row['CLASS_NO'])])[0]
                    print 'salary_grid_level_id',salary_grid_level_id
                    
                if str(row['GRADE_NO']):
                    grade_ids = grade.search(cr, uid, [('code', '=',row['GRADE_NO'])])
                    if grade_ids:
                        grade_id=grade_ids[0]
               
                if str(row['MAJOR_NO']):
                    diplome_ids = diplome.search(cr, uid, [('code', '=',row['GRADE_NO'])])
                    if diplome_ids:
                        diplome_id =diplome_ids[0]
                if str(row['PAGER_NO'])==  'عضوهيئة تحقيق':
                    is_member=True
                else:
                    is_member=False
                region_id=False
                if str(row['REGION_NO']):
                    region = city_side.search(cr, uid, [('code', '=',row['REGION_NO'])])
                    if region:
                        region_id =region[0]
                        
                if str(row['GOSI_CAT']):
                    print str(row['GOSI_CAT'])
                    insurance_obj = insurance.search(cr, uid, [('code', '=',str(row['GOSI_CAT']))])
                    print 'insurance',insurance_obj
                    if insurance_obj:
                        insurance_id =insurance_obj[0]
                type_id=False     
                if str(row['TYPE_NO']):
                    type_obj = type.search(cr, uid, [('code', '=',row['TYPE_NO'])])
                    if type_obj:
                        type_id =type_obj[0]
                departement_id = departement.search(cr, uid, [('code', '=','C001')])[0]
                vals_education={'name':'01',
                                'level_education_id':education_level_id,
                                'diploma_id':diplome_id
                                
                                }
                
                    
                id_eductaion_level=job_education_level.create(cr, uid, vals_education,context=context)
                    
                    
                    
                
                    
                print row['HIRE_DATE']
                print row['GOV_HIRE_DATE']
                rcuter_date =   row['HIRE_DATE']
                begin_work_date =  row['GOV_HIRE_DATE']
                    
                
               
                if len( employee.search(cr, uid, [('number', '=',row['EMP_NO'])]))==0:
                    employee_val={
                            'name':(row['FIRST_NAME_AR']).decode('utf-8').strip(),
                            'father_name':(row['MIDDLE_NAME1_AR']).decode('utf-8').strip(),
                            'grandfather_name':(row['MIDDLE_NAME2_AR']).decode('utf-8').strip(),
                            'family_name':(row['LAST_NAME_AR']).decode('utf-8').strip(),
                            'number':(row['EMP_NO']).decode('utf-8').strip(),
                            'mobile_phone':(row['MobileNo']).decode('utf-8').strip(),
                             'work_email':(row['Email']).decode('utf-8').strip(),
                             'gender':sexe,
                              'birthday':((row['DOB'])),
                             'place_of_birth':city_name,
                             'religion_state':religion_id,
                             'country_id':country_id,
                             'identification_id':(row['COMPUTER_NO']).decode('utf-8').strip(),
                             'marital':marital,
                             'education_level_ids':[(6,0,[id_eductaion_level])],
                             'emp_state':state_employee,
                             'degree_id':salary_grid_level_id,
                             'grade_id':grade_id,
                             'recruiter_date':rcuter_date,
                              'begin_work_date': begin_work_date,
                             'is_member':is_member,
                             'employee_state':'employee',
                             'recruiter':id_recuiter,
                             'royal_decree_number':(row['ROYAL_DECREE_NO']).decode('utf-8').strip(),
                             'royal_decree_date':(row['ROYAL_DECREE_DATE']).decode('utf-8').strip(),
                             'department_id':departement_id,
                             'dep_side':region_id,
                             'insurance_type':insurance_id,
                             'type_id':type_id,
                             
                            }
                    print employee
                    print employee_val
                    id_emp=employee.create(cr, uid, employee_val,context=context)
                    print id_emp
         
                
            
            
         
        
        return True
    
    def import_passport(self, cr, uid, ids, context=None):
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
                
        move_id=''
        all_move_ids=[]
        employee = self.pool.get('hr.employee')
        for row  in reader : 
            if str(row['ISSUE_PLACE_NO']):
                    city_ids=city.search(cr, uid, [('code', '=',row['ISSUE_PLACE_NO'])])
                    if city_ids:
                        city_name=city.browse(cr, uid, city_ids[0]).name
            employee_ids= employee.search(cr, uid, [('number', '=',str(row['EMP_NO']))])
            print 'employee_ids',str(row['EMP_NO'])
            if employee_ids:
                emplyee_obj=employee.browse(cr, uid, employee_ids[0]) 
                emplyee_obj.write( {'passport_id': str(row['DOC_NO']),'passport_date':str(row['ISSUE_DATE']),'passport_place':city_name,'passport_end_date':str(row['EXPIRY_DATE'])}, )
        
        
            
        
        return True
         
    def import_directeur_direct_for_employee(self, cr, uid, ids, context=None):
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
                
        move_id=''
        all_move_ids=[]
        employee = self.pool.get('hr.employee')
        for row  in reader : 
            employee_ids_parent= employee.search(cr, uid, [('number', '=',str(row['MGR_NO']))])
            employee_ids_file= employee.search(cr, uid, [('number', '=',str(row['EMP_NO']))])
            if employee_ids_parent:
                emplyee_obj_parent=employee.browse(cr, uid, employee_ids_parent[0])
                emplyee_obj_file=employee.browse(cr, uid, employee_ids_file[0]) 
                emplyee_obj_file.write( {'parent_id': emplyee_obj_parent.id}, )    
    
    def import_bank(self, cr, uid, ids, context=None):
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
                
        move_id=''
        all_move_ids=[]
        bank = self.pool.get('res.bank')
        for row  in reader :  
            bank_val={
                            'name':row['name'],
                            'bic':str(row['code']),
                            'active':True
                            
                            }
            
            bank.create(cr, uid, bank_val,context=context)
        
        
            
        
        return True 
    
    def import_groups_general(self, cr, uid, ids, context=None):
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
        groups = self.pool.get('hr.groupe.job')
                
        move_id=''
        all_move_ids=[]
        
        for row  in reader :  
            groups_speacilaite_val={
                            'name':row['DSCR_AR'],
                            'numero':str(row['CHI_GRP_NO']),
                            'active':True,
                            'group_type':'general'
                            
                            }
            
            groups.create(cr, uid, groups_speacilaite_val,context=context)
        
        
            
        
        return True
    
    def import_group_specifique(self, cr, uid, ids, context=None):
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
        groups = self.pool.get('hr.groupe.job')
        move_id=''
        all_move_ids=[]
        parent_id=False
        for row  in reader :  
            groups_ids=groups.search(cr, uid, [('numero', '=',str(row['PAR_GRP_NO']))])
            if groups_ids:
                parent_id=groups_ids[0]
            print 'name' ,str(row['DSCR_AR'])
            print 'code' ,str(row['CHI_GRP_NO'])
            groups_speacilaite_val={
                            'name':str(row['DSCR_AR']),
                            'numero':str(row['CHI_GRP_NO']),
                            'group_type':'spicific',
                            'parent_id':parent_id,
                            
                            }
            
            groups.create(cr, uid, groups_speacilaite_val,context=context)
        
        
            
        
        return True
    
    def import_goupe_serie(self, cr, uid, ids, context=None):
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
        groups = self.pool.get('hr.groupe.job')
        move_id=''
        all_move_ids=[]
        parent_id=False
        for row  in reader :  
            groups_ids=groups.search(cr, uid, [('numero', '=',str(row['PAR_GRP_NO']))])
            if groups_ids:
                parent_id=groups_ids[0]
            print 'name' ,str(row['DSCR_AR'])
            print 'code' ,str(row['CHI_GRP_NO'])
            groups_speacilaite_val={
                            'name':str(row['DSCR_AR']),
                            'numero':str(row['CHI_GRP_NO']),
                            'group_type':'serie',
                            'parent_id':parent_id,
                            
                            }
            
            groups.create(cr, uid, groups_speacilaite_val,context=context)
        
        
            
        
        return True
    
    def import_name_job(self, cr, uid, ids, context=None):
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
        groups = self.pool.get('hr.groupe.job')
        name_job = self.pool.get('hr.job.name')
        move_id=''
        all_move_ids=[]
        parent_id=False
        for row  in reader :  
            groups_ids=groups.search(cr, uid, [('numero', '=',str(row['PAR_GRP_NO']))])
            if groups_ids:
                parent_id=groups_ids[0]
            print 'name' ,str(row['DSCR_AR'])
            print 'code' ,str(row['CHI_GRP_NO'])
            name_job_ids= name_job.search(cr, uid, [('number', '=',str(row['CHI_GRP_NO']))])
            if not name_job_ids:
                name_jobs_serie_val={
                                'name':str(row['DSCR_AR']),
                                'number':str(row['CHI_GRP_NO']),
                                }
                
                id_jobs=name_job.create(cr, uid, name_jobs_serie_val,context=context)
                if groups_ids:
                    print 'groupssss',groups_ids[0]
                    jobgroups=groups.browse(cr,uid,groups_ids[0])
                    jobgroups.write( {'job_name_ids':[(4,id_jobs)]})
                    print 'groupfffffffssss',groups_ids[0]
           
        
    
            
        
        return True
    
    
    def compte_bank(self, cr, uid, ids, context=None):
        
      
        
      
        
         
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
        employee_obj = self.pool.get('hr.employee')
        bank_obj = self.pool.get('res.bank')
        currency_obj = self.pool.get('res.currency')
        bank_compte = self.pool.get('res.partner.bank')
         
        move_id=''
        all_move_ids=[]
        for row  in reader :  
            employee=employee_obj.search(cr, uid, [('number', '=',str(row['EMP_NO']))])
            bank=bank_obj.search(cr, uid, [('bic', '=',str(row['BANK_NO']))])
           
            bank_compte_val={
                                'acc_number':str(row['ACCNT_NO']),
                                'employee_id':employee[0] if employee else False,
                                'bank_id':bank[0] if bank else False,
                                'is_deposit': True if str(row['BANK_DEPOSIT_FLAG'])=='1' else False,
                                'account_opening_date':row['ACC_OPEN_DATE'] if  row['ACC_OPEN_DATE'] != 'NULL' else  False,
                                'currency_id':156,
                                 
                                }
            
            bank_compte.create(cr, uid, bank_compte_val,context=context)
              
           
        
    
    
            
        
        return True
    
    def import_type_termination(self, cr, uid, ids, context=None):
        
      
        
         
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
        terminated_type = self.pool.get('hr.termination.type')
        move_id=''
        all_move_ids=[]
        for row  in reader :  
            terminated_type_val={
                                'name':str(row['name']),
                                'code':str(row['code']),
                                }
            
            terminated_type.create(cr, uid, terminated_type_val,context=context)
            
import_csv()

