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
        # Set booking order to True
        vals['is_booking_order'] = True
            # Call super
        return super(SaleOrder, self).create(vals)
    
    def check_availability(self):
        team = self.team
        booking_start = self.booking_start
        booking_end = self.booking_end
        
        if not team or not booking_start or not booking_end:
            raise UserError(f"Please make sure to select a team and set booking dates")
        
        overlapping_work = self.env['booking_order_farras_arrafi_26092024.work_order'].search([
            ('team', '=', team.id),
            ('state', '!=', 'cancel'),
            ('planned_start', '<=', booking_end),
            ('planned_end', '>=', booking_start)
        ])
        
        overlapping_work_ids = overlapping_work.ids
        overlapping_work_names = self.env['booking_order_farras_arrafi_26092024.work_order'].browse(overlapping_work_ids).mapped('name')
        
        if overlapping_work:
            raise UserError(f"Team already has work order during that period on {overlapping_work_names}")
        
        return True
    
    @api.model
    def action_confirm(self):
        if self.check_availability():
            res = super(SaleOrder, self).action_confirm()
            
            work_order = self.env['booking_order_farras_arrafi_26092024.work_order'].create({
                'team': self.team.id,
                'team_leader': self.team_leader.id,
                'team_members': [(6, 0, self.team_members.ids)],
                'planned_start': self.booking_start,
                'planned_end': self.booking_end,
                'state': 'pending',
                'booking_order_reference': self.id,  # set booking reference directly
            })
            
            return res
    
    @api.onchange('team')
    def _onchange_team(self):
        if self.team:
            self.team_leader = self.team.team_leader.id
            self.team_members = [(6, 0, self.team.team_members.ids)]
        else:
            self.team_leader = False
            self.team_members = [(5, 0, 0)]
    
    def action_check_booking_order(self):
        
        if self.check_availability():
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Success',
                    'message': 'The selected booking dates are available. You can proceed with saving the record.',
                    'sticky': False,
                }
            }
            
    def action_view_related_work_order(self):
        # Find the related work order based on booking_order_reference
        work_orders = self.env['booking_order_farras_arrafi_26092024.work_order'].search([('booking_order_reference', '=', self.id)])

        if not work_orders:
            raise UserError("No Work Order found for this Sale Order.")

        # Return an action to open the form view of the work order
        return {
            'type': 'ir.actions.act_window',
            'name': 'Work Order',
            'view_mode': 'form',
            'res_model': 'booking_order_farras_arrafi_26092024.work_order',
            'res_id': work_orders.id,  # assuming there is only one related work order
            'target': 'current',
        }
    
    
    
class WorkOrder(models.Model):
    
    # Model info 
    _name = 'booking_order_farras_arrafi_26092024.work_order'
    _description = 'Work Order'
    
    name = fields.Char("WO Number", required=True, readonly=True, copy=False, default='New')
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
        ('cancel', 'Cancelled'),
    ], string='Status', default='pending', readonly=True)
    
    notes = fields.Text('Notes')
    
    @api.model
    def create(self, vals):
        # If the name is still 'New', generate a sequence number
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('work_order_seq') or 'WO00000'
        return super(WorkOrder, self).create(vals)
    
    def action_start(self):
        self.write({
            'state': 'in_progress',
            'date_start': fields.Datetime.now()
        })
        
    def action_done(self):
        self.write({
            'state': 'done',
            'date_end': fields.Datetime.now()
        })
    
    def action_reset(self):
        self.write({
            'state': 'pending',
            'date_start': False,
        })
        
    def action_cancel_wizard(self):
        return {
            'name': 'Cancel Work Order',
            'type': 'ir.actions.act_window',
            'res_model': 'booking_order_farras_arrafi_26092024.work_order.cancel_wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'active_id': self.id}
        }
        
    def print_work_order(self):
        return self.env.ref('booking_order_farras_arrafi_26092024.action_report_work_order').report_action(self)
        
    
class WorkOrderCancelWizard(models.TransientModel):
    _name = 'booking_order_farras_arrafi_26092024.work_order.cancel_wizard'

    reason = fields.Text(string='Cancellation Reason', required=True)
    
    def action_cancel(self):
        active_id = self.env.context.get('active_id')
        if active_id:
            work_order = self.env['booking_order_farras_arrafi_26092024.work_order'].browse(active_id)
            work_order.write({
                'state': 'cancel',
                'notes': self.reason,
            })
            
            return True
        
        
    