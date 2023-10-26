from odoo import api, models, fields

class SaleOrder(models.Model):
    _inherit = "sale.order"
    
    delivery_term = fields.Many2one("delivery.term","Delivery Terms", store=True)
    date_of_delivery = fields.Many2one("date.of.delivery","Date of Delivery", store=True)
    sale_validity = fields.Many2one("sale.validity","Validity Name", store=True)
    sale_warranty = fields.Many2one("sale.warranty","Warranty", store=True)