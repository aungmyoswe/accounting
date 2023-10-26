from odoo import api, models, fields

class DeliveryTeam(models.Model):
	_name = "sale.validity"

	name = fields.Char("Name")