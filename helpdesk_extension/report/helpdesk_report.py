from odoo import models, api

class HelpdeskTicketReport(models.AbstractModel):
    _name = 'report.helpdesk_extension.service_ticket_report'

    @api.multi
    def _get_report_values(self, docids, data=None):
        docs = self.env['helpdesk.ticket'].browse(docids)
        print (docs,"DOCS")
        return {
            'doc_ids': docs.ids,
            'doc_model': 'helpdesk.ticket',
            'docs': docs,
        }