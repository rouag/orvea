{
    "name": "Calandar Hijri",
    'version': '9.0.1.0',
    'summary': 'Web',
    "description":
        "Calandar Hijri"
        ,
    "depends": ['web'],
    'category': 'web',
    'data': [
         "res_users_view.xml",
         "views/assets.xml"    
    ],
   
    'qweb' : [
         "static/src/xml/*.xml",
    ],
    'installable': True,    
    'auto_install': False,
}
