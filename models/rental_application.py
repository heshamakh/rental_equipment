from dateutil.relativedelta import relativedelta
import datetime
#from lxml import etree
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

    total_cost = fields.Float(string='Total', readonly=True)

    #potential_equipment_ids = fields.Char(default="[('id','in',[1,2])]", store=False, readonly=True)
    rented_equipment_ids = fields.One2many('rental.equipment', 'app_id', store=False)
    
    @api.onchange("from_date","to_date")
    def _onchange_dates(self):
        if(self.from_date <= fields.Date.today()):
            _logger.info('From_Date validation failed')
            self.from_date = fields.Date.today() + relativedelta(days=1)
        if(self.to_date <= self.from_date):
            _logger.info('To_Date validation failed')
            self.to_date = self.from_date + relativedelta(days=1)
        #all_conflict_apps = self.env['rental.application'].search(['&',
        #('state','!=','Done'),
        #'|',
        #'&',('from_date','<=',self.from_date),('to_date','>=',self.from_date),
        #'&',('from_date','<=',self.to_date),('to_date','>=',self.to_date)
        #])
        #self.rented_equipment_ids = all_conflict_apps.mapped('equipment_ids').mapped('id')
        all_conflict_apps = self.env['rental.application'].search([('state','!=','Done')])
        self.rented_equipment_ids = False
        for app in all_conflict_apps:
            if(((self.from_date >= app.from_date) and (self.from_date <= app.to_date))
            or ((self.to_date >= app.from_date) and (self.to_date <= app.to_date))):
                _logger.info('conflict_app_id:')
                _logger.info(app.id)
                #for equipment_id in app.equipment_ids:
                #    _logger.info('equipment_id:')
                #    _logger.info(equipment_id.id)
                self.rented_equipment_ids = app.equipment_ids.mapped('id')
                _logger.info('update rented_ids:')
                _logger.info(self.rented_equipment_ids)
        #self.equipment_ids.domain = [('id','not in',self.rented_equipment_ids)]
        #self.potential_equipment_ids = "{'domain': [('id', 'not in' , ["+','.join([str(i) for i in self.rented_equipment_ids])+"])]}"
        #self.potential_equipment_ids = "[" + ','.join([str(i) for i in self.rented_equipment_ids])+ "]"


    #@api.depends('potential_equipment_ids')
    #def _compute_potential_equipment_ids(self):
    #    _logger.info('_compute_potential_equipment_ids:')
    #    _logger.info(self.potential_equipment_ids)
    #    return self.potential_equipment_ids
    
    equipment_ids = fields.Many2many('rental.equipment', string='Equipment')#, domain=_compute_potential_equipment_ids)
    

    #@api.model
    #def fields_view_get(self, view_id=None, view_type='form', toolbar=None, submenu=None):
    #    result = super().fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
    #    if view_type == 'form':
    #        doc = etree.XML(result['arch'])
    #        sale_reference = doc.xpath("//field[@name='equipment_ids']")
    #        if sale_reference:
    #            sale_reference[0].set("domain", "[('id','in',[1,2])]")
    #            #sale_reference[0].addnext(etree.Element('domain', {'string': self.rented_equipment_ids}))
    #            result['arch'] = etree.tostring(doc, encoding='unicode')
    #    
    #    return result