
from odoo import api, fields, models

class Inventory(models.Model):
    _inherit = "stock.inventory"

    remark = fields.Text("Remark")