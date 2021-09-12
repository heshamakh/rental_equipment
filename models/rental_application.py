from dateutil.relativedelta import relativedelta
import logging

_logger = logging.getLogger(__name__)

from odoo import api,fields,models,_
from odoo.exceptions import ValidationError

class rental_application(models.Model):
    _name = 'rental.application'
    _description = 'Rental Application'

    user_id = fields.Many2one('res.users', string='Renter', required=True, default=lambda self: self.env.user)
    state = fields.Selection([
        ('new', 'New'),
        ('active','Active'),
        ('late','Late'),
        ('done','Done')
    ], default='new', readonly=True, copy=False)

    from_date = fields.Date(required=True, default=lambda self:fields.Date.today() + relativedelta(days=1))#from next day
    to_date = fields.Date(required=True, default=lambda self:fields.Date.today() + relativedelta(days=8))#to next week
    total_cost = fields.Float(compute='_compute_total_cost', string='Total', readonly=True)
    
    equipment_ids = fields.Many2many('rental.equipment', string='Equipment')
    rented_equipment_ids = fields.One2many('rental.equipment', 'app_id', store=False, readonly=True)

    name = fields.Char(compute='_compute_name', store=False, readonly=True)
    
    @api.depends('equipment_ids')
    def _compute_name(self):
        for record in self:
            record.name = f'{str(record.id)}-RA for {", ".join(record.equipment_ids.mapped("name"))}'
    
    @api.depends('equipment_ids','from_date','to_date')
    def _compute_total_cost(self):
        for record in self:
            sum_cost = 0
            period = (record.to_date - record.from_date).days
            for equipment in record.equipment_ids:
                sum_cost += equipment.fees * period
            record.total_cost = sum_cost
        record._get_rented_equipment()
    
    @api.onchange('from_date','to_date')
    def _onchange_dates(self):
        if(self.from_date <= fields.Date.today()):
            _logger.info('From_Date validation failed')
            self.from_date = fields.Date.today() + relativedelta(days=1)
        if(self.to_date <= self.from_date):
            _logger.info('To_Date validation failed')
            self.to_date = self.from_date + relativedelta(days=1)
        self._get_rented_equipment()
    
    def _get_rented_equipment(self):
        """Always We have to gather rented equipment from Applications
        in case a new application was saved during create the newest"""
        self.rented_equipment_ids = False
        
        # Get all "open application" that conflict with these dates
        all_conflict_apps = self.env['rental.application'].search([
            ('id','!=',self._origin.id),
            ('state','!=','done'),
            '|',
            '|',
            '&',('from_date','>',self.from_date),('to_date','<',self.to_date),
            '&',('from_date','<=',self.from_date),('to_date','>=',self.from_date),
            '&',('from_date','<=',self.to_date),('to_date','>=',self.to_date)
            ])
        self.rented_equipment_ids = all_conflict_apps.mapped('equipment_ids.id')
        _logger.info(f'to be rented ids {self.rented_equipment_ids}')
    
    @api.constrains('equipment_ids')
    def _check_equipment_ids(self):
        for record in self:
            record._get_rented_equipment()
            # Validate Potential Equipment if will be available
            for equipment in record.equipment_ids:
                _logger.info(f'check equipment "{equipment.id}-{equipment.name}"')
                if equipment in record.rented_equipment_ids:
                    raise ValidationError(_(f'"{equipment.name}" Equipment is rented or reserved to be rent on the same period of your application'))
            if(len(record.equipment_ids) < 2):
                raise ValidationError(_('Rental Application should be created for two equipment at least'))
    
    def cron_check_late(self):
        today = fields.Date.today()
        # Get all "Active & Late applications"
        all_late_active_apps = record.env['rental.application'].search([('state','=','active'),('to_date','<',today)])
        for app in all_late_active_apps:
            app.state = 'late'
            for equipment in app.equipment_ids:
                equipment.state = 'late'
    
    def activate_application_action(self):
        if(self.from_date > fields.Date.today()):
            raise ValidationError(_('You can not activate this application before its day'))
        elif(self.state != 'new'):
            raise ValidationError(_('This application is already activated'))
        self.state = 'active'
        for equipment in self.equipment_ids:
            equipment.state = 'rented'
    
    def finish_application_action(self):
        if(self.to_date > fields.Date.today()):
            raise ValidationError(_('You can not finish this application before its day'))
        elif(self.state == 'new'):
            raise ValidationError(_('This application should be activated first'))
        elif(self.state == 'done'):
            raise ValidationError(_('This application is already done'))
        self.state = 'done'
        for equipment in self.equipment_ids:
            equipment.state = 'available'