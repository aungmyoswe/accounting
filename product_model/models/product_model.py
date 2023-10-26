from odoo import api, fields, models


class ProductModel(models.Model):
    _name = 'product.model'
    _description = "Product model"
    _order = 'name'

    name = fields.Char('Model Name', required=True)
    description = fields.Text(translate=True)

    logo = fields.Binary('Logo File')
    product_ids = fields.One2many(
        'product.template',
        'product_model_id',
        string='Model Products',
    )
    products_count = fields.Integer(
        string='Number of products',
        compute='_compute_products_count',
    )

    @api.multi
    @api.depends('product_ids')
    def _compute_products_count(self):
        for model in self:
            model.products_count = len(model.product_ids)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    product_model_id = fields.Many2one('product.model', string='Model', help='Select a model for this product')
