from odoo import fields,models

class rental_application(models.Model):
    _name = 'rental.application'
    _description = 'Rental Application'

    user_id = fields.Many2one('res.users', string='User', required=True, default=lambda self: self.env.user)
    state = fields.Selection([
        ('new', 'New'),
        ('active','Active'),
        ('done','Done')
    ], default='new', readonly=True, copy=False)

    from_date = fields.Date(required=True)
    to_date = fields.Date(required=True)

    total_cost = fields.Float(string='Total', readonly=True)