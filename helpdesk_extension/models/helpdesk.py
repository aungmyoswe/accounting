from odoo import models, fields, api
from datetime import date


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    partner_id = fields.Many2one('res.partner', string='Customer',domain=[('customer','=',True)],store=True)
    partner_name = fields.Char(string='Customer Name',store=True)
    name = fields.Char(string='New', default="New", readonly=True, index=True)
    phone = fields.Char('Phone Number', store=True, requried=True)
    name = fields.Char(string='New', default="New", readonly=True, index=True)
    date_receive = fields.Date(string='Received Date', required=True)
    date_request = fields.Date(string='Request Date', required=True)
    document_id = fields.Char('Source Document', store=True, required=True)
    selection = fields.Selection([('warranty', 'Warranty'), ('no_warranty', 'No Warranty'), ('repair', 'Repair'), ('service', 'Service')],string='Type')
    product = fields.Char(string='Product Name', store=True, required=True)
    brand = fields.Char(string='Product Brand', store=True, required=True)
    model = fields.Char(string='Product Model', store=True, required=True)
    serial_number = fields.Char(string='Serieal Number', store=True, required=True)
    add_note = fields.Text(string='Add Note')
    description = fields.Text(string='Complain Description')
    case = fields.Text(string='Finding Case')
    helpdesk_ticket_id = fields.One2many('helpdesk.accessories','hekpdesk_accessories_id', string='Accessories Information')
    service_number = fields.Integer(compute='_compute_service_number', string="Number of Service")
    partner_email = fields.Char(string='Customer Email', required=False)

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id:
            self.partner_email = self.partner_id.email
            self.partner_name = self.partner_id.contact_name
            self.phone = self.partner_id.phone


    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('helpdesk.ticket')
        return super(HelpdeskTicket, self).create(vals)