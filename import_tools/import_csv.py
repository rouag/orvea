# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------
#
#    
#    
#
#----------------------------------------------------------------------------
# encoding=utf8  
import sys  
from Tkconstants import BROWSE
from stdnum.exceptions import ValidationError

reload(sys)  
sys.setdefaultencoding('utf8')
import base64
from openerp.osv import osv, fields
from openerp import tools,netsvc
from tempfile import TemporaryFile
import csv
from openerp.tools.translate import _
import timeit
from datetime import datetime
from umalqurra.hijri_date import HijriDate
from umalqurra.hijri import Umalqurra
from datetime import date
from dateutil.relativedelta import relativedelta

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
   

  
    
 
    def import_loan(self, cr, uid, ids, context=None):
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
        move_id=''
        all_move_ids=[]
        umalqurra = Umalqurra()
        employee_obj = self.pool.get('hr.employee')
        bank_obj = self.pool.get('res.bank')
        loan_obj = self.pool.get('hr.loan')
        currency_obj = self.pool.get('res.currency')
        bank_compte = self.pool.get('res.partner.bank')
        type=self.pool.get('ir.model.data').get_object_reference(cr, uid, 'smart_hr', 'hr_loan_type_01')[1]
        move_id=''
        all_move_ids=[]
        for row  in reader :  
            employee=employee_obj.search(cr, uid, [('number', '=',str(row['EMP_NO']))])
            bank=bank_obj.search(cr, uid, [('bic', '=',str(row['BANK_NO']))])
            fmt = '%d/%m/%Y'
            if row['LOAN_START_DATE_HJ'] != 'NULL':
                try:
                        dt = datetime.strptime(str(row['LOAN_START_DATE_HJ']), fmt)
                        start_date = umalqurra.hijri_to_gregorian(dt.year, dt.month, dt.day)
                        date_first_tranche = date(int(start_date[0]), int(start_date[1]), int(start_date[2]))
                except:
                    
                        date_first_tranche=row['LOAN_START_DATE']
                   
                    
            if row['END_DEDUCTED_DATE_HJ'] != 'NULL':
                try:
                        dtf = datetime.strptime(str(row['END_DEDUCTED_DATE_HJ']), fmt)
                        end_date = umalqurra.hijri_to_gregorian(dtf.year, dtf.month, dtf.day)
                        date_last_tranche = date(int(end_date[0]), int(end_date[1]), int(end_date[2]))
                except:
                    
                        date_last_tranche=row['END_DEDUCTED_DATE']
                   
            if row['DOC_DATE_HJ'] != 'NULL':
                try:
                    
                        dtd = datetime.strptime(str(row['DOC_DATE_HJ']), fmt)
                        doc_date = umalqurra.hijri_to_gregorian(dtd.year, dtd.month, dtd.day)
                        date_doc = date(int(doc_date[0]), int(doc_date[1]), int(doc_date[2]))
                except:
                    
                        date_last_tranche=row['END_DEDUCTED_DATE']
                   
                   
                
            number = float(row['LOAN_AMT']) / (float(row['INSTALLMENT_AMT']) or 1.0)
            
            if str(row['LOAN_STATUS'])=='C' or str(row['LOAN_STATUS'])=='1' :
                state='done'
            else:
                state='progress'
                
                
            print date_doc,date_last_tranche,date_first_tranche
            if bank and not loan_obj.search(cr, uid, [('name', '=',str(row['LOAN_VOUCHER_NO']))]):
           
                    loan_val={
                                'name':str(row['LOAN_VOUCHER_NO']),
                                'employee_id':employee[0] if employee else False,
                                'bank_id':bank[0] if bank else False,
                                'loan_type_id':type,
                                'date_from':date_first_tranche,
                                'date_to':date_last_tranche,
                                'amount':float(row['LOAN_AMT']),
                                'monthly_amount':float(row['INSTALLMENT_AMT']),
                                'date_decision':date_doc,
                                'number_decision':row['DOC_NO'],
                                'date': row['TIME_STAMP'],
                                'installment_number':number,
                                'state':state,
                                 
                                }
          
                    loan_obj.create(cr, uid, loan_val,context=context)
                    
                    
                 
               
                
        
        
        
        
        return True 
    
    def import_loan_ligne(self, cr, uid, ids, context=None):
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
        move_id=''
        all_move_ids=[]
        umalqurra = Umalqurra()
        employee_obj = self.pool.get('hr.employee')
        loan_line_obj = self.pool.get('hr.loan.line')
        loan_obj = self.pool.get('hr.loan')
        employee_id = employee_obj.search(cr, uid, [('number', '=','01618')])
        fmt = '%d/%m/%Y'
        move_id=''
        all_move_ids=[]
        
        loan_ids=loan_obj.search(cr, uid,  [('state', '=','progress'),('employee_id', '=',employee_id[0])])
        date_now= datetime.now()
        print len(loan_ids)
        i=0
        l=0
       
        for lon_id  in loan_ids : 
                loan= loan_obj.browse(cr, uid, lon_id)
                if loan.state=="progress":
                    i=0
                    for line_number in range (loan.installment_number):
                        
                        date1=datetime.strptime(loan.date_from,"%Y-%m-%d")
                      
                        line_month=date1+ relativedelta(months=date1.month+i)
                       
                        line_months=line_month.strftime('%Y-%m-%d')
                        um = HijriDate()
                        dates = str(line_months).split('-')
                        
                        um.set_date_from_gr(int(dates[0]), int(dates[1]), int(dates[2]))
                        i=i+1
                        if line_month<datetime.now()   :
                            state='done'
                        else:
                             state='progress'
                             
                       
                        print i
                        month_val = {   'loan_id': loan.id,
                                         'amount': loan.monthly_amount,
                                         'month': str(int(um.month)).zfill(2),
                                         'state':state,
                                         'date':line_month,
                                 }
                        
                        loan_line_obj.create(cr, uid, month_val,context=context)
                         
                     
                         
                     
                     
               
                    
                   
                
          
               
                
        
        
        
        
        return True 
  
    def import_echelle_salaire(self, cr, uid, ids, context=None):
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
        move_id=''
        all_move_ids=[]
       
        hr_job=self.pool.get('hr.job')
        type = self.pool.get('salary.grid.type')
        salary_grid_degree = self.pool.get('salary.grid.degree')
        grade = self.pool.get('salary.grid.grade')
        job_group=self.pool.get('hr.groupe.job')
        slary_grid=self.pool.get('salary.grid')
        slary_grid_detail=self.pool.get('salary.grid.detail')
        hr_allowance_type=self.pool.get('hr.allowance.type')
        hr_allowance__detaile=self.pool.get('salary.grid.detail.allowance')
        serie_id=False
        job_name_id=False
        general_id=False
        salary_grid_degree_id=False
        i=0
        hr_allowance_type_id=hr_allowance_type.search(cr, uid, [('code', '=','01')])
        i=1
        for row  in reader : 
            if str(row['CLASS_NO']):
                    salary_grid_degree_ids = salary_grid_degree.search(cr, uid, [('code', '=',row['CLASS_NO'])])
                    if salary_grid_degree_ids:
                        salary_grid_degree_id=salary_grid_degree_ids[0]
            type_id=type.search(cr, uid,  [('code', '=',str(row['BAND_NO']))])
            grade_id =grade.search(cr, uid,  [('code', '=',str(row['GRADE_NO']))])
            type_obj=type.browse(cr, uid, type_id[0])
            i=i+1
            slary_grid_ids=slary_grid.search(cr, uid, [('name', '=',type_obj.name)])
            if not  slary_grid_ids:
                echelle_val = {
                        'name':type_obj.name,
                       'code':str(i),
                        'date': datetime.now(),
                       'enabled':True ,
                       'state':'done'
                       
                       }
                slary_grid_id=slary_grid.create(cr, uid, echelle_val,context=context)
            else:
                slary_grid_id=slary_grid_ids[0]
            if  grade_id and salary_grid_degree_id and type_id :
                slary_grid_detail_is=slary_grid_detail.search(cr, uid, [('type_id', '=',type_id[0]),('grade_id', '=',grade_id[0]),('degree_id', '=',salary_grid_degree_id)])
                slary_grid_ids=slary_grid.search(cr, uid, [('name', '=',type_obj.name)])
                if not slary_grid_detail_is:
                    if type_obj=="003":
    
                        echelle_val_detail = {
                                       
                           'grid_id': slary_grid_id or slary_grid_id[0] ,
                           'type_id': type_id[0] if type_id else False ,
                           'grade_id': grade_id[0]if grade_id else False ,
                           'degree_id':salary_grid_degree_id,
                           'basic_salary':row['BASIC_SAL'],
                           'net_salary':row['BASIC_SAL'],
                           'retirement':10,
                           }
                    else:
                         echelle_val_detail = {
                                       
                           'grid_id': slary_grid_id or slary_grid_id[0] ,
                           'type_id': type_id[0] if type_id else False ,
                           'grade_id': grade_id[0]if grade_id else False ,
                           'degree_id':salary_grid_degree_id,
                           'basic_salary':row['BASIC_SAL'],
                           'net_salary':row['BASIC_SAL'],
                           'retirement':9,
                           }
                        
                       
                    hr_allowance__detaile_id=slary_grid_detail.create(cr, uid, echelle_val_detail,context=context)
                    aallance_val = {
                                       
                           'allowance_id':23,
                           'compute_method':'amount' ,
                           'amount':float(row['TRANSPORTATION']) if row['TRANSPORTATION'] != 'NULL' else False,
                           
                           }
                    hr_allowance_bonus_detaile_id=hr_allowance__detaile.create(cr, uid, aallance_val,context=context)
                    slary_grid_detailobj=slary_grid_detail.browse(cr, uid, hr_allowance__detaile_id)
                    slary_grid_detailobj.write({'allowance_ids':[(6,0,[hr_allowance_bonus_detaile_id])],})
                        
                    
                 
               
                
        
        
        
        
        return True 
    
    def import_echelle_salaire_bonus(self, cr, uid, ids, context=None):
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
        move_id=''
        all_move_ids=[]
       
        hr_job=self.pool.get('hr.job')
        type = self.pool.get('salary.grid.type')
        salary_grid_degree = self.pool.get('salary.grid.degree')
        grade = self.pool.get('salary.grid.grade')
        job_group=self.pool.get('hr.groupe.job')
        slary_grid=self.pool.get('salary.grid')
        slary_grid_detail=self.pool.get('salary.grid.detail')
        hr_allowance_types=self.pool.get('hr.allowance.type')
        hr_allowance__detaile=self.pool.get('salary.grid.detail.allowance')
        serie_id=False
        job_name_id=False
        general_id=False
        salary_grid_degree_id=False
        i=0
        hr_allowance_type_ids=hr_allowance_types.search(cr, uid, [('code', '=','01')])
        i=1
        for row  in reader : 
            if str(row['CLASS_NO']):
                    salary_grid_degree_ids = salary_grid_degree.search(cr, uid, [('code', '=',row['CLASS_NO'])])
                    if salary_grid_degree_ids:
                        salary_grid_degree_id=salary_grid_degree_ids[0]
            type_id=type.search(cr, uid,  [('code', '=',str(row['BAND_NO']))])
            grade_id =grade.search(cr, uid,  [('code', '=',str(row['GRADE_NO']))])
            if  grade_id and salary_grid_degree_id and type_id :
                  
                slary_grid_detail_is=slary_grid_detail.search(cr, uid, [('type_id', '=',type_id[0]),('grade_id', '=',grade_id[0]),('degree_id', '=',salary_grid_degree_id)])
                print 'slary_grid_detail',slary_grid_detail_is
                slary_grid_detailobj=slary_grid_detail.browse(cr, uid, slary_grid_detail_is[0])
                print 'slary_grid_detail',hr_allowance_type_ids[0]
                aallance_val = {
                                       
                           'allowance_id':23,
                           'compute_method':'amount' ,
                           'amount':float(row['TRANSPORTATION']) if row['TRANSPORTATION'] != 'NULL' else False,
                           
                           }
                hr_allowance__detaile_id=hr_allowance__detaile.create(cr, uid, aallance_val,context=context)
                print 'hr_allowance__detaile_id',hr_allowance__detaile_id
                print 'slary_grid_detailobj',slary_grid_detailobj
                slary_grid_detailobj.write({'allowance_ids':[(6,0,[hr_allowance__detaile_id])],})
                
    def import_employee_echelle(self, cr, uid, ids, context=None):
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
        move_id=''
        all_move_ids=[]
       
        hr_job=self.pool.get('hr.job')
        type = self.pool.get('salary.grid.type')
        salary_grid_degree = self.pool.get('salary.grid.degree')
        grade = self.pool.get('salary.grid.grade')
        job_group=self.pool.get('hr.groupe.job')
        slary_grid=self.pool.get('salary.grid')
        slary_grid_detail=self.pool.get('salary.grid.detail')
        hr_allowance_types=self.pool.get('hr.allowance.type')
        hr_allowance__detaile=self.pool.get('salary.grid.detail.allowance')
        employee = self.pool.get('hr.employee')
        insurance= self.pool.get('hr.insurance.type') 
        serie_id=False
        job_name_id=False
        general_id=False
        salary_grid_degree_id=False
        i=0
        hr_allowance_type_ids=hr_allowance_types.search(cr, uid, [('code', '=','01')])
        i=1
        for row  in reader : 
            if str(row['CLASS_NO']):
                    salary_grid_degree_ids = salary_grid_degree.search(cr, uid, [('code', '=',row['CLASS_NO'])])
                    if salary_grid_degree_ids:
                        salary_grid_degree_id=salary_grid_degree_ids[0]
            type_id=type.search(cr, uid,  [('code', '=',str(row['BAND_NO']))])
            grade_id =grade.search(cr, uid,  [('code', '=',str(row['GRADE_NO']))])
            if  grade_id and salary_grid_degree_id and type_id :
                slary_grid_detail_is=slary_grid_detail.search(cr, uid, [('type_id', '=',type_id[0]),('grade_id', '=',grade_id[0]),('degree_id', '=',salary_grid_degree_id)])
                if slary_grid_detail_is:
                    slary_grid_detailobj=slary_grid_detail.browse(cr, uid, slary_grid_detail_is[0])
                    employee_id = employee.search(cr, uid, [('number', '=',str(row['EMP_NO']))])
                    val={'salary_grid_id':slary_grid_detail_is[0]}
                    employee.write(cr, uid,employee_id, val,context=context)
                    if str(row['GOSI_CAT']):
                            insurance_obj = insurance.search(cr, uid, [('code', '=',str(row['GOSI_CAT']))])
                            if insurance_obj:
                                if str(row['GOSI_CAT'])=='C':
                                    slary_grid_detailobj.write({'insurance_type':insurance_obj[0],'retirement':9})
                                else:
                                    slary_grid_detailobj.write({'insurance_type':insurance_obj[0],'retirement':10})
                            
                    
                        
                    
                 
               
                
        
        
        
        
        return True 
    
        
        
    def import_bonus(self, cr, uid, ids, context=None):
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
        move_id=''
        all_move_ids=[]
        departement = self.pool.get('hr.department')
        hr_bonus=self.pool.get('hr.bonus')
        hr_job_allowance=self.pool.get('hr.allowance.type')
        hr_indemnity_type=self.pool.get('hr.indemnity.type')
        type_1_id=False
        type_2_id=False
        type_3_id=False
        
        for row  in reader : 
            type_1_id=False
            type_2_id=False
            type_3_id=False
            type=(row['AWARD_TYPE_ID'])
            if type =="1":
                type_bonus='reward'
                type_1_id=self.pool.get('ir.model.data').get_object_reference(cr, uid, 'smart_hr', 'hr_reward_type_03')[1]
            elif type=="2":
                type_bonus='reward'
                type_1_id=self.pool.get('ir.model.data').get_object_reference(cr, uid, 'smart_hr', 'hr_reward_type_05')[1]
            elif type=="3":
                type_bonus='reward'
                type_1_id=self.pool.get('ir.model.data').get_object_reference(cr, uid, 'smart_hr', 'hr_reward_type_06')[1]
            elif type=="4":
                type_bonus='reward'
                type_1_id=self.pool.get('ir.model.data').get_object_reference(cr, uid, 'smart_hr', 'hr_reward_type_07')[1]
            elif type=="5":
                type_bonus='reward'
                type_1_id=self.pool.get('ir.model.data').get_object_reference(cr, uid, 'smart_hr', 'hr_reward_type_08')[1]
            elif type=="6":
                type_bonus='reward'
                type_1_id=self.pool.get('ir.model.data').get_object_reference(cr, uid, 'smart_hr', 'hr_reward_type_02')[1]
            elif type=="7":
                type_bonus='reward'
                type_1_id=self.pool.get('ir.model.data').get_object_reference(cr, uid, 'smart_hr', 'hr_reward_type_09')[1]
            elif type=="8":
                type_bonus='reward'
                type_1_id=self.pool.get('ir.model.data').get_object_reference(cr, uid, 'smart_hr', 'hr_reward_type_01')[1]
            elif type=="9":
                type_bonus='reward'
                type_1_id=self.pool.get('ir.model.data').get_object_reference(cr, uid, 'smart_hr', 'hr_reward_type_10')[1]
            elif type=="10":
                type_bonus='reward'
                type_1_id=self.pool.get('ir.model.data').get_object_reference(cr, uid, 'smart_hr', 'hr_reward_type_11')[1]
            elif type=="11":
                type_bonus='reward'
                type_1_id=self.pool.get('ir.model.data').get_object_reference(cr, uid, 'smart_hr', 'hr_reward_type_12')[1]
            elif type=="12":
                type_bonus='reward'
                type_1_id=self.pool.get('ir.model.data').get_object_reference(cr, uid, 'smart_hr', 'hr_reward_type_13')[1]
            elif type=="13":
                type_bonus='reward'
                type_1_id=self.pool.get('ir.model.data').get_object_reference(cr, uid, 'smart_hr', 'hr_reward_type_15')[1]
            elif type=="14":
                type_bonus='indemnity'
                type_2_id=self.pool.get('ir.model.data').get_object_reference(cr, uid, 'smart_hr', 'hr_indemnity_type_01')[1]
            elif type=="15":
                type_bonus='indemnity'
                type_2_id=self.pool.get('ir.model.data').get_object_reference(cr, uid, 'smart_hr', 'hr_indemnity_type_02')[1]
            elif type=="16":
                type_bonus='indemnity'
                type_2_id=self.pool.get('ir.model.data').get_object_reference(cr, uid, 'smart_hr', 'hr_indemnity_type_03')[1]
            elif type=="17":
                type_bonus='allowance'
                type_3_id=self.pool.get('ir.model.data').get_object_reference(cr, uid, 'smart_hr', 'hr_allowance_type_03')[1]
            elif type=="18":
                type_bonus='allowance'
                type_3_id=self.pool.get('ir.model.data').get_object_reference(cr, uid, 'smart_hr', 'hr_allowance_type_06')[1]
            elif type=="19":
                type_bonus='allowance'
                type_3_id=self.pool.get('ir.model.data').get_object_reference(cr, uid, 'smart_hr', 'hr_allowance_type_11')[1]
            elif type=="20":
                type_bonus='allowance'
                type_3_id=self.pool.get('ir.model.data').get_object_reference(cr, uid, 'smart_hr', 'hr_allowance_type_12')[1]
            elif type=="21":
                type_bonus='allowance'
                type_3_id=self.pool.get('ir.model.data').get_object_reference(cr, uid, 'smart_hr', 'hr_allowance_type_03')[1]
                
            fmt = '%d/%m/%Y'
            
            month= str(row['DOC_DATE'])[5:7] 
            hr_bonus_val = {
                       'name': str(row['PAY_SEQNO']),
                       'number_decision':  str(row['DOC_NO']),
                       'date_decision':  str(row['DOC_DATE']),
                       'date': str(row['AWARD_DATE']),
                       'month_from':month,
                       'month_to':month,
                       'reward_id':type_1_id,
                       'indemnity_id':type_2_id,
                       'allowance_id':type_3_id,
                       'type':type_bonus,
                       'deccription':str(row['REMARKS']),
                       'compute_method':'amount',
                       'state':'done',
            
                       }
            hr_bonus.create(cr, uid, hr_bonus_val,context=context)
        
        return True  
   

    def import_bonus_employee(self, cr, uid, ids, context=None):
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
        move_id=''
        all_move_ids=[]
        departement = self.pool.get('hr.department')
        hr_job=self.pool.get('hr.job')
        type = self.pool.get('salary.grid.type')
        grade = self.pool.get('salary.grid.grade')
        job_name = self.pool.get('hr.job.name')
        job_group=self.pool.get('hr.groupe.job')
        serie_id=False
        job_name_id=False
        genral_id=False
        i=0
        hr_bonus=self.pool.get('hr.bonus')
        hr_bonus_line = self.pool.get('hr.bonus.line')
        employee = self.pool.get('hr.employee')
        for row  in reader : 
            hr_bonus_id=hr_bonus.search(cr, uid,  [('name', '=',str(row['PAY_SEQNO']))])
            employee_id= employee.search(cr, uid, [('number', '=',str(row['EMP_NO']))])
            if employee_id and hr_bonus_id:
                hr_bonus_obj=hr_bonus.browse(cr, uid, hr_bonus_id[0])
                employee_obj=employee.browse(cr, uid, employee_id[0])
                hr_bonus_line_val = {
                       'name':hr_bonus_obj.deccription+employee_obj.name,
                       'employee_id': employee_id[0] ,
                       'bonus_id':hr_bonus_id[0],
                       'amount':row['ACTUAL_AMT'],
                       'compute_method':'amount',
                       'state':'expired',
                       'month_from':hr_bonus_obj.month_from,
                       'month_to':hr_bonus_obj.month_to,
                       'reward_id':hr_bonus_obj.reward_id.id if hr_bonus_obj.reward_id else False ,
                       'indemnity_id':hr_bonus_obj.indemnity_id.id if hr_bonus_obj.indemnity_id else False ,
                       'allowance_id':hr_bonus_obj.allowance_id.id if hr_bonus_obj.allowance_id else False ,
                       'type':hr_bonus_obj.type,
                       }
                   
                hr_bonus_line.create(cr, uid, hr_bonus_line_val,context=context)
                hr_bonus_obj.write({'amount':row['ACTUAL_AMT'], })
            
                    
                 
               
                
        
        
        
        
        return True 
        
        

   
   
      
   
        

           
    def import_job(self, cr, uid, ids, context=None):
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
        move_id=''
        all_move_ids=[]
        departement = self.pool.get('hr.department')
        hr_job=self.pool.get('hr.job')
        type = self.pool.get('salary.grid.type')
        grade = self.pool.get('salary.grid.grade')
        job_name = self.pool.get('hr.job.name')
        job_group=self.pool.get('hr.groupe.job')
        serie_id=False
        job_name_id=False
        general_id=False
        i=0
        
        for row  in reader : 
            type_id=type.search(cr, uid,  [('code', '=',str(row['BAND_NO']))])
            grade_id =grade.search(cr, uid,  [('code', '=',str(row['GRADE_NO']))])
            departement_id = departement.search(cr, uid, [('code', '=',str(row['BRANCH_NO']))])
            job_name_id = job_name.search(cr, uid, [('number', '=',str(row['POSITION_CODE']))])
            if job_name_id:
                serie_id= job_group.search(cr, uid, [('job_name_ids', 'in',job_name_id)])
            if serie_id:
                specifique_id=job_group.search(cr, uid, [('child_ids', 'in',serie_id)])
            if specifique_id:
                genral_id=job_group.search(cr, uid, [('child_ids', 'in',specifique_id)])
            if specifique_id and genral_id and serie_id and job_name_id and type_id :
                
                    job_val = {
                       'number': str(row['POSITION_NO']),
                       'name': job_name_id[0] ,
                       'type_id': type_id[0] if type_id else False ,
                       'grade_id': grade_id[0]if grade_id else False ,
                       'department_id': departement_id[0]if departement_id else False ,
                       'general_id': genral_id[0] if genral_id else False,
                       'specific_id': specifique_id[0]if specifique_id else False,
                       'serie_id': serie_id[0]if serie_id else False,
                       'state':'unoccupied',
                       }
                   
                    
                 
               
                
        
        
        
        
        return True 
        
        
         
    
    def import_job_employee(self, cr, uid, ids, context=None):
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
        move_id=''
        all_move_ids=[]
        job = self.pool.get('hr.job')
        employee = self.pool.get('hr.employee')
        for row  in reader : 
            job_id=job.search(cr, uid,  [('number', '=',str(row['POSITION_NO']))])
            employee_id= employee.search(cr, uid, [('number', '=',str(row['EMP_NO']))])
            if job_id and employee_id :
                jobs=job.browse(cr, uid, job_id[0]) 
                jobs.write({'employee':employee_id[0], 'state':'occupied',})
        
        return True  

    def fix_employee_department(self, cr, uid, ids, context=None):
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
        move_id=''
        all_move_ids=[]
        departement = self.pool.get('hr.department')
        employee = self.pool.get('hr.employee')
        for row  in reader :
            if row['EMP_NO'] != 'NULL'  and row['LOC_ID'] != 'NULL' :
                employee_id = employee.search(cr, uid, [('number', '=',str(row['EMP_NO']))])
                department_id = departement.search(cr, uid, [('code', '=',str(row['LOC_ID']))])
                val={'department_id':department_id[0] if department_id else False}
                employee.write(cr, uid,employee_id, val,context=context)
        return True
    
          
    def import_branche(self, cr, uid, ids, context=None):
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
        move_id=''
        all_move_ids=[]
        departement = self.pool.get('hr.department')
        employee = self.pool.get('hr.employee')
        for row  in reader :

            daprtment_val={
                            'name':str(row['SHORT_NAME']),
                            'code':str(row['LOC_ID']),
                            }

            departement.create(cr, uid, daprtment_val,context=context)
        return True

    def import_branche_parent(self, cr, uid, ids, context=None):
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
        move_id=''
        all_move_ids=[]
        departement = self.pool.get('hr.department')
        employee = self.pool.get('hr.employee')
        for row in reader:
            if len(str(row['MGR_NO'].strip(" ")))==4:
                empid = str(0)+str(row['MGR_NO'].strip(" "))
            elif len(str(row['MGR_NO'].strip(" ")))==3:
                empid = str(0)+str(0)+str(row['MGR_NO'].strip(" "))
            elif len(str(row['MGR_NO'].strip(" ")))==2:
                empid = str(0)+str(0)+str(0)+str(row['MGR_NO'].strip(" "))
            elif len(str(row['MGR_NO'].strip(" ")))==1:
                empid = str(0)+str(0)+str(0)+str(0)+str(row['MGR_NO'].strip(" "))
            else:
                empid = str(row['MGR_NO'].strip(" "))
            emp_id = employee.search(cr, uid, [('number', '=',empid)])
            exist_dep = departement.search(cr, uid, [('code','=',str(row['LOC_ID']))],context=context)
            print exist_dep
            print 'emp_id',emp_id
            if exist_dep:
                parent = departement.search(cr, uid, [('code','=',str(row['LOC_Parent_ID']))],context=context)
                print parent
                departement.browse(cr, uid, exist_dep[0], context=context).write({'parent_id':parent[0] if parent else False})
                print str(row['LOC_ID'])
        return True
    
    
    def import_branche_manager(self, cr, uid, ids, context=None):
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
        move_id=''
        all_move_ids=[]
        departement = self.pool.get('hr.department')
        employee = self.pool.get('hr.employee')
        for row in reader:
            if len(str(row['MGR_NO'].strip(" ")))==4:
                manager = str(0)+str(row['MGR_NO'].strip(" "))
            elif len(str(row['MGR_NO'].strip(" ")))==3:
                manager = str(0)+str(0)+str(row['MGR_NO'].strip(" "))
            elif len(str(row['MGR_NO'].strip(" ")))==2:
                manager = str(0)+str(0)+str(0)+str(row['MGR_NO'].strip(" "))
            elif len(str(row['MGR_NO'].strip(" ")))==1:
                manager = str(0)+str(0)+str(0)+str(0)+str(row['MGR_NO'].strip(" "))
            else:
                manager = str(row['MGR_NO'].strip(" "))
            manager_id = employee.search(cr, uid, [('number', '=',manager)])
            exist_dep = departement.search(cr, uid, [('code','=',str(row['LOC_ID']))],context=context)
            if exist_dep and manager_id:
                departement.browse(cr, uid, exist_dep[0], context=context).write({'manager_id': manager_id[0] if manager_id else False})
                print row['LOC_ID']
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
            if employee_ids:
                emplyee_obj=employee.browse(cr, uid, employee_ids[0]) 
                passport_end_date  = row['EXPIRY_DATE']
                passport_date  = row['ISSUE_DATE']
                if passport_end_date == 'NULL':
                    passport_end_date = False
                if passport_date == 'NULL':
                    passport_date = False                    
                emplyee_obj.write( {'passport_id': str(row['DOC_NO']),'passport_date':passport_date,'passport_place':city_name,
                                    'passport_end_date':passport_end_date}, )
        
        
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
                            'code':'SA',
                            'name':row['name'],
                            'code_nat':code,
                            'national':row['NATION_DSCR_AR'],
                            }
            
                country.create(cr, uid, country_line_val,context=context)
            else:
                country_line_val={
                            'name':row['name'],
                            'code_nat':code,
                            'nation':row['NATION_DSCR_AR'],
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
            print country_id
            city_line_val={
                            'name':row['name'],
                            'code':str(row['code']),
                            'contry':country_id[0]
                            }
            
            city.create(cr, uid, city_line_val,context=context)
          
            
         
        
        return True


    def import_city(self, cr, uid, ids, context=None):
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
    
    def import_degree(self, cr, uid, ids, context=None):
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
    
    def import_specialiter(self, cr, uid, ids, context=None):
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
        diplome = self.pool.get('hr.employee.specialization')
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
    
    
    def import_import_employee(self, cr, uid, ids, context=None):
           
        start = timeit.default_timer()
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
        diplome = self.pool.get('')
        departement = self.pool.get('hr.department')
        type = self.pool.get('salary.grid.type')
        education_level_id=False
        grade_id=False
        diplome_id=False
        city_id=False
        religion_id=False
        salary_grid_level_id=False
        id_recuiter = self.pool.get('recruiter.recruiter').search(cr, uid, [('name', '=','حكومي')])[0]
        country_id=False
        city_side = self.pool.get('city.side')
        insurance= self.pool.get('hr.insurance.type')  
        job_education_level= self.pool.get('hr.employee.job.education.level')
        move_id=''
        all_move_ids=[]
        city_name=False
        for row  in reader : 
            if row['EMP_NO'] and not ( employee.search(cr, uid, [('number', '=',row['EMP_NO'])])): 
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
                    religion_ids=religion.search(cr, uid, [('code', '=',row['RELIGION_NO'])])
                    if religion_ids:
                        religion_id=religion_ids[0]
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
                    salary_grid_level_ids = salary_grid_level.search(cr, uid, [('code', '=',row['CLASS_NO'])])
                    if salary_grid_level_ids:
                        salary_grid_level_id=salary_grid_level_ids[0]
                    
                if str(row['GRADE_NO']):
                    grade_ids = grade.search(cr, uid, [('code', '=',row['GRADE_NO'])])
                    if grade_ids:
                        grade_id=grade_ids[0]
               
                if str(row['MAJOR_NO']):
                    diplome_ids = diplome.search(cr, uid, [('code', '=',row['MAJOR_NO'])])
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
                   
                    insurance_obj = insurance.search(cr, uid, [('code', '=',str(row['GOSI_CAT']))])
                   
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
                    
                    
                    
                
                    
               
                rcuter_date =   row['HIRE_DATE']
                begin_work_date =  row['GOV_HIRE_DATE']
                    
                
               
                
                employee_val={
                            'name':(row['FIRST_NAME_AR']).decode('utf-8').strip()if (row['FIRST_NAME_AR']).decode('utf-8').strip()!='NULL' else 'لا إسم' ,
                            'father_name':(row['MIDDLE_NAME1_AR']).decode('utf-8').strip() if (row['MIDDLE_NAME1_AR']).decode('utf-8').strip()!='NULL' else 'لا إسم',
                            'grandfather_name':(row['MIDDLE_NAME2_AR']).decode('utf-8').strip() if (row['MIDDLE_NAME2_AR']).decode('utf-8').strip()!='NULL' else 'لا إسم',
                            'family_name':(row['LAST_NAME_AR']).decode('utf-8').strip()if (row['LAST_NAME_AR']).decode('utf-8').strip()!='NULL' else 'لا إسم',
                            'number':(row['EMP_NO']).decode('utf-8').strip(),
                            'mobile_phone':(row['MobileNo']).decode('utf-8').strip(),
                             'work_email':(row['Email']).decode('utf-8').strip(),
                             'gender':sexe,
                              'birthday':((row['DOB']))if  row['DOB'] != 'NULL' else  datetime.now(),
                             'place_of_birth':city_name,
                             'religion_state':religion_id,
                             'country_id':country_id,
                             'identification_id':(row['COMPUTER_NO']).decode('utf-8').strip(),
                             'marital':marital,
                             'education_level_ids':[(6,0,[id_eductaion_level])],
                             'emp_state':state_employee,
                             'degree_id':salary_grid_level_id,
                             'grade_id':grade_id,
                             'recruiter_date':row['HIRE_DATE']if  row['HIRE_DATE'] != 'NULL' else datetime.now(),
                              'begin_work_date':  row['GOV_HIRE_DATE'] if  row['GOV_HIRE_DATE'] != 'NULL' else datetime.now(),
                             'is_member':is_member,
                             'employee_state':'employee',
                             'recruiter':id_recuiter,
                             'royal_decree_number':(row['ROYAL_DECREE_NO']).decode('utf-8').strip(),
                             'royal_decree_date':(row['ROYAL_DECREE_DATE']).decode('utf-8').strip()if  row['ROYAL_DECREE_DATE'] != 'NULL' else  datetime.now(),
                             'department_id':departement_id,
                             'dep_side':region_id,
                             'insurance_type':insurance_id,
                             'type_id':type_id,
                             
                            }
                try:
                        id_emp=employee.create(cr, uid, employee_val,context=context)
                except:
                        print 'error'
                   
         
                
            
            
         
        stop = timeit.default_timer()
        print 'time for import employee', stop - start
        return True
            
    
    def import_education_level_employee(self, cr, uid, ids, context=None):
           
        start = timeit.default_timer()
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
        religion_id=False
        salary_grid_level_id=False
        id_recuiter = self.pool.get('recruiter.recruiter').search(cr, uid, [('name', '=','حكومي')])[0]
        country_id=False
        city_side = self.pool.get('city.side')
        insurance= self.pool.get('hr.insurance.type')  
        job_education_level= self.pool.get('hr.employee.job.education.level')
        move_id=''
        all_move_ids=[]
        city_name=False
        for row  in reader : 
            if row['EMP_NO'] and not ( employee.search(cr, uid, [('number', '=',row['EMP_NO'])])): 
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
                    religion_ids=religion.search(cr, uid, [('code', '=',row['RELIGION_NO'])])
                    if religion_ids:
                        religion_id=religion_ids[0]
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
                    salary_grid_level_ids = salary_grid_level.search(cr, uid, [('code', '=',row['CLASS_NO'])])
                    if salary_grid_level_ids:
                        salary_grid_level_id=salary_grid_level_ids[0]
                    
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
                   
                    insurance_obj = insurance.search(cr, uid, [('code', '=',str(row['GOSI_CAT']))])
                   
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
                    
                    
                    
                
                    
               
                rcuter_date =   row['HIRE_DATE']
                begin_work_date =  row['GOV_HIRE_DATE']
                    
                
               
                
                employee_val={
                            'name':(row['FIRST_NAME_AR']).decode('utf-8').strip()if (row['FIRST_NAME_AR']).decode('utf-8').strip()!='NULL' else 'لا إسم' ,
                            'father_name':(row['MIDDLE_NAME1_AR']).decode('utf-8').strip() if (row['MIDDLE_NAME1_AR']).decode('utf-8').strip()!='NULL' else 'لا إسم',
                            'grandfather_name':(row['MIDDLE_NAME2_AR']).decode('utf-8').strip() if (row['MIDDLE_NAME2_AR']).decode('utf-8').strip()!='NULL' else 'لا إسم',
                            'family_name':(row['LAST_NAME_AR']).decode('utf-8').strip()if (row['LAST_NAME_AR']).decode('utf-8').strip()!='NULL' else 'لا إسم',
                            'number':(row['EMP_NO']).decode('utf-8').strip(),
                            'mobile_phone':(row['MobileNo']).decode('utf-8').strip(),
                             'work_email':(row['Email']).decode('utf-8').strip(),
                             'gender':sexe,
                              'birthday':((row['DOB']))if  row['DOB'] != 'NULL' else  datetime.now(),
                             'place_of_birth':city_name,
                             'religion_state':religion_id,
                             'country_id':country_id,
                             'identification_id':(row['COMPUTER_NO']).decode('utf-8').strip(),
                             'marital':marital,
                             'education_level_ids':[(6,0,[id_eductaion_level])],
                             'emp_state':state_employee,
                             'degree_id':salary_grid_level_id,
                             'grade_id':grade_id,
                             'recruiter_date':row['HIRE_DATE']if  row['HIRE_DATE'] != 'NULL' else datetime.now(),
                              'begin_work_date':  row['GOV_HIRE_DATE'] if  row['GOV_HIRE_DATE'] != 'NULL' else datetime.now(),
                             'is_member':is_member,
                             'employee_state':'employee',
                             'recruiter':id_recuiter,
                             'royal_decree_number':(row['ROYAL_DECREE_NO']).decode('utf-8').strip(),
                             'royal_decree_date':(row['ROYAL_DECREE_DATE']).decode('utf-8').strip()if  row['ROYAL_DECREE_DATE'] != 'NULL' else  datetime.now(),
                             'department_id':departement_id,
                             'dep_side':region_id,
                             'insurance_type':insurance_id,
                             'type_id':type_id,
                             
                            }
                try:
                        id_emp=employee.create(cr, uid, employee_val,context=context)
                except:
                        print 'error'
                   
         
                
            
            
         
        stop = timeit.default_timer()
        print 'time for import employee', stop - start
        return True
            
    
    
    #===========================================================================
    # def import_passport(self, cr, uid, ids, context=None):
    #     if context is None:
    #         context = {}
    #     this = self.browse(cr, uid, ids[0])   
    #     quotechar='"'
    #     delimiter=';'
    #     fileobj = TemporaryFile('w+')
    #     sourceEncoding = 'windows-1252'
    #     targetEncoding = "utf-8"   
    #     
    #     fileobj.write((base64.decodestring(this.data)))   
    #     fileobj.seek(0)                                    
    #     reader = csv.DictReader(fileobj, quotechar=str(quotechar), delimiter=str(delimiter))        
    #     city = self.pool.get('res.city')
    #             
    #     move_id=''
    #     all_move_ids=[]
    #     employee = self.pool.get('hr.employee')
    #     for row  in reader : 
    #         if str(row['ISSUE_PLACE_NO']):
    #                 city_ids=city.search(cr, uid, [('code', '=',row['ISSUE_PLACE_NO'])])
    #                 if city_ids:
    #                     city_name=city.browse(cr, uid, city_ids[0]).name
    #         employee_ids= employee.search(cr, uid, [('number', '=',str(row['EMP_NO']))])
    #         print 'employee_ids',str(row['EMP_NO'])
    #         if employee_ids:
    #             emplyee_obj=employee.browse(cr, uid, employee_ids[0]) 
    #             emplyee_obj.write( {'passport_id': str(row['DOC_NO']),'passport_date':str(row['ISSUE_DATE']),'passport_place':city_name,'passport_end_date':str(row['EXPIRY_DATE'])}, )
    #     
    #     
    #         
    #     
    #     return True
    #===========================================================================
         
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
            if len(str(row['MGR_NO'].strip(" ")))==4:
                employee_id_parent = str(0)+str(row['MGR_NO'].strip(" "))
            elif len(str(row['MGR_NO'].strip(" ")))==3:
                employee_id_parent = str(0)+str(0)+str(row['MGR_NO'].strip(" "))
            elif len(str(row['MGR_NO'].strip(" ")))==2:
                employee_id_parent = str(0)+str(0)+str(0)+str(row['MGR_NO'].strip(" "))
            elif len(str(row['MGR_NO'].strip(" ")))==1:
                employee_id_parent = str(0)+str(0)+str(0)+str(0)+str(row['MGR_NO'].strip(" "))
            else:
                employee_id_parent = str(row['MGR_NO'].strip(" "))
            employee_ids_parent= employee.search(cr, uid, [('number', '=',employee_id_parent)])
            if len(str(row['EMP_NO'].strip(" ")))==4:
                employee_id = str(0)+str(row['EMP_NO'].strip(" "))
            elif len(str(row['EMP_NO'].strip(" ")))==3:
                employee_id = str(0)+str(0)+str(row['EMP_NO'].strip(" "))
            elif len(str(row['EMP_NO'].strip(" ")))==2:
                employee_id = str(0)+str(0)+str(0)+str(row['EMP_NO'].strip(" "))
            elif len(str(row['EMP_NO'].strip(" ")))==1:
                employee_id= str(0)+str(0)+str(0)+str(0)+str(row['EMP_NO'].strip(" "))
            else:
                employee_id = str(row['EMP_NO'].strip(" "))
            employee_ids_file= employee.search(cr, uid, [('number', '=',employee_id)])
            if employee_ids_parent and employee_ids_file  :
                if employee_ids_parent[0] != employee_ids_file[0]:
                    try:
                        emplyee_obj_file=employee.browse(cr, uid, employee_ids_file[0]) 
                        emplyee_obj_file.write( {'parent_id': employee_ids_parent[0]}, ) 
                    except:
                        False
        return True   
    
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
                if parent_id == 6:
                    print str(row['CHI_GRP_NO'])
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
            
    def import_dudpension(self, cr, uid, ids, context=None):
        
      
        
         
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
        terminated_obj = self.pool.get('hr.suspension')
        terminated_closed_obj = self.pool.get('hr.suspension.end')
        move_id=''
        all_move_ids=[]
        for row  in reader :  
            employee=employee_obj.search(cr, uid, [('number', '=',str(row['EMP_NO']))])
            terminated_val={
                                'date':row['DECISION_DATE'] if  row['DECISION_DATE'] != 'NULL' else  False,
                                'employee_id':employee[0] if employee else False,
                                'suspension_date':row['START_DATE'] if  row['START_DATE'] != 'NULL' else  False,
                                'letter_number':row['DECISION_NO'] if  row['DECISION_NO'] != 'NULL' else  False,
                                'letter_date':row['DECISION_DATE'] if  row['DECISION_DATE'] != 'NULL' else  False,
                                'raison':str(row['REASON_AR']),
                                'state':'done',
                                }
            
            id_terminated=terminated_obj.create(cr, uid, terminated_val,context=context)
            if str(row['IS_CLOSED'])=="1":
                terminated_closed_val={
                                'date':row['CLS_DECISION_DATE'] if  row['CLS_DECISION_DATE'] != 'NULL' else  False,
                                'employee_id':employee[0] if employee else False,
                                'suspension_id':id_terminated,
                                'letter_no':row['CLS_DECISION_NO'],
                                'letter_date':row['CLS_DECISION_DATE'] if  row['CLS_DECISION_DATE'] != 'NULL' else  False,
                                'release_date':row['END_DATE'] if  row['END_DATE'] != 'NULL' else  False,
                                'condemned':True if str(row['IS_PENALIZED']) else False,
                                'state':'done',
                                }
                terminated_closed_obj.create(cr, uid, terminated_closed_val,context=context)
                
                
                
              
           
        
    
            
        
        return True
    
    def import_terminated(self, cr, uid, ids, context=None):
             
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
        terminated_obj = self.pool.get('hr.termination')
        terminated_obj_type = self.pool.get('hr.termination.type')
        move_id=''
        all_move_ids=[]
        employee_name=False
        for row  in reader :
           
            employee=employee_obj.search(cr, uid, [('number', '=',str(row['EMP_NO']))])
            if not employee:
                print 'not' ,str(row['EMP_NO'])
            if employee:
                employee_name=employee_obj.browse(cr, uid, employee[0]).name
                terminated_type =terminated_obj_type.search(cr, uid, [('code', '=',str(row['TERMINATION_CODE']))])
                if terminated_type:
                    terminated_val={
                                'name':'طي القيد الموظف :' + employee_name ,
                                'date':row['DECISION_DATE'] if  row['DECISION_DATE'] != 'NULL' else  False,
                                'employee_id':employee[0] if employee else False,
                                'date_termination':row['TERMINATION_DATE'] if  row['TERMINATION_DATE'] != 'NULL' else  False,
                                'letter_no':row['DECISION_NO'] if  row['DECISION_NO'] != 'NULL' else  '111',
                                'letter_date':row['DECISION_DATE'] if  row['DECISION_DATE'] != 'NULL' else  False,
                                'state':'done' if str(row['IS_TERMINATED']) == '1' else False ,
                                'termination_type_id':terminated_type[0] if terminated_type else False
                }
                     
                    terminated_obj.create(cr, uid, terminated_val,context=context)
                   
               
                
           
                
            
        return True

    def import_holidays(self, cr, uid, ids, context=None):
        start = timeit.default_timer()
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
        holiday_obj = self.pool.get('hr.holidays')
        status_study=self.pool.get('ir.model.data').get_object_reference(cr, uid, 'smart_hr', 'data_hr_holiday_status_study')[1]
        status_normal=self.pool.get('ir.model.data').get_object_reference(cr, uid, 'smart_hr', 'data_hr_holiday_status_normal')[1]
        status_maladie=self.pool.get('ir.model.data').get_object_reference(cr, uid, 'smart_hr', 'data_hr_holiday_status_illness')[1]
        exceptional=self.pool.get('ir.model.data').get_object_reference(cr, uid, 'smart_hr', 'data_hr_holiday_status_exceptional')[1]
        compiling=self.pool.get('ir.model.data').get_object_reference(cr, uid, 'smart_hr', 'data_hr_holiday_status_compelling')[1]
        sport=self.pool.get('ir.model.data').get_object_reference(cr, uid, 'smart_hr', 'data_hr_holiday_status_sport')[1]
        accompaniment=self.pool.get('ir.model.data').get_object_reference(cr, uid, 'smart_hr', 'data_hr_holiday_status_exceptional_accompaniment')[1]
        absent=self.pool.get('ir.model.data').get_object_reference(cr, uid, 'smart_hr', 'data_hr_holiday_status_legal_absent')[1]
        compelling=self.pool.get('ir.model.data').get_object_reference(cr, uid, 'smart_hr', 'data_hr_holiday_status_compelling')[1]
        
        move_id=''
        all_move_ids=[]
        i=0
        fmt = '%d/%m/%Y'
        umalqurra = Umalqurra()
        for row  in reader :
                employee=employee_obj.search(cr, uid, [('number', '=',str(row['EMP_NO']))])
             
                if  str(row['TOTAL_USED'])!='NULL':
                    if employee:
                       
                        if  str(row['LEAVE_TYPE']) == '1':
                            type_holiday=status_normal
                        elif str(row['LEAVE_TYPE']) == '20':
                            type_holiday=compelling
                        elif str(row['LEAVE_TYPE']) == '23':
                            type_holiday=status_study
                        elif str(row['LEAVE_TYPE']) == '5':
                            type_holiday=status_maladie
                        elif str(row['LEAVE_TYPE']) == '12':
                            type_holiday=sport
                        elif str(row['LEAVE_TYPE']) == '13':
                            type_holiday=accompaniment
                        elif str(row['LEAVE_TYPE']) == '333':
                            type_holiday=absent
                        else :
                            type_holiday=exceptional
                            
                            
                      
                        
                        if row['REFERENCE_DATE_HJ'] != 'NULL':
                                try:
                                    dt = datetime.strptime(str(row['REFERENCE_DATE_HJ']), fmt)
                                    start_date = umalqurra.hijri_to_gregorian(dt.year, dt.month, dt.day)
                                    date2 = date(int(start_date[0]), int(start_date[1]), int(start_date[2]))
                                    
                                except:
                                    date2 = False
                        else :
                            date2 = False
                            
                          
                        duration = str(row['TOTAL_USED']).replace('.00','')
                        start_date=str(row['START_DATE'])[:10]
                       
                        date1=datetime.strptime(start_date,"%Y-%m-%d")
                        date_to=date1+ relativedelta(day=(date1.day+int(duration)-1))
                        
                        holiday_val={
                                        'name':row['REQUEST_NO'] if  row['REQUEST_NO'] != 'NULL' else  False,
                                        'employee_id':employee[0] if employee else False,
                                        'date_from':row['START_DATE']if  row['START_DATE'] != 'NULL' else  False,
                                        'date_to':date_to,
                                        'duration':int(duration),
                                        'date_decision':date2,
                                        'num_decision':row['REQUEST_NO'] if  row['REQUEST_NO'] != 'NULL' else  False,
                                        'holiday_status_id':type_holiday if type_holiday!='employee' else False,
                                        'state': 'done' ,
                                        }
                        
                        holiday_obj.create(cr, uid, holiday_val,context=context)
                        
                        
        stop = timeit.default_timer()
        print 'time for import employee', stop - start       
        return True
    
    
    def import_holidays_extension(self, cr, uid, ids, context=None):
          
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
        holiday_obj = self.pool.get('hr.holidays')
        status_study=self.pool.get('ir.model.data').get_object_reference(cr, uid, 'smart_hr', 'data_hr_holiday_status_study')[1]
        status_normal=self.pool.get('ir.model.data').get_object_reference(cr, uid, 'smart_hr', 'data_hr_holiday_status_normal')[1]
        status_maladie=self.pool.get('ir.model.data').get_object_reference(cr, uid, 'smart_hr', 'data_hr_holiday_status_illness')[1]
        exceptional=self.pool.get('ir.model.data').get_object_reference(cr, uid, 'smart_hr', 'data_hr_holiday_status_exceptional')[1]
        compiling=self.pool.get('ir.model.data').get_object_reference(cr, uid, 'smart_hr', 'data_hr_holiday_status_compelling')[1]
        sport=self.pool.get('ir.model.data').get_object_reference(cr, uid, 'smart_hr', 'data_hr_holiday_status_sport')[1]
        accompaniment=self.pool.get('ir.model.data').get_object_reference(cr, uid, 'smart_hr', 'data_hr_holiday_status_exceptional_accompaniment')[1]
        absent=self.pool.get('ir.model.data').get_object_reference(cr, uid, 'smart_hr', 'data_hr_holiday_status_legal_absent')[1]
        compelling=self.pool.get('ir.model.data').get_object_reference(cr, uid, 'smart_hr', 'data_hr_holiday_status_compelling')[1]
        
        move_id=''
        all_move_ids=[]
        i=0
        
        for row  in reader :
            
            if  str(row['LEAVE_TYPE']) == '1':
                type_holiday=status_normal
            elif str(row['LEAVE_TYPE']) == '20':
                type_holiday=compelling
            elif str(row['LEAVE_TYPE']) == '23':
                type_holiday=status_study
            elif str(row['LEAVE_TYPE']) == '5':
                type_holiday=status_maladie
            elif str(row['LEAVE_TYPE']) == '12':
                type_holiday=sport
            elif str(row['LEAVE_TYPE']) == '13':
                type_holiday=accompaniment
            elif str(row['LEAVE_TYPE']) == '333':
                type_holiday=absent
            else :
                type_holiday=exceptional        
                        
                            
                            
                
           
            holidays_parent=holiday_obj.search(cr, uid, [('num_decision', '=',str(row['REQUEST_NO']))])
            
            if  holidays_parent :
                holidays=holiday_obj.browse(cr, uid, holidays_parent[0])
                
              
                duration = str(row['DAYS_USED']).replace('.000','')
                
                holiday_val={
                                'employee_id':holidays.employee_id.id,
                                'date_from':row['FROM_DATE']if  row['FROM_DATE'] != 'NULL' else  False,
                                'date_to':row['TO_DATE']if  row['TO_DATE'] != 'NULL' else  False,
                                'duration':int(duration),
                                'date_decision':row['REFERENCE_DATE']  if  row['REFERENCE_DATE'] != 'NULL' else  False,
                                'state': 'done' ,
                                'extended_holiday_id':holidays_parent[0],
                                'num_outspeech':row['REFERENCE_ID'],
                                'num_decision':row['REQUEST_NO'] if  row['REQUEST_NO'] != 'NULL' else  False,
                                'is_extension':True,
                                }
                
                holiday_obj.create(cr, uid, holiday_val,context=context)
               
                   
                
        return True
    
    def import_holiday_stock(self, cr, uid, ids, context=None):
          
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
        entitlement=self.pool.get('hr.holidays.status.entitlement')
        holiday_stock_obj = self.pool.get('hr.employee.holidays.stock')
        holiday_stock_type_obj= self.pool.get('hr.holidays.entitlement.config')
        status_normal=self.pool.get('ir.model.data').get_object_reference(cr, uid, 'smart_hr', 'data_hr_holiday_status_normal')[1]
        type=self.pool.get('ir.model.data').get_object_reference(cr, uid, 'smart_hr', 'data_hr_holiday_entitlement_all')[1]
        move_id=''
        all_move_ids=[]
        entitlement_val={
                                'entitlment_category':type,
                                'leave_type':status_normal,
                                'holiday_stock_default':36,
                                'periode':1,
                                }
        id_entitlment=  entitlement.create(cr, uid, entitlement_val,context=context)
        
        for row  in reader :
            employee_ids= employee_obj.search(cr, uid, [('number', '=',str(row['EMP_NO']))])
            if  employee_ids :
                holiday_stock_val={
                                'employee_id':employee_ids[0],
                                'holiday_status_id':status_normal,
                                'holidays_available_stock':float(str(row['BALANCE'])),
                                'entitlement_id':id_entitlment,
                                }
                
                holiday_stock_obj.create(cr, uid, holiday_stock_val,context=context)
            else:
                print 'employee non importer',str(row['EMP_NO'])
                
                
        return True
    
    
    def import_update_education_level_employee(self, cr, uid, ids, context=None):
        start = timeit.default_timer()
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
       
        diploma = self.pool.get('hr.employee.diploma')
     
        specialiter = self.pool.get('hr.employee.specialization')
        education_level_id=False
        grade_id=False
        diplome_id=False
        city_id=False
        religion_id=False
        salary_grid_level_id=False
        
        move_id=''
        all_move_ids=[]
        city_name=False
        job = self.pool.get('hr.job')
        employee = self.pool.get('hr.employee')
        partner = self.pool.get('res.partner')
        job_education_level= self.pool.get('hr.employee.job.education.level')
        umalqurra = Umalqurra()
        fmt = '%d/%m/%Y'
        for row  in reader: 
            employee_ids=employee.search(cr, uid, [('number', '=',row['EMP_NO'])])
            if employee_ids and row['LOC_ID']=='3369' : 
                if str(row['MAJOR_NO']):
                    specialiter_ids = specialiter.search(cr, uid, [('code', '=',row['MAJOR_NO'])])
                    if specialiter_ids:
                        specialiter_id =specialiter_ids[0]
                if str(row['DEGREE_NO']):
                    diplome_ids=diploma.search(cr, uid, [('code', '=',row['DEGREE_NO'])])
                    if diplome_ids:
                        diplome_id=diplome_ids[0]
              
                if str(row['DEGREE_PLACE']):
                    partner_ids=partner.search(cr, uid, [('code', '=',row['DEGREE_PLACE'])])
                    if partner_ids:
                        partner_id=partner_ids[0]
                if row['DEGREE_DATE_HJ'] != 'NULL':
                    try:
                        dt = datetime.strptime(str(row['DEGREE_DATE_HJ']), fmt)
                        start_date = umalqurra.hijri_to_gregorian(dt.year, dt.month, dt.day)
                        date1 = date(int(start_date[0]), int(start_date[1]), int(start_date[2]))
                    except:
                        date1 = False
                
                vals_education={'name':'01',
                                'diploma_id':diplome_id,
                                'specialization_ids':[(6,0,[specialiter_id])],
                                'diploma_date':date1,
                                'governmental_entity':partner_id,
                                'while_serving':True,
                                }
                
                id_eductaion_level=job_education_level.create(cr, uid, vals_education,context=context)
                emplyee_obj=employee.browse(cr, uid, employee_ids[0]) 
                emplyee_obj.write({'education_level_ids':[(4,id_eductaion_level)],})

   
        stop = timeit.default_timer()
        print 'time for import employee', stop - start
        return True
            


    def update_groups_general(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        this = self.browse(cr, uid, ids[0])   
        quotechar = '"'
        delimiter = ';'
        fileobj = TemporaryFile('w+')
        fileobj.write((base64.decodestring(this.data)))
        fileobj.seek(0)
        reader = csv.DictReader(fileobj, quotechar=str(quotechar), delimiter=str(delimiter))
        groups = self.pool.get('hr.groupe.job')
        salary_grid_grade = self.pool.get('salary.grid.grade')
        for row in reader:
            pos_grp_no = str(row['POS_GRP_NO'])
            exist_groups = groups.search(cr, uid, [('numero','=',str(row['POS_GRP_NO']))],context=context)
            if exist_groups:
                min_grade_no = salary_grid_grade.search(cr, uid, [('code','=', str(row['MIN_GRADE_NO']))], context=context)
                max_grade_no = salary_grid_grade.search(cr, uid, [('code','=', str(row['MAX_GRADE_NO']))], context=context)
                min_max_vals = {'rank_from': min_grade_no[0] if min_grade_no else False, 'rank_to': max_grade_no[0] if max_grade_no else False}
                groups.browse(cr, uid, exist_groups[0], context=context).write(min_max_vals)

    def update_groups_general_code(self, cr, uid, ids, context=None):
        groups = self.pool.get('hr.groupe.job')
        for group_id in groups.search(cr, uid, []):
            group_browse = groups.browse(cr, uid, group_id)
            new_num = group_browse.numero.strip(" ")
            group_browse.write({'numero': new_num})
        if context is None:
            context = {}
        this = self.browse(cr, uid, ids[0])
        quotechar = '"'
        delimiter = ';'
        fileobj = TemporaryFile('w+')
        fileobj.write((base64.decodestring(this.data)))
        fileobj.seek(0)
        reader = csv.DictReader(fileobj, quotechar=str(quotechar), delimiter=str(delimiter))
        groups = self.pool.get('hr.groupe.job')
        for row in reader:
            parent_group = groups.search(cr, uid, [('numero', '=', str(row['PAR_GRP_NO']))], context=context)
            current_group = groups.search(cr, uid, [('numero', '=', str(row['CHI_GRP_NO']))], context=context)
            if parent_group and current_group:
                groups.browse(cr, uid, current_group[0], context=context).write({'parent_id': parent_group[0]})
        return True
    
    
    def emplyee_historique(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        this = self.browse(cr, uid, ids[0])
        quotechar = '"'
        delimiter = ';'
        fileobj = TemporaryFile('w+')
        fileobj.write((base64.decodestring(this.data)))
        fileobj.seek(0)
        reader = csv.DictReader(fileobj, quotechar=str(quotechar), delimiter=str(delimiter))
        employee = self.pool.get('hr.employee')
        history = self.pool.get('hr.employee.history')
        grade = self.pool.get('salary.grid.grade')
        for row in reader:
            if len(str(row['EMP_NO'].strip(" ")))==4:
                empid = str(0)+str(row['EMP_NO'].strip(" "))
            elif len(str(row['EMP_NO'].strip(" ")))==3:
                empid = str(0)+str(0)+str(row['EMP_NO'].strip(" "))
            elif len(str(row['EMP_NO'].strip(" ")))==2:
                empid = str(0)+str(0)+str(0)+str(row['EMP_NO'].strip(" "))
            elif len(str(row['EMP_NO'].strip(" ")))==1:
                empid = str(0)+str(0)+str(0)+str(0)+str(row['MGR_NO'].strip(" "))
            else:
                empid = str(row['EMP_NO'].strip(" "))
                            
            employee_ids = employee.search(cr, uid, [('number', '=', empid)])
            fmt = '%d/%m/%Y'
            date1 = False
            date2 = False
            umalqurra = Umalqurra()
            if row['DECISION_DATE_HJ'] != 'NULL':
                    try:
                        dt = datetime.strptime(str(row['DECISION_DATE_HJ']), fmt)
                        start_date = umalqurra.hijri_to_gregorian(dt.year, dt.month, dt.day)
                        date1 = date(int(start_date[0]), int(start_date[1]), int(start_date[2]))
                    except:
                        date1 = False
            if row['FIELD_EFF_DATE_HJ'] != 'NULL':
                try:
                    um_date = HijriDate()
                    date_end = datetime.strptime(str(row['FIELD_EFF_DATE_HJ']), fmt)
                    start_date2 = umalqurra.hijri_to_gregorian(date_end.year, date_end.month, date_end.day)
                    date2 = date(int(start_date2[0]), int(start_date2[1]), int(start_date2[2]))
                except:
                    date2 = False
            if employee_ids:
                employee_id = employee.browse(cr, uid, employee_ids[0])
                dep_side = employee_id.user_id.company_id.name
                grade_id = False
                grade_ids = grade.search(cr, uid, [('code', '=',row['rank_new'])])
                if grade_ids:
                    grade_id=grade_ids[0]
                
                try:
                    history_line_val={
                            'employee_id':employee_ids[0],
                            'type':str(row['ACT_DSCR']),
                            'num_decision':str(row['DECISION_NO']),
                            'date_decision':date1,
                            'date':date2,
                            'job_id': str(row['position']) if str(row['position']) !='NULL' else str(row['position_old']),
                            'dep_side': str(row['side']),
                            'grade_id':grade_id,
                            'number':str(row['rank_new'])+str(row['degree_new']),
                            'department_id':employee_id.department_id.id,
                            }
                    history.create(cr, uid, history_line_val,context=context)
                    
                except :
                        print "I/O error({0}): {1}"
                    

        return True
   
    def emplyee_historique_appoint(self, cr, uid, ids, context=None):
        appoint_type=self.pool.get('ir.model.data').get_object_reference(cr, uid, 'smart_hr', 'data_hr_new_agent_public')[1]
        if context is None:
            context = {}
        this = self.browse(cr, uid, ids[0])
        quotechar = '"'
        delimiter = ';'
        fileobj = TemporaryFile('w+')
        fileobj.write((base64.decodestring(this.data)))
        fileobj.seek(0)
       
        employee = self.pool.get('hr.employee')
        job=self.pool.get('hr.job')
        history = self.pool.get('hr.employee.history')
        grade = self.pool.get('salary.grid.grade')
        appoint = self.pool.get('hr.decision.appoint')
        fmt = '%d/%m/%Y'
        with open('/home/aymen/EMP_JOB_HISTORY.csv') as csvfile:
            reader = csv.DictReader(csvfile, quotechar='"', delimiter=';')
            for row in reader:
                if row['ACT_TYPE_ID']=='51' and row['FIELD_NAME']=='POSITION_NO':
                    empid = str(row['EMP_NO'].strip(" "))
                    employee_ids = employee.search(cr, uid, [('number', '=', empid)])
                    if employee_ids:
                        employee_id = employee.browse(cr, uid, employee_ids[0])
                        dep_side = employee_id.user_id.company_id.name
                        dates=str(row['FIELD_EFF_DATE'])
                        dates1=dates[0:10]
                        grade_id = False
                        job_id=job.search(cr, uid,  [('number', '=',str(row['FIELD_NEW_VALUE']))])
                        dt = datetime.strptime((dates1),"%Y-%m-%d")
                         
                        date2=dt+ relativedelta(day=dt.day+1)
                        
                             
    #                     try:
                    
                        appoint_id=appoint.search(cr, uid,  [('employee_id', '=',employee_ids[0])])
                        if not appoint_id:
                            apoint_val={                    'employee_id':employee_ids[0],    
                                                                'name':row['SEQ_NO'],
                                                               'order_date': row['FIELD_EFF_DATE'],
                                                               'date_hiring': date2,
                                                               'date_direct_action': date2,
                                                               'job_id':job_id[0] if job_id else False,
                                                               'degree_id':employee_id.degree_id.id,
                                                               'type_appointment':appoint_type,
                                                               'depend_on_test_periode':True,
                                                               'state':'done',
                                                               'first_appoint':True,
                                                                
                                                               }
                             
                            
                            appoint.create(cr, uid, apoint_val,context=context)
    #                     except Exception, e:
    #                         cr.rollback()
                             
                            
                     
 
        return True
    
    
    def emplyee_historique_promotion(self, cr, uid, ids, context=None):
        appoint_type=self.pool.get('ir.model.data').get_object_reference(cr, uid, 'smart_hr', 'data_hr_promotion_agent')[1]
        if context is None:
            context = {}
        this = self.browse(cr, uid, ids[0])
        quotechar = '"'
        delimiter = ';'
        fileobj = TemporaryFile('w+')
        fileobj.write((base64.decodestring(this.data)))
        fileobj.seek(0)
       
        employee = self.pool.get('hr.employee')
        job=self.pool.get('hr.job')
        history = self.pool.get('hr.employee.history')
        grade = self.pool.get('salary.grid.grade')
        appoint = self.pool.get('hr.decision.appoint')
        promotion=self.pool.get('hr.promotion.employee.job')
        fmt = '%d/%m/%Y'
        with open('/home/aymen/EMP_JOB_HISTORY.csv') as csvfile:
            reader = csv.DictReader(csvfile, quotechar='"', delimiter=';')
            for row in reader:
                if (row['ACT_TYPE_ID']=='73' or row['ACT_TYPE_ID']=='96')  :
                    empid = str(row['EMP_NO'].strip(" "))
                    employee_ids = employee.search(cr, uid, [('number', '=', empid)])
                    if employee_ids:
                        employee_id = employee.browse(cr, uid, employee_ids[0])
                        dep_side = employee_id.user_id.company_id.name
                        dates=str(row['FIELD_EFF_DATE'])
                        dates1=dates[0:10]
                        grade_id = False
                        job_id=False
                        old_job=False
                        new_grade=False
                        old_grade=False
                        if row['FIELD_NAME']=='POSITION_NO':
                            job_id=job.search(cr, uid,  [('number', '=',str(row['FIELD_NEW_VALUE']))])
                            old_job=job.search(cr, uid,  [('number', '=',str(row['FIELD_OLD_VALUE']))])
                        if row['FIELD_NAME']=='GRADE_NO':
                            new_grade=grade.search(cr, uid,  [('code', '=',str(row['FIELD_NEW_VALUE']))])
                            old_grade=grade.search(cr, uid,  [('code', '=',str(row['FIELD_OLD_VALUE']))])
                        dt = datetime.strptime((dates1),"%Y-%m-%d")
                         
                        date2=dt+ relativedelta(day=dt.day+1)
                             
    #                     try:
                        appoint_id=appoint.search(cr, uid,  [('name', '=',row['REQUEST_NO'])])
                        if not appoint_id:
                            apoint_val={                    
                                                                  
                                                                'employee_id':employee_ids[0],    
                                                                'name':row['REQUEST_NO'],
                                                               'order_date': row['FIELD_EFF_DATE'],
                                                               'date_hiring': date2,
                                                               'date_direct_action': date2,
                                                               'job_id':job_id[0] if job_id else False,
                                                               'degree_id':employee_id.degree_id.id,
                                                               'type_appointment':appoint_type,
                                                               'depend_on_test_periode':True,
                                                               'state':'done',
                                                               
                                                                
                                                               }
                             
                            
                            appoint.create(cr, uid, apoint_val,context=context)
                            promotio_val={                    
                                                                'employee_id':employee_ids[0],    
                                                                'name':row['REQUEST_NO'],
                                                               'date_direct_action': row['FIELD_EFF_DATE'],
                                                               'old_job_id':old_job[0] if old_job else False,
                                                               'emp_grade_id_old':old_grade[0] if old_grade else False,
                                                               'new_job_id':job_id[0] if job_id else False,
                                                               'emp_grade_id_new':new_grade[0] if new_grade else False,
                                                               'state':'done',
                                                               }
                                                                
                                                           
                            promotion.create(cr, uid, promotio_val,context=context)
                           
                        else:
                            print 2
                            if row['FIELD_NAME']=='POSITION_NO':
                                job_id=job.search(cr, uid,  [('number', '=',str(row['FIELD_NEW_VALUE']))])
                                old_job=job.search(cr, uid,  [('number', '=',str(row['FIELD_OLD_VALUE']))]) 
                                promotion_id=promotion.search(cr, uid,  [('name', '=',row['REQUEST_NO'])])
                                if promotion_id:
                                    val={'old_job_id':old_job[0] if old_job else False,'new_job_id':job_id[0] if job_id else False, 'date_direct_action': row['FIELD_EFF_DATE'],}
                                    promotion.write(cr, uid,promotion_id, val,context=context)
                                    
                            if row['FIELD_NAME']=='GRADE_NO':
                                print 3
                                new_grade=grade.search(cr, uid,  [('code', '=',str(row['FIELD_NEW_VALUE']))])
                                old_grade=grade.search(cr, uid,  [('code', '=',str(row['FIELD_OLD_VALUE']))]) 
                                promotion_id=promotion.search(cr, uid,  [('name', '=',row['REQUEST_NO'])])
                                if promotion_id:
                                    val={'emp_grade_id_new':new_grade[0] if new_grade else False, 'emp_grade_id_old':old_grade[0] if old_grade else False, 'date_direct_action': row['FIELD_EFF_DATE'],}
                                    promotion.write(cr, uid,promotion_id, val,context=context)
                                   
                                    
                      
    #                     except Exception, e:
    #                         cr.rollback()
                             
                            
                     
 
        return True
    def emplyee_historique_appoint_lines(self, cr, uid, ids, context=None):
        appoint_type=self.pool.get('ir.model.data').get_object_reference(cr, uid, 'smart_hr', 'data_hr_new_agent_public')[1]
        if context is None:
            context = {}
        this = self.browse(cr, uid, ids[0])
        quotechar = '"'
        delimiter = ';'
        fileobj = TemporaryFile('w+')
        fileobj.write((base64.decodestring(this.data)))
        fileobj.seek(0)
        reader = csv.DictReader(fileobj, quotechar=str(quotechar), delimiter=str(delimiter))
        employee = self.pool.get('hr.employee')
        job=self.pool.get('hr.job')
        history = self.pool.get('hr.employee.history')
        grade = self.pool.get('salary.grid.grade')
        appoint = self.pool.get('hr.decision.appoint')
        fmt = '%d/%m/%Y'
        with open('/home/aymen/Desktop/EMP_JOB_HISTORY.csv') as csvfile:
            reader = csv.DictReader(csvfile, quotechar=str(quotechar), delimiter=str(delimiter))
            for row in reader:
                if row['ACT_TYPE_ID']=='52' and row['FIELD_NAME']=='POSITION_NO':
                    empid = str(row['EMP_NO'].strip(" "))
                    employee_ids = employee.search(cr, uid, [('number', '=', empid)])
                    if employee_ids:
                        employee_id = employee.browse(cr, uid, employee_ids[0])
                        dep_side = employee_id.user_id.company_id.name
                        dates=str(row['FIELD_EFF_DATE'])
                        dates1=dates[0:10]
                        print employee_id.grade_id.id
                        grade_id = False
                        job_id=job.search(cr, uid,  [('number', '=',str(row['FIELD_NEW_VALUE']))])
                        dt = datetime.strptime((dates1),"%Y-%m-%d")
                        
                        date2=dt+ relativedelta(day=dt.day+1)
                       
                            
    #                     try:
                        if job_id:
                                apoint_val={                   'employee_id':employee_ids[0],    
                                                                'name':row['SEQ_NO'],
                                                               'order_date': row['FIELD_EFF_DATE'],
                                                               'date_hiring': date2,
                                                               'date_direct_action': date2,
                                                               'job_id':job_id[0],
                                                               'degree_id':employee_id.degree_id.id,
                                                               'type_appointment':appoint_type,
                                                               'depend_on_test_periode':True,
                                                               'state':'done',
                                                               
                                                               }
                            
                           
                                appoint.create(cr, uid, apoint_val,context=context)
    #                     except Exception, e:
    #                         cr.rollback()
                            
                       
                    

        return True
    
    def emplyee_historique_appoint_direct(self, cr, uid, ids, context=None):
        appoint_type=self.pool.get('ir.model.data').get_object_reference(cr, uid, 'smart_hr', 'data_hr_new_agent_public')[1]
        if context is None:
            context = {}
        this = self.browse(cr, uid, ids[0])
        quotechar = '"'
        delimiter = ';'
        fileobj = TemporaryFile('w+')
        fileobj.write((base64.decodestring(this.data)))
        fileobj.seek(0)
        reader = csv.DictReader(fileobj, quotechar=str(quotechar), delimiter=str(delimiter))
        employee = self.pool.get('hr.employee')
        job=self.pool.get('hr.job')
        history = self.pool.get('hr.employee.history')
        grade = self.pool.get('salary.grid.grade')
        appoint = self.pool.get('hr.direct.appoint')
        fmt = '%d/%m/%Y'
        for row in reader:
            if row['ACT_TYPE_ID']=='51' and row['FIELD_NAME']=='POSITION_NO':
                empid = str(row['EMP_NO'].strip(" "))
                employee_ids = employee.search(cr, uid, [('number', '=', empid)])
                if employee_ids:
                    employee_id = employee.browse(cr, uid, employee_ids[0])
                    dep_side = employee_id.user_id.company_id.name
                    dates=str(row['FIELD_EFF_DATE'])
                    dates1=dates[0:10]
                    grade_id = False
                    job_id=job.search(cr, uid,  [('number', '=',str(row['FIELD_NEW_VALUE']))])
                    dt = datetime.strptime((dates1),"%Y-%m-%d")
                    
                    date2=dt+ relativedelta(day=dt.day+1)
                    
                   
                    
#                     try:
                    if job_id:
                        jobs=job.browse(cr, uid,job_id[0] )
                        print job_id[0]
                        apoint_val={                   'employee_id':employee_ids[0],    
                                                           'date': row['FIELD_EFF_DATE'],
                                                           'date_direct_action': date2,
                                                            'job_id':job_id[0],
                                                           'grade_id':employee_id.grade_id.id,
                                                           'type_id':employee_id.type_id.id,
                                                           'department_id':employee_id.department_id.id,
                                                           'type_appointment':appoint_type,
                                                           'state':'done',
                                                           'state_direct':'done',
                                                           'number_job':jobs.number,
                                                           
                                                           }
                        
                       
                        appoint.create(cr, uid, apoint_val,context=context)
#                     except Exception, e:
#                         cr.rollback()
                        
                       
                    

        return True
 
   
    def emplyee_historique_appoint_transport(self, cr, uid, ids, context=None):
        appoint_type=self.pool.get('ir.model.data').get_object_reference(cr, uid, 'smart_hr', 'data_hr_new_agent_public')[1]
        if context is None:
            context = {}
        this = self.browse(cr, uid, ids[0])
        quotechar = '"'
        delimiter = ';'
        fileobj = TemporaryFile('w+')
        fileobj.write((base64.decodestring(this.data)))
        fileobj.seek(0)
        reader = csv.DictReader(fileobj, quotechar=str(quotechar), delimiter=str(delimiter))
        employee = self.pool.get('hr.employee')
        job=self.pool.get('hr.job')
        history = self.pool.get('hr.employee.history')
        grade = self.pool.get('salary.grid.grade')
        transport = self.pool.get('hr.employee.transfert')
        fmt = '%d/%m/%Y'
        for row in reader:
            if row['ACT_TYPE_ID']=='63' and row['FIELD_NAME']=='POSITION_NO':
                empid = str(row['EMP_NO'].strip(" "))
                employee_ids = employee.search(cr, uid, [('number', '=', empid)])
                if employee_ids:
                    employee_id = employee.browse(cr, uid, employee_ids[0])
                    dep_side = employee_id.user_id.company_id.name
                    dates=str(row['FIELD_EFF_DATE'])
                    dates1=dates[0:10]
                    print employee_id.grade_id.id
                    grade_id = False
                    job_id=job.search(cr, uid,  [('number', '=',str(row['FIELD_NEW_VALUE']))])
                    dt = datetime.strptime((dates1),"%Y-%m-%d")
                    
                    date2=dt+ relativedelta(day=dt.day+1)
                   
                    type_id=fields.Many2one('salary.grid.type',string='الصنف',store=True,readonly=1) 
                    department_id=fields.Many2one('hr.department',string='الادارة',store=True,readonly=1)
                    grade_id=fields.Many2one('salary.grid.grade',string='المرتبة',store=True,readonly=1)
                    
#                     try:
                    if job_id:
                            apoint_val={                   'employee_id':employee_ids[0],    
                                                            'name':row['SEQ_NO'],
                                                           'date': row['FIELD_EFF_DATE'],
                                                           'date_direct_action': date2,
                                                           'job_id':job_id[0],
                                                           'grade_id':employee_id.grade_id.id,
                                                           'type_id':employee_id.type_id.id,
                                                           'department_id':employee_id.department_id,
                                                           'type_appointment':appoint_type,
                                                           'state':'done',
                                                           'state_direct':'done',
                                                           
                                                           }
                        
                       
                            appoint.create(cr, uid, apoint_val,context=context)
#                     except Exception, e:
#                         cr.rollback()
                        
                       
                    

        return True





    def emplyee_historique_appoint_promotion(self, cr, uid, ids, context=None):
        appoint_type=self.pool.get('ir.model.data').get_object_reference(cr, uid, 'smart_hr', 'data_hr_new_agent_public')[1]
        if context is None:
            context = {}
        this = self.browse(cr, uid, ids[0])
        quotechar = '"'
        delimiter = ';'
        fileobj = TemporaryFile('w+')
        fileobj.write((base64.decodestring(this.data)))
        fileobj.seek(0)
        reader = csv.DictReader(fileobj, quotechar=str(quotechar), delimiter=str(delimiter))
        employee = self.pool.get('hr.employee')
        job=self.pool.get('hr.job')
        history = self.pool.get('hr.employee.history')
        grade = self.pool.get('salary.grid.grade')
        appoint = self.pool.get('hr.direct.appoint')
        fmt = '%d/%m/%Y'
        for row in reader:
            if row['ACT_TYPE_ID']=='63' and row['FIELD_NAME']=='POSITION_NO':
                empid = str(row['EMP_NO'].strip(" "))
                employee_ids = employee.search(cr, uid, [('number', '=', empid)])
                if employee_ids:
                    employee_id = employee.browse(cr, uid, employee_ids[0])
                    dep_side = employee_id.user_id.company_id.name
                    dates=str(row['FIELD_EFF_DATE'])
                    dates1=dates[0:10]
                    print employee_id.grade_id.id
                    grade_id = False
                    job_id=job.search(cr, uid,  [('number', '=',str(row['FIELD_NEW_VALUE']))])
                    dt = datetime.strptime((dates1),"%Y-%m-%d")
                    
                    date2=dt+ relativedelta(day=dt.day+1)
                   
                    type_id=fields.Many2one('salary.grid.type',string='الصنف',store=True,readonly=1) 
                    department_id=fields.Many2one('hr.department',string='الادارة',store=True,readonly=1)
                    grade_id=fields.Many2one('salary.grid.grade',string='المرتبة',store=True,readonly=1)
                    
#                     try:
                    if job_id:
                            apoint_val={                   'employee_id':employee_ids[0],    
                                                            'name':row['SEQ_NO'],
                                                           'date': row['FIELD_EFF_DATE'],
                                                           'date_direct_action': date2,
                                                           'job_id':job_id[0],
                                                           'grade_id':employee_id.grade_id.id,
                                                           'type_id':employee_id.type_id.id,
                                                           'department_id':employee_id.department_id,
                                                           'type_appointment':appoint_type,
                                                           'state':'done',
                                                           'state_direct':'done',
                                                           
                                                           }
                        
                       
                            appoint.create(cr, uid, apoint_val,context=context)
#                     except Exception, e:
#                         cr.rollback()
                        
                       
                    

        return True





    def update_employee_manager(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        departement = self.pool.get('hr.department')
        employee = self.pool.get('hr.employee')
        i=0
        for emp in employee.search(cr, uid, [('parent_id', '=', False)]):
            emp_browse = employee.browse(cr, uid, emp, context=context)
            if emp_browse.department_id:
                if emp_browse.department_id.manager_id.id==emp:
                    if emp_browse.department_id.parent_id.manager_id.id!=emp:
                        emp_browse.write({'parent_id':emp_browse.department_id.parent_id.manager_id.id})
                    else:
                        i+=1

                else:
                    emp_browse.write({'parent_id': emp_browse.department_id.manager_id.id})
            else:
                i+=1
        print i
        return True
    
    def update_employe_citys(self, cr, uid, ids, context=None):
         
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
        city = self.pool.get('res.city')
        for row  in reader: 
            if row['EMP_NO'] and row['BIRTH_PLACE']  : 
                employee_id=employee.search(cr, uid, [('number', '=',str(row['EMP_NO']))])
                city_id=city.search(cr, uid, [('code', '=',str(row['BIRTH_PLACE']))])
                if employee_id and city_id:
                    val={'place_of_birth':city_id[0]}
                    employee.write(cr, uid,employee_id, val,context=context)
                    
        return True


    
    def update_passport(self, cr, uid, ids, context=None):
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
        umalqurra = Umalqurra() 
        move_id=''
        all_move_ids=[]
        employee = self.pool.get('hr.employee')
        fmt = '%d/%m/%Y'
        brth_dates=False
        for row  in reader : 
            if row['ISSUE_DATE_HJ'] != 'NULL':
                    try:
                        row['ISSUE_DATE_HJ'].replace("29/2", "28/2")
                        dt = datetime.strptime(str(row['ISSUE_DATE_HJ']), fmt)
                        start_date = umalqurra.hijri_to_gregorian(dt.year, dt.month, dt.day)
                        date_first_tranche = date(int(start_date[0]), int(start_date[1]), int(start_date[2]))
                    except:
                        print row['ISSUE_DATE_HJ']

            if str(row['ISSUE_PLACE_NO']):
                    city_ids=city.search(cr, uid, [('code', '=',row['ISSUE_PLACE_NO'])])
                    print city_ids
            employee_ids= employee.search(cr, uid, [('number', '=',str(row['EMP_NO']))])
            if employee_ids:
                emplyee_obj=employee.browse(cr, uid, employee_ids[0]) 
                emplyee_obj.write( {'hoveizeh_id': str(row['DOC_NO']),'hoveizeh_date':date_first_tranche,'hoveizeh_place':city_ids[0] if city_ids else False ,
                                    'hoveizeh_end_date':False,}, )
        
        
        return True
    
    
    def update_job(self, cr, uid, ids, context=None):
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
        move_id=''
        all_move_ids=[]
        departement = self.pool.get('hr.department')
        hr_job=self.pool.get('hr.job')
        type = self.pool.get('salary.grid.type')
        grade = self.pool.get('salary.grid.grade')
        job_name = self.pool.get('hr.job.name')
        job_group=self.pool.get('hr.groupe.job')
        serie_id=False
        job_name_id=False
        general_id=False
        i=0
        
        for row  in reader : 
           
                hr_job_id=hr_job.search(cr, uid, [('number', '=',str(row['POSITION_NO']))])
                job_name_id = job_name.search(cr, uid, [('number', '=',str(row['POSITION_CODE']))])
                if hr_job_id and job_name_id:
                    print job_name_id[0]
                    val={'name':job_name_id[0]}
                    hr_job.write(cr, uid,hr_job_id[0], val,context=context)

        return True 
    
    def import_training_course(self, cr, uid, ids, context=None):
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
        move_id=''
        all_move_ids=[]
        training_id = self.pool.get('hr.training')
        for row  in reader : 
           
                hr_job_id=hr_job.search(cr, uid, [('number', '=',str(row['POSITION_NO']))])
                job_name_id = job_name.search(cr, uid, [('number', '=',str(row['POSITION_CODE']))])
                if hr_job_id and job_name_id:
                    print job_name_id[0]
                    val={'name':job_name_id[0]}
                    hr_job.write(cr, uid,hr_job_id[0], val,context=context)
                    
                 
               
                
        
        
        
        
        return True 
        
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
        print 11111
        for row  in reader : 
            if row['name']: 
                diplome.search(cr, uid, [('code', '=',row['code'])])
                if len(diplome.search(cr, uid, [('code', '=',row['code'])]))==0:
                    diplome_val={
                            'name':(row['name']).decode('utf-8').strip(),
                            'code':(row['code']).decode('utf-8').strip(),
                            }
          
                    diplome.create(cr, uid, diplome_val,context=context)
         
        
        
    def update_saudi_citys_coutry(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        city = self.pool.get('res.city')
        country = self.pool.get('res.country')
        sa_country_id = country.search(cr, uid, [('code_nat', '=','SA')])
        city_ids = city.search(cr, uid, [])
        for city_id in city_ids:
            city.write(cr, uid,city_id, {'country_id':sa_country_id[0]},context=context)
        return True
    
    def import_contry_categorys(self, cr, uid, ids, context=None):
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
        print 6551665454654656454
        country_obj = self.pool.get('res.country')
        city_obj = self.pool.get('res.city')
        categ_obj = self.pool.get('hr.deputation.category')
        country_city_obj = self.pool.get('hr.country.city')
        
        move_id=''
        all_move_ids=[]
        for row  in reader :  
            print 7777
            #create move line
            code = str(row['code'].strip(" "))
            if code =='0001':
                code = 'SA'
            if code ==0001:
                code = 'SA'
            category = row['category']
            city = row['city']
            if category:
                category_id = categ_obj.search(cr, uid, [('category', '=',category)])
                if not category_id:
                    print 777755555
                    category_val = categ_obj.create(cr, uid, {'category':category,'name':category})
                else:
                    print 777758888
                    category_val = category_id[0]
                country = country_obj.search(cr, uid, [('code_nat', '=',code)])
                country_name=country_obj.browse(cr, uid, country[0]).name
                print '55555',country_name
                if country:
                    if city:
                        city_id = city_obj.create(cr, uid, {'name': city, 'country_id': country[0]}, context=context)
                        print 8888
                        country_city_vals = {
                            'name':country_name,
                            'country_id': country[0],
                            'city_id': city_id,
                            'duputation_category_id': category_val,
                            }
                    else:
                        print 1000
                        country_city_vals={
                            'name':country_name,
                            'country_id':country[0],
                            'duputation_category_id': category_val,
                            }
                    print 999
                    country_city_obj.create(cr, uid, country_city_vals)


    def import_deputation_settings(self, cr, uid, ids, context=None):
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
        categ_obj = self.pool.get('hr.deputation.category')
        grade_obj = self.pool.get('salary.grid.grade')
        dep_allowance_obj = self.pool.get('hr.deputation.allowance')
        dep_allowance_line = self.pool.get('hr.deputation.allowance.line')
        dep_setting_obj = self.pool.get('hr.deputation.setting')
        dep_setting_search = dep_setting_obj.search(cr, uid, [])[0]
        
        for row in reader:
            #create move line
            grade_group = str(row['grade_group'].strip(" "))
            grade_id = str(row['grade_id'].strip(" "))
            int_trans_type = str(row['int_trans_type'].strip(" "))
            int_dep_type = str(row['int_dep_type'].strip(" "))
            int_transt_amount = row['int_transt_amount']
            int_dep_amount = row['int_dep_amount']
            ext_trans_type = str(row['ext_trans_type'].strip(" "))
            ext_trans_amount = row['ext_trans_amount']
            ext_dep_hight = row['ext_dep_hight']
            ext_dep_a = row['ext_dep_a']
            ext_dep_b = row['ext_dep_b']
            ext_dep_c = row['ext_dep_c']

            grade = grade_obj.search(cr, uid, [('code', '=',grade_id)])
            dep_allowance = dep_allowance_obj.search(cr, uid, [('name', '=',grade_group)])
            if dep_allowance:
                dep_allowance_id = dep_allowance[0]
                dep_allowance_obj.write(cr, uid,dep_allowance_id, {'grade_ids': [(4, grade[0])]})
            else:
                dep_setting_vals={
                    'name':grade_group,
                    'grade_ids': [(6, 0, [grade[0]])],
                    'internal_transport_type': int_trans_type,
                    'internal_transport_amount': int_transt_amount,
                    'internal_deputation_type': int_dep_type,
                    'internal_deputation_amount': int_dep_amount,
                    'external_transport_type': ext_trans_type,
                    'external_transport_amount': ext_trans_amount,
                    'deputation_setting_id' : dep_setting_search,
                    'external_deputation_type': 'daily',

                    }
                dep_allowance_id = dep_allowance_obj.create(cr, uid, dep_setting_vals)
                high_categ_id = categ_obj.search(cr, uid, [('category', '=','high')])[0]
                a_categ_id = categ_obj.search(cr, uid, [('category', '=','a')])[0]
                b_categ_id = categ_obj.search(cr, uid, [('category', '=','b')])[0]
                c_categ_id = categ_obj.search(cr, uid, [('category', '=','c')])[0]
                dep_allowance_line_vals_high = {
                    'deputation_allowance_id': dep_allowance_id,
                    'category_id':high_categ_id,
                    'amount':ext_dep_hight
                }
                dep_allowance_line_vals_a = {
                    'deputation_allowance_id': dep_allowance_id,
                    'category_id':a_categ_id,
                    'amount':ext_dep_a
                }
                dep_allowance_line_vals_b = {
                    'deputation_allowance_id': dep_allowance_id,
                    'category_id':b_categ_id,
                    'amount':ext_dep_b
                }
                dep_allowance_line_vals_c = {
                    'deputation_allowance_id': dep_allowance_id,
                    'category_id':c_categ_id,
                    'amount':ext_dep_c
                }
                dep_allowance_line_high = dep_allowance_line.create(cr, uid, dep_allowance_line_vals_high)
                dep_allowance_line_a = dep_allowance_line.create(cr, uid, dep_allowance_line_vals_a)
                dep_allowance_line_b = dep_allowance_line.create(cr, uid, dep_allowance_line_vals_b)
                dep_allowance_line_c = dep_allowance_line.create(cr, uid, dep_allowance_line_vals_c)
                
    def import_universitty(self, cr, uid, ids, context=None):
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
        move_id=''
        all_move_ids=[]
        school = self.pool.get('res.partner')
        for row  in reader :  
            school_val={
                            'name':row['name'],
                            'code':str(row['code']),
                            'company_type':'school'
                            
                            }
            
            school.create(cr, uid, school_val,context=context)
        
        
            
        
        return True 
    
    def update_birthday(self, cr, uid, ids, context=None):
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
        umalqurra = Umalqurra() 
        move_id=''
        all_move_ids=[]
        employee = self.pool.get('hr.employee')
        fmt = '%d/%m/%Y'
        brth_dates=False
        for row  in reader : 
           
            if str(row['LOC_ID']) == "3369":
                if str(row['BIRTH_PLACE']):
                        city_ids=city.search(cr, uid, [('code', '=',row['BIRTH_PLACE'])])
                        
                employee_ids= employee.search(cr, uid, [('number', '=',str(row['EMP_NO']))])
                if employee_ids:
                
                    emplyee_obj=employee.browse(cr, uid, employee_ids[0]) 
                    emplyee_obj.write( {'place_of_birth':city_ids[0] if city_ids else False,}, )
        
        
        return True
    
    def import_update_education_level_employee_before_job(self, cr, uid, ids, context=None):
        start = timeit.default_timer()
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
       
        diploma = self.pool.get('hr.employee.diploma')
     
        specialiter = self.pool.get('hr.employee.specialization')
        education_level_id=False
        grade_id=False
        diplome_id=False
        city_id=False
        religion_id=False
        salary_grid_level_id=False
        
        move_id=''
        all_move_ids=[]
        city_name=False
        job = self.pool.get('hr.job')
        employee = self.pool.get('hr.employee')
        partner = self.pool.get('res.partner')
        job_education_level= self.pool.get('hr.employee.job.education.level')
        umalqurra = Umalqurra()
        fmt = '%d/%m/%Y'
        for row  in reader: 
            employee_ids=employee.search(cr, uid, [('number', '=',row['EMP_NO'])])
            if employee_ids  : 
                if str(row['MAJOR_NO']):
                    specialiter_ids = specialiter.search(cr, uid, [('code', '=',row['MAJOR_NO'])])
                    if specialiter_ids:
                        specialiter_id =specialiter_ids[0]
                if str(row['DEGREE_NO']):
                    diplome_ids=diploma.search(cr, uid, [('code', '=',row['DEGREE_NO'])])
                    if diplome_ids:
                        diplome_id=diplome_ids[0]
              
                if str(row['COLL_NO']):
                    partner_ids=partner.search(cr, uid, [('code', '=',row['COLL_NO'])])
                    if partner_ids:
                        partner_id=partner_ids[0]
                date1 = False
                if row['FROM_DATE_HJ'] != 'NULL':
                    try:
                        dt = datetime.strptime(str(row['FROM_DATE_HJ']), fmt)
                        start_date = umalqurra.hijri_to_gregorian(dt.year, dt.month, dt.day)
                        date1 = date(int(start_date[0]), int(start_date[1]), int(start_date[2]))
                    except:
                        date1 = False
                
                vals_education={'name':'00',
                                'diploma_id':diplome_id,
                                'specialization_ids':[(6,0,[specialiter_id])],
                                'diploma_date':date1,
                                'governmental_entity':partner_id,
                                }
                
                id_eductaion_level=job_education_level.create(cr, uid, vals_education,context=context)
                emplyee_obj=employee.browse(cr, uid, employee_ids[0]) 
                emplyee_obj.write({'education_level_ids':[(6,0,[id_eductaion_level])],})

   
        stop = timeit.default_timer()
        print 'time for import employee', stop - start
        return True
    
    def import_externel_side(self, cr, uid, ids, context=None):
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
        move_id=''
        all_move_ids=[]
        departement = self.pool.get('external.authorities')
        for row  in reader :

            daprtment_val={
                            'name':str(row['name']),
                            'code':str(row['code']),
                            }

            departement.create(cr, uid, daprtment_val,context=context)
        return True
    def emplyee_historique_before(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        this = self.browse(cr, uid, ids[0])
        quotechar = '"'
        delimiter = ';'
        fileobj = TemporaryFile('w+')
        fileobj.write((base64.decodestring(this.data)))
        fileobj.seek(0)
        reader = csv.DictReader(fileobj, quotechar=str(quotechar), delimiter=str(delimiter))
        employee = self.pool.get('hr.employee')
        history = self.pool.get('hr.employee.history')
        grade = self.pool.get('salary.grid.grade')
        ext = self.pool.get('external.authorities')
        for row in reader:
            if len(str(row['EMP_NO'].strip(" ")))==4:
                empid = str(0)+str(row['EMP_NO'].strip(" "))
            elif len(str(row['EMP_NO'].strip(" ")))==3:
                empid = str(0)+str(0)+str(row['EMP_NO'].strip(" "))
            elif len(str(row['EMP_NO'].strip(" ")))==2:
                empid = str(0)+str(0)+str(0)+str(row['EMP_NO'].strip(" "))
            elif len(str(row['EMP_NO'].strip(" ")))==1:
                empid = str(0)+str(0)+str(0)+str(0)+str(row['MGR_NO'].strip(" "))
            else:
                empid = str(row['EMP_NO'].strip(" "))
                            
            employee_ids = employee.search(cr, uid, [('number', '=', empid)])
            extr_ids = ext.search(cr, uid, [('code', '=', str(row['EXT_ENT_ID']))])
            fmt = '%d/%m/%Y'
            date1 = False
            date2 = False
            umalqurra = Umalqurra()
            if row['DECISION_DATE_HJ'] != 'NULL':
                    try:
                        dt = datetime.strptime(str(row['DECISION_DATE_HJ']), fmt)
                        start_date = umalqurra.hijri_to_gregorian(dt.year, dt.month, dt.day)
                        date1 = date(int(start_date[0]), int(start_date[1]), int(start_date[2]))
                    except:
                        date1 = False
            if row['STATUS_DATE_HJ'] != 'NULL':
                try:
                    um_date = HijriDate()
                    date_end = datetime.strptime(str(row['STATUS_DATE_HJ']), fmt)
                    start_date2 = umalqurra.hijri_to_gregorian(date_end.year, date_end.month, date_end.day)
                    date2 = date(int(start_date2[0]), int(start_date2[1]), int(start_date2[2]))
                except:
                    date2 = False
            else:
                     date1 = False
            ext_name=False
            if extr_ids:
                ext_name=ext.browse(cr, uid, extr_ids[0]).name               
            if employee_ids:
                employee_id = employee.browse(cr, uid, employee_ids[0])
                dep_side = employee_id.user_id.company_id.name
                grade_id = False
                grade_ids = grade.search(cr, uid, [('code', '=',row['GRADE_NO'])])
                if grade_ids:
                    grade_id=grade_ids[0]
                if str(row['TITLE_DSCR_AR']) !='NULL':
                   
                        history_line_val={
                                'employee_id':employee_ids[0],
                                'num_decision':str(row['DECISION_NO']),
                                'date_decision':date1,
                                'date':date2,
                                'job_id': str(row['TITLE_DSCR_AR']),
                                'dep_side': ext_name,
                                'grade_id':grade_id,
                                'number':str(row['EXT_PAY_CODE']),
                                }
                        history.create(cr, uid, history_line_val,context=context)
                        
                    
                    

        return True
   
            

import_csv()




