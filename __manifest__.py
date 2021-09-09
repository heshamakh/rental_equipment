{
    'name': 'Rental Equipment',
    'summary': 'track equipment rental process',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/rental_equipment_category_view.xml',
        'views/rental_equipment_view.xml',
        'views/rental_menus.xml'
    ],
	'installable': True,
    'application': True
}