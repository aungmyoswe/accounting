# -*- coding: utf-8 -*-
import time
from datetime import datetime
from odoo import models, fields, api
from dateutil import parser
from dateutil.relativedelta import relativedelta



from datetime import datetime, timedelta


class StockReport(models.TransientModel):
    _name = "wizard.stock.history"
    _description = "Current Stock History"

    company_id = fields.Many2one('res.company', string='Company',default=lambda self: self.env.user.company_id)
    warehouse = fields.Many2many('stock.warehouse', 'wh_wiz_rel', 'wh', 'wiz', string='Warehouse', required=True)
    category = fields.Many2many('product.category', 'categ_wiz_rel', 'categ', 'wiz', string='Category"')
    product_id = fields.Many2many('product.product', 'product_wiz_rel', 'prod','wiz',string="Warehouse")
    stock_location = fields.Many2one('stock.location', string="Location", store=True)
    type_id = fields.Selection([('warehouse', 'Warehouse'), ('category', 'Product Category')], 'Group By', required=True, default='category')
    start_date = fields.Date('Beginning Date', required=True, default= lambda *a:(parser.parse(datetime.now().strftime('%Y-%m-%d')) + relativedelta(days=-1)).strftime('%Y-%m-%d'))
    end_date = fields.Date('End Date', required=True, default= lambda *a :  time.strftime('%Y-%m-%d'))

    @api.multi
    def export_xls(self):
        context = self._context
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'wizard.stock.history'
        datas['form'] = self.read()[0]
        for field in datas['form'].keys():
            if isinstance(datas['form'][field], tuple):
                datas['form'][field] = datas['form'][field][0]
        if context.get('xls_export'):
            return self.env.ref('export_stockinfo_xls.stock_xlsx').report_action(self, data=datas)
