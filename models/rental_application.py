from dateutil.relativedelta import relativedelta
import logging

_logger = logging.getLogger(__name__)

from odoo import api,fields,models

class rental_application(models.Model):
    _name = 'rental.application'
    _description = 'Rental Application'

    user_id = fields.Many2one('res.users', string='User', required=True, default=lambda self: self.env.user)
    state = fields.Selection([
        ('new', 'New'),
        ('active','Active'),
        ('done','Done')
    ], default='new', readonly=True, copy=False)

    from_date = fields.Date(required=True, default=lambda self:fields.Date.today() + relativedelta(days=1))#from next day
    to_date = fields.Date(required=True, default=lambda self:fields.Date.today() + relativedelta(days=8))#to next week
    total_cost = fields.Float(compute='_compute_total_cost', string='Total', readonly=True)
    
    equipment_ids = fields.Many2many('rental.equipment', string='Equipment')
    rented_equipment_ids = fields.One2many('rental.equipment', 'app_id', store=False, readonly=True)
    
    @api.depends('equipment_ids','from_date','to_date')
    def _compute_total_cost(self):
        for record in self:
            sum_cost = 0
            period = (record.to_date - record.from_date).days
            for equipment in record.equipment_ids:
                sum_cost += equipment.fees * period
            record.total_cost = sum_cost
        record._validate_rented_ids()
    
    @api.onchange('from_date','to_date')
    def _onchange_dates(self):
        if(self.from_date <= fields.Date.today()):
            _logger.info('From_Date validation failed')
            self.from_date = fields.Date.today() + relativedelta(days=1)
        if(self.to_date <= self.from_date):
            _logger.info('To_Date validation failed')
            self.to_date = self.from_date + relativedelta(days=1)
        self._validate_rented_ids()
    
    def _validate_rented_ids(self):
        self.rented_equipment_ids = False
        all_conflict_apps = self.env['rental.application'].search(['&',
        ('state','!=','Done'),
        '|',
        '&',('from_date','<=',self.from_date),('to_date','>=',self.from_date),
        '&',('from_date','<=',self.to_date),('to_date','>=',self.to_date)
        ])
        self.rented_equipment_ids = all_conflict_apps.mapped('equipment_ids.id')
        return False