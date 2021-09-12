{
    'name': 'Rental Equipment',
    'version': '1.0.0',
    'summary': 'track equipment rental process',
    'website': 'https://github.com/heshamakh/rental_equipment',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/rental_equipment_category_view.xml',
        'views/rental_equipment_view.xml',
        'views/rental_application_view.xml',
        'views/rental_menus.xml'
    ],
	'installable': True,
    'application': True
}