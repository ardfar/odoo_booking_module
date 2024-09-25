# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError

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
    
    @api.model
    def create(self, vals):
        if 'prevent_save' in self._context:
            return True
        else:
            # Set booking order to True
            vals['is_booking_order'] = True
            # Call super
            return super(SaleOrder, self).create(vals)
    
    @api.model
    def write(self, vals):
        if 'prevent_save' in self._context:
            return True
        else:
            # Set booking order to True
            vals['is_booking_order'] = True
            # Call super
            return super().write(vals)
    
    @api.onchange('team')
    def _onchange_team(self):
        if self.team:
            self.team_leader = self.team.team_leader.id
            self.team_members = [(6, 0, self.team.team_members.ids)]
        else:
            self.team_leader = False
            self.team_members = [(5, 0, 0)]
    
    @api.depends('team', 'booking_start', 'booking_end')
    def action_check_booking_order(self):
        
        team = self.team
        booking_start = self.booking_start
        booking_end = self.booking_end
        
        if not team or not booking_start or not booking_end:
            raise UserError(f"Please make sure to select a team and set booking dates")
        
        overlapping_work = self.env['booking_order_farras_arrafi_26092024.work_order'].search([
            ('team', '=', team.id),
            ('state', '=', 'in_progress'),
            ('planned_start', '<=', booking_end),
            ('planned_end', '>=', booking_start)
        ])
        
        overlapping_work_ids = overlapping_work.ids
        overlapping_work_names = self.env['booking_order_farras_arrafi_26092024.work_order'].browse(overlapping_work_ids).mapped('name')
        
        if overlapping_work:
            raise UserError("Team already has work order during that period on {overlapping_work_names}")
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Success',
                'message': 'The selected booking dates are available. You can proceed with saving the record.',
                'sticky': False,
            }
        }
    
    
    
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
    