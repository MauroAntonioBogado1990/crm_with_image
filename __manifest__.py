{
    'name': 'CRM With Image',
    'version': '17.0',
    'category': 'Tools',
    'author':'Mauro Bogado',
    'summary': 'Modulo para poder realizar la carga de una imagen comprimida y con marca de agua',
    'depends': ['base','crm','sale'],
    'data': [
        #'security/ir.model.access.csv',
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