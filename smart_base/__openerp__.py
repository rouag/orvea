# -*- coding: utf-8 -*-

{
    'name': 'Smart Base',
    'version': '9.0.1.0',
    'author': 'Smart',
    'summary': 'Smart Base',
    'description':
        """
        Module base  can be used in any app
        """,
    'depends': ['base', 'web', 'report', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'data/paperformat.xml',
        'data/template_email.xml',
        'view/res_company.xml',
        'view/notification.xml',
        'view/notification_setting.xml',
        'views/layout.xml',
        'views/assets.xml',
             ],
    'qweb': ['static/src/xml/*.xml'],
    'external_dependencies': {'python': ['umalqurra']},
    'auto_install': False,
}
