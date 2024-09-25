# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ServiceTeam(models.Model):
    # Model info 
    _name = 'booking_order_farras_arrafi_26092024.service_team'
    _description = 'Service Team'

    name = fields.Char('Team Name', required=True)
    
    # Team Settings 
    team_leader = fields.Many2one('res.users', string='Team Leader', required=True)
    team_members = fields.Many2many('res.users', string='Team Members')
    
class SaleOrder(models.Model):
    # Inherti from a model 
    _inherit = 'sale.order'
    
    is_booking_order = fields.Boolean('Is Booking Order', default=False)
    
    # Team settings 
    team = fields.Many2one('booking_order_farras_arrafi_26092024.service_team', string='Team')
    team_leader = fields.Many2one('res.users', string='Team Leader')
    team_members = fields.Many2many('res.users', string='Team Members')
    
    # Booking date 
    booking_start = fields.Datetime('Booking Start')
    booking_end = fields.Datetime('Booking End')
    
class WorkOrder(models.Model):
    
    # Model info 
    _name = 'booking_order_farras_arrafi_26092024.work_order'
    _description = 'Work Order'
    
    name = fields.Char("WO Number", required=True, default=lambda self: self.env['ir.sequence'].next_by_code('wo_sequence'))
    booking_order_reference = fields.Many2one('sale.order', string='Booking Order Reference', readonly=True)
    
    # Team Settings 
    team = fields.Many2one('booking_order_farras_arrafi_26092024.service_team', string='Team')
    team_leader = fields.Many2one('res.users', string='Team Leader')
    team_members = fields.Many2many('res.users', string='Team Members')
    
    # Planned Date 
    planned_start = fields.Datetime('Planned Start', required=True)
    planned_end = fields.Datetime('Planned End', required=True)
    
    # Actual Date
    date_start = fields.Datetime('Date Start', readonly=True)
    date_end = fields.Datetime('Date End', readonly=True)
    
    # States 
    state = fields.Selection([
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='pending', readonly=True)
    
    notes = fields.Text('Notes')
    