# -*- coding: utf-8 -*-

import datetime
from datetime import datetime
import pytz
from odoo import models,_


class StockReportXls(models.AbstractModel):
    _name = 'report.export_stockinfo_xls.stock_report_xls.xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def get_warehouse(self, data):
        wh = data.warehouse.mapped('id')
        obj = self.env['stock.warehouse'].search([('id', 'in', wh)])
        l1 = []
        l2 = []
        for j in obj:
            l1.append(j.name)
            l2.append(j.id)
        return l1, l2

    # def get_lines(self, data, warehouse,start_date,end_date):
    #     lines = []
    #     categ_id = data.mapped('id')
    #     # start_date = datetime.strptime(start_date, '%Y-%m-%d').strftime('%Y-%m-%d 00:00:00')
    #     # end_date = datetime.strptime(end_date, '%Y-%m-%d').strftime('%Y-%m-%d 00:00:00')
    #     # start_date =  datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')
    #     # end_date =  datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S')
    #     # print("Date",start_date,end_date)
    def get_lines(self, data, warehouse):
        lines = []
        categ_id = data.mapped('id')
        if categ_id:
            stock_history = self.env['product.product'].search([('categ_id', 'in', categ_id)],order="categ_id asc")
        for obj in stock_history:
            sale_value = 0
            purchase_value = 0
            product = self.env['product.product'].browse(obj.id)
            sale_obj = self.env['sale.order.line'].search([('order_id.state', 'in', ('sale', 'done')),
                                                           ('product_id', '=', product.id),
                                                           ('order_id.warehouse_id', '=', warehouse)])
            for i in sale_obj:
                sale_value = sale_value + i.product_uom_qty
            purchase_obj = self.env['purchase.order.line'].search([('order_id.state', 'in', ('purchase', 'done')),
                                                                   ('product_id', '=', product.id),
                                                                   ('order_id.picking_type_id', '=', warehouse)])
            for i in purchase_obj:
                purchase_value = purchase_value + i.product_qty
            available_qty = product.with_context({'warehouse': warehouse}).virtual_available + \
                            product.with_context({'warehouse': warehouse}).outgoing_qty - \
                            product.with_context({'warehouse': warehouse}).incoming_qty
            value = available_qty * product.standard_price
            vals = {
                'name': product.name,
                'category': product.categ_id.name,
                'net_on_hand': product.with_context({'warehouse': warehouse}).qty_available,
            }
            lines.append(vals)
        return lines

    def generate_xlsx_report(self, workbook, data, lines):
        d = lines.category
        get_warehouse = self.get_warehouse(lines)
        count = len(get_warehouse[0]) * 11 + 6
        comp = self.env.user.company_id.name
        # s = data['form']['start_date']
        # e = data['form']['end_date']
        location = data['form']['stock_location']
        y_offset = 0
        date = datetime.today().date()
        date = datetime.strptime(str(date), '%Y-%m-%d').date().strftime("%d-%m-%Y")
        print ("Date",date)
        sheet = workbook.add_worksheet('Inventory Report')
        format0 = workbook.add_format({ 'bold': True,'align': 'center','font_size': 14,})
        format1 = workbook.add_format({'bold': True,'bg_color': '#FFFFCC','border': True,'align': 'left'})
        format2 = workbook.add_format({'border': True,'align': 'left',})
        format5 = workbook.add_format({'align': 'left','bold': True,})
        format3 = workbook.add_format({'align': 'center','bold': True,'border': True,})
        format4 = workbook.add_format({'border': True,'align': 'left'})
        font_size_8 = workbook.add_format({'border': True,'align': 'center'})
        red_mark = workbook.add_format({'font_size': 8, 'bg_color': 'red'})
        justify = workbook.add_format({'font_size': 12})
        sheet.set_column('A:A',30)
        sheet.set_column('B:B',30)
        sheet.merge_range(y_offset, 0, y_offset, 1, _('Inventory On Hand Report'), format0)
        y_offset += 2
        company_name = warehouse_name = location_name ='' 
        com=data['form']['company_id']
        #Company Parameter 
        if com:            
            for company in self.env['res.company'].browse(com).name_get():
                company_name += str(company[1]) + ','
            company_name = company_name[:-1]    
        else:
            company_name = 'All' 
        #Warehouse Parameter 
        warehouse_id=data['form']['warehouse']
        if warehouse_id:            
            for warehouse in self.env['stock.warehouse'].browse(warehouse_id).name_get():
                warehouse_name += str(warehouse[1]) + ','
            warehouse_name = warehouse_name[:-1]    
        else:
            warehouse_name = 'All'
        if location:            
            for loct in self.env['stock.location'].browse(location).name_get():
                location_name += str(loct[1]) + ','
            location_name = location_name[:-1]    
        else:
            location_name = "All"
        df = _('From') + ': '
        df += data['form']['start_date'] if data['form']['start_date'] else u''
        df += ' ' + _('To') + ': '
        df += data['form']['end_date'] if data['form']['end_date'] else u''
        sheet.write(y_offset, 0, _('Company'), format1)
        sheet.write(y_offset, 1, company_name or '', format2)
        y_offset += 1
        sheet.write(y_offset, 0, _('Warehouse'), format1)
        sheet.write(y_offset, 1,warehouse_name or '', format2)
        y_offset += 1
        sheet.write(y_offset, 0, _('Location'), format1)
        sheet.write(y_offset, 1, location_name or '', format2)
        y_offset += 1
        sheet.write(y_offset, 0, _('Sort By'), format1)
        sheet.write(y_offset, 1, data['form']['type_id'] or '', format2)          
        y_offset += 1  
        sheet.write(y_offset, 0, _('Date'), format1)
        sheet.write(y_offset, 1, str(date)or '', format2)          
        y_offset += 2                  
        sheet.write(9, 0, 'Product', format3)
        sheet.write(9, 1, 'On Hand', format3)
        for cat in get_warehouse[1]:
            line = self.get_lines(d, cat)
            y_offset = 10
            prod_col= 0
            parent_id=[]
            categ_ids = 0
            i = 0
            name = None
            path = None
            categ_name=[]
            product = []
            for each in line:
                cats = self.env['product.category'].search([('name','=',each['category'])])
                parent_path = cats.parent_path
                categ_ids = parent_path.split("/")
                for loop in [categ_ids]:
                    categs = self.env['product.category'].search([('id','=',loop[i+1])])
                    if name!=categs.name:
                        parent_id = categs.parent_id.id
                        y_offset +=1
                        while (parent_id!=None):
                            categ = self.env['product.category'].search([('id','=',parent_id)])
                            if categ.parent_id:
                                categ_name.append(categ)
                                parent_id = categ.parent_id.id
                            else:
                                categ_name.append(categ)
                                parent_id = None
                        n = 0
                        for loop in [categ_name]:
                            sheet.write(y_offset, 0,  loop[i].name, format5)
                            y_offset += 1
                        sheet.write(y_offset, 0, categs.name, format5)
                        y_offset += 1
                        if cats.name != categs.name:
                            sheet.write(y_offset, 0, cats.name, format5)
                            y_offset += 1
                    name=categs.name
                if each['name'] not in product:
                    sheet.write(y_offset, prod_col, each['name'], format4)
                    if each['net_on_hand'] < 0:
                        sheet.write(y_offset, 1, each['net_on_hand'], red_mark)
                        y_offset = y_offset + 1
                    else:
                        sheet.write(y_offset, 1, each['net_on_hand'], font_size_8)
                        y_offset = y_offset + 1
                product.append(each['name'])
            y_offset = 10
            prod_col = prod_col + 11