from odoo import api, fields, models, tools

class PosOrderReport(models.Model):
    _inherit = "report.pos.order"

    product_brand_id = fields.Many2one("product.brand", "Brand", readonly=True)

    def _select(self):
        select_str = super()._select()
        select_str += """
            , pt.product_brand_id as product_brand_id
            """
        return select_str


    def _group_by(self):
        group_by_str = super()._group_by()
        group_by_str += ", pt.product_brand_id"
        return group_by_str           