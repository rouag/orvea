# -*- encoding: utf-8 -*-

{
    'name': 'Odoo Theme',
    'version': '9.0.1.0.0',
    'category': 'Web',
    'summary': """
Theme For odoo
""",
    'author': "Borni",
    'depends': ['web'
    ],
    'data': [
        'data/data.xml', 
        'views/login.xml',
        'views/home.xml',
        'views/assets.xml',
    ],
    'qweb' : [
        "static/src/xml/*.xml",
    ],
    'installable': True,
    'application': False,
}
