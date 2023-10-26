from odoo import models, fields, api


class HelpdeskAccessories(models.Model):
    _name = "helpdesk.accessories"
    _description = "Helpdesk Accessories"

    name = fields.Char(string='Accessories Product Name')
    quantity = fields.Integer(string='Received Qty')
    accessories_description = fields.Char(string='Description')
    hekpdesk_accessories_id = fields.Many2one('helpdesk.ticket')