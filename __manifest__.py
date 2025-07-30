{
    'name': 'CRM With Image',
    'version': '17.0',
    'category': 'Tools',
    'author':'Mauro Bogado',
    'summary': 'Modulo para poder realizar la carga de una imagen comprimida y con marca de agua',
    'depends': ['base','crm','sale','web', 'website'],
    'data': [
        'security/ir.model.access.csv',
        'views/product_with_image.xml',
        #'views/assets.xml',
        'views/view_partner_form_photographer.xml',
        'views/website_menuitem_photographer.xml',
        'views/website_menu.xml',
        'views/view_equitacion.xml',
        'views/product_with_image.xml',
        
        
    ],
    'assets': {
    'web.assets_frontend': [
        'crm_with_image/static/src/js/custom_cart.js',
    ],
    },

    'installable': True,
    'application': False,
}   