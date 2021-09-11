from dateutil.relativedelta import relativedelta

from odoo import api,fields,models,_
from odoo.exceptions import ValidationError

class rental_equipment(models.Model):
    _name = 'rental.equipment'
    _description = 'Rental Equipment'

    name = fields.Char(required=True, copy=False)
    description = fields.Char()
    category_id = fields.Many2one('rental.equipment.category', string='Category', required=True)
    owner_id = fields.Many2one("res.partner", string="Owner", required=True)
    fees = fields.Float(required=True)
    state = fields.Selection([
        ('available', 'Available'),
        ('rented', 'Rented'),
        ('late', 'Late')
    ], default='available', readonly=True, copy=False)

    app_id = fields.Many2one('rental.application', store=False) # Fake Field

    return_date = fields.Date(compute='_compute_return_date', readonly=True, store=False)
    user_id = fields.Many2one('res.users', string='Renter', readonly=True, store=False)
    
    @api.depends('state')
    def _compute_return_date(self):
        for record in self:
            record.user_id = None
            record.return_date = fields.Date.today()
            if(record.state != 'available'):
                # Get all "Active applications" then check for equipment ID
                all_active_apps = record.env['rental.application'].search([('state','=','active')])
                for app in all_active_apps:
                    if (record._origin.id in app.mapped('equipment_ids.id')):
                        record.user_id = app.user_id
                        record.return_date = app.to_date + relativedelta(days=1)
                        return

    @api.constrains('fees')
    def _check_fees(self):
        for record in self:
            if(record.fees < 0):
                raise ValidationError(_('Do you pay for people to make them rent your stuff!!! fees should be valuable'))
            elif(record.fees == 0):
                raise ValidationError(_('Rent your stuff for free!!! fees should be valuable'))