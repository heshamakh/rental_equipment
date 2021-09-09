from odoo import fields,models

class rental_equipment_category(models.Model):
    _name = 'rental.equipment.category'
    _description = 'Rental Equipment Category'

    name = fields.Char(required=True)
    