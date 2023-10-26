from odoo import api, models, fields

class DeliveryTeam(models.Model):
	_name = "date.of.delivery"

	name = fields.Char("Name")