from odoo import fields,models

class rental_equipment(models.Model):
    _name = 'rental.equipment'
    _description = 'Rental Equipment'

    name = fields.Char(required=True, copy=False)
    description = fields.Char()
    category_id = fields.Many2one('rental.equipment.category', string='Category', required=True)
    owner_id = fields.Many2one("res.partner", string="Owner", required=True)
    fees = fields.Float(digits=(total, decimal), required=True)
    state = fields.Selection([
        ('available', 'Available'),
        ('rented', 'Rented'),
        ('late', 'Late')
    ], default='available', readonly=True, copy=False)