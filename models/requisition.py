from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.osv import expression
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_compare
from odoo.exceptions import UserError, AccessError
from odoo.tools.misc import formatLang
from odoo.addons import decimal_precision as dp


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    requisition_number = fields.Char('PO Requisition')


class Requisition(models.Model):
    _name = "po.requisition"

    name = fields.Char('PO Requisition')
    warehouse_id = fields.Many2one(
        'stock.warehouse', string='Warehouse', required=True)
    delivery_date = fields.Datetime(
        string='Delivery Date', required=True, index=True)
    po_reference = fields.Many2one('purchase.order', string='PO Reference')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approve', 'Approve'),
        ('cancel', 'Cancelled')
    ], string='Status', readonly=True, index=True, copy=False, default='draft', track_visibility='onchange')
    partner_id = fields.Many2one('res.partner', string='Vendor', required=True,
                                 help="You can find a vendor by its Name, TIN, Email or Internal Reference.")
    order_line = fields.One2many('requisition.order.line', 'order_id', string='Order Lines', states={
                                 'cancel': [('readonly', True)], 'done': [('readonly', True)]}, copy=True)

    @api.multi
    def action_approve_po_requisition(self):

        po_data = {
            'requisition_number': str(self.name),
            'date_order': fields.datetime.now(),
            'partner_id': self.partner_id.id,

        }

        po_line_list = list()

        for line_item in self.order_line:
            po_line_list.append([0, False,
                                 {
                                     'name': line_item.product_id.product_tmpl_id.name,
                                     'product_id': line_item.product_id.id,
                                     'product_qty': line_item.product_qty,
                                     'product_uom': line_item.product_uom.id,
                                     'date_planned': fields.datetime.now(),
                                     'price_unit': line_item.product_id.price,
                                 }])

        po_data['order_line'] = po_line_list

        # create PO
        po_env = self.env['purchase.order'].create(po_data)
        saved_po_id = po_env.create(po_data)
        import pdb;pdb.set_trace()
        # po_env = self.pool.get('purchase.order')
        # saved_po_id = po_env.create(self._cr, self._uid, po_data, context=self._context)

        # Update PO Reference and state
        req_update_query = "UPDATE po_requisition SET po_reference={0}, state='approve' WHERE id={1}".format(
            saved_po_id, self.id)
        self._cr.execute(req_update_query)
        self._cr.commit()

        return True

    @api.model
    def create(self, values):
        record = super(Requisition, self).create(values)

        # Odoo Error, a partner cannot follow twice the same object
        subtype_ids = self.env['mail.message.subtype'].search([('res_model', '=', 'po.requisition')]).ids
        record.message_subscribe(partner_ids=[record.partner_id.id],subtype_ids=subtype_ids)

        record.name = "REQ0"+str(record.id)

        return record


class RequisitionOrderLine(models.Model):
    _name = 'requisition.order.line'
    _description = 'Requisition Order Line'

    order_id = fields.Many2one(
        'po.requisition', string='Order Reference', index=True, required=True, ondelete='cascade')
    name = fields.Text(string='Description')
    product_id = fields.Many2one('product.product', string='Product', domain=[
                                 ('purchase_ok', '=', True)], change_default=True, required=True)
    product_qty = fields.Float(string='Quantity', digits=dp.get_precision(
        'Product Unit of Measure'), required=True)

    product_uom = fields.Many2one(
        'uom.uom', string='Product Unit of Measure', required=True)
    price_unit = fields.Float(string='Price', digits=dp.get_precision(
        'Product Price'))
