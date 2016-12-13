# -*- coding: utf-8 -*-

{
    'name': 'Smart HR',
    'version': '9.0.1.0',
    'author': 'SMART-ETEK',
    'summary': 'HR',
    'description':
        """
        """,
    'depends': ['hr','hr_holidays','odoo_rtl','web_readonly_bypass'],
    'data': [
        'security/hr_security.xml',
        'security/ir.model.access.csv',
        
        'view/hr_menu.xml',
        'view/hr.xml',
        'view/hr_job.xml',
        'view/hr_decision_appoint.xml',
        'view/hr_holidays.xml',
        'view/hr_promotion.xml',
        'view/salary_grid.xml',
        'view/hr_training.xml',
        'view/hr_exam_emp.xml',
        'view/res_partner.xml',
        'view/judicial_precedent.xml',
        'view/recruiter.xml',
        
        
        'views/report_salary_grid.xml',
        'views/report_medical_examination.xml',
        'views/report_order_enquiry.xml',
        'views/report.xml',
        'views/templates.xml',
        
        'data/sequences.xml',
        'data/configurations.xml',
    ],
    'auto_install': False,
}
