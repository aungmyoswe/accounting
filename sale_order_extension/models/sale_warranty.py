from odoo import api, models, fields

class DeliveryTeam(models.Model):
	_name = "sale.warranty"

	name = fields.Char("Name")