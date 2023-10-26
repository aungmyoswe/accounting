from odoo import api, fields, models

class ProductBrand(models.Model):
    _name = 'product.brand'
    _description = "Product Brand"
    _order = 'name'

    name = fields.Char('Brand Name', required=True)
    description = fields.Text(translate=True)
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
        help='Select a partner for this brand if any.',
        ondelete='restrict'
    )
    logo = fields.Binary('Logo File')
    product_ids = fields.One2many(
        'product.template',
        'product_brand_id',
        string='Brand Products',
    )
    products_count = fields.Integer(
        string='Number of products',
        compute='_compute_products_count',
    )

    @api.multi
    @api.depends('product_ids')
    def _compute_products_count(self):
        for brand in self:
            brand.products_count = len(brand.product_ids)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    product_brand_id = fields.Many2one(
        'product.brand',
        string='Brand',
        help='Select a brand for this product'
    )

#class PosOrderLine(models.Model):
#    _inherit = "pos.order.line"
#
#    brand_id = fields.Many2one('product.brand', "Brand", store=True)
#
#    @api.model
#    def create(self, values):
#        if values.get('order_id') and not values.get('name'):
#            # set name based on the sequence specified on the config
#            config_id = self.order_id.browse(values['order_id']).session_id.config_id.id
#            # HACK: sequence created in the same transaction as the config
#            # cf TODO master is pos.config create
#            # remove me saas-15
#            self.env.cr.execute("""
#                SELECT s.id
#                FROM ir_sequence s
#                JOIN pos_config c
#                  ON s.create_date=c.create_date
#                WHERE c.id = %s
#                  AND s.code = 'pos.order.line'
#                LIMIT 1
#                """, (config_id,))
#            sequence = self.env.cr.fetchone()
#            if sequence:
#                values['name'] = self.env['ir.sequence'].browse(sequence[0])._next()
#        if not values.get('name'):
#            # fallback on any pos.order sequence
#            values['name'] = self.env['ir.sequence'].next_by_code('pos.order.line')
#        product_id = values['product_id']
#        tmpl_id = self.env['product.template'].browse(product_id)
#        if tmpl_id:
#            values['brand_id'] = tmpl_id.product_brand_id.id
#        return super(PosOrderLine, self).create(values)