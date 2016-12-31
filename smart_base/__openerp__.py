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
    'depends': ['base', 'web', 'report'],
    'data': [
        'security/ir.model.access.csv',
        'data/paperformat.xml',
        'view/res_company.xml',
        'views/layout.xml',
        'views/assets.xml',
             ],
    'qweb': ['static/src/xml/*.xml'],
    'auto_install': False,
}
