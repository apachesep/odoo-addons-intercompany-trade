# -*- encoding: utf-8 -*-
##############################################################################
#
#    Integrated Trade - Purchase module for OpenERP
#    Copyright (C) 2015-Today GRAP (http://www.grap.coop)
#    @author Sylvain LE GAL (https://twitter.com/legalsylvain)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields
from openerp.osv.orm import Model
from openerp.osv.osv import except_osv
from openerp.tools.translate import _

from openerp.addons.integrated_trade_product.model.custom_tools\
    import _get_other_product_info


class purchase_order_line(Model):
    _inherit = 'purchase.order.line'

    # Columns Section
    _columns = {
        'integrated_trade': fields.related(
            'order_id', 'integrated_trade', type='boolean',
            string='Integrated Trade'),
        'integrated_trade_sale_order_line_id': fields.many2one(
            'sale.order.line', string='Integrated Trade Sale Order Line',
            readonly=True,
        ),
    }

    # Overload Section
    def create(self, cr, uid, vals, context=None):
        """Create the according Sale Order Line."""
        print "**** vals"
        print vals
        context = context and context or {}

        rit_obj = self.pool['res.integrated.trade']
        po_obj = self.pool['purchase.order']
        sol_obj = self.pool['sale.order.line']

        po = po_obj.browse(cr, uid, vals['order_id'], context=context)
        create_sale_order_line = (
            not context.get('integrated_trade_do_not_propagate', False) and
            po.integrated_trade)

        # Call Super: Create
        res = super(purchase_order_line, self).create(
            cr, uid, vals, context=context)

        if create_sale_order_line:
            ctx = context.copy()
            ctx['integrated_trade_do_not_propagate'] = True

            rit = rit_obj._get_integrated_trade_by_partner_company(
                cr, uid, po.partner_id.id, po.company_id.id, 'in',
                context=context)

            pol = self.browse(cr, uid, res, context=context)

            # Create associated Sale Order Line
            other_product_info = _get_other_product_info(
                self.pool, cr, uid, rit, vals['product_id'], 'in',
                context=context)

            sol_vals = sol_obj.product_id_change(
                cr, rit.supplier_user_id.id, False, rit.pricelist_id.id,
                other_product_info['product_id'], qty=vals['product_qty'],
            uom=vals['product_uom'], partner_id=rit.customer_partner_id.id,
            context=context)['value']

            sol_vals.update({
                'order_id': pol.order_id.integrated_trade_sale_order_id.id,
                'product_id': other_product_info['product_id'],
                'delay': 0,
                'discount': 0,
                'tax_id': [[
                    6, False, sol_vals['tax_id']]],
                    'product_uom_qty': sol_vals['product_uos_qty'],
                    'product_uom': sol_vals['product_uos'],
            })
            sol_id = sol_obj.create(
                cr, rit.supplier_user_id.id, sol_vals, context=ctx)

            # Update associated Sale Order Line to Force the call of the
            # the function '_amount_all'
            sol_obj.write(
                cr, rit.supplier_user_id.id, sol_id, {
                    'integrated_trade_purchase_order_line_id': pol.id,
                    'price_unit': other_product_info['price_unit'],
                }, context=ctx)

            # Update Purchase Order line with Sale Order Line id created
            self.write(cr, uid, res, {
                'integrated_trade_sale_order_line_id': sol_id,
                'price_unit': other_product_info['price_unit'],
            }, context=ctx)
        return res

    def write(self, cr, uid, ids, vals, context=None):
        """"- Update the according Sale Order Line with new data.
            - Block any changes of product."""
        print "write ******"
        print vals
        context = context and context or {}
        sol_obj = self.pool['sale.order.line']
        rit_obj = self.pool['res.integrated.trade']

        res = super(purchase_order_line, self).write(
            cr, uid, ids, vals, context=context)

        if not context.get('integrated_trade_do_not_propagate', False):
            ctx = context.copy()
            ctx['integrated_trade_do_not_propagate'] = True
            for pol in self.browse(cr, uid, ids, context=context):
                if pol.integrated_trade_sale_order_line_id:
                    rit = rit_obj._get_integrated_trade_by_partner_company(
                        cr, uid, pol.order_id.partner_id.id,
                        pol.order_id.company_id.id, 'in', context=context)
                    sol_vals = {}

                    if 'product_id' in vals.keys():
                        raise except_osv(
                            _("Error!"),
                            _("""You can not change the product. %s"""
                                """Please remove this line and choose a"""
                                """ a new one.""" % (pol.product_id.name)))
                    if 'product_uom' in vals.keys():
                        raise except_osv(
                            _("Error!"),
                            _("""You can not change the UoM of the Product"""
                                """ %s.""" % (pol.product_id.name)))
                    if 'price_unit' in vals.keys():
                        raise except_osv(
                            _("Error!"),
                            _("""You can not change the Price for"""
                                """ the product '%s'."""
                                """ Please ask to your supplier.""" % (
                                    pol.product_id.name)))
                    if 'product_qty' in vals:
                        sol_vals['product_uos_qty'] = pol.product_qty
                        sol_vals['product_uom_qty'] = pol.product_qty
                    # TODO Manage discount / delay / tax
                    sol_obj.write(
                        cr, rit.supplier_user_id.id,
                        pol.integrated_trade_sale_order_line_id.id,
                        sol_vals, context=ctx)
        return res

    def unlink(self, cr, uid, ids, context=None):
        """"- Unlink the according Sale Order Line."""
        if not context:
            context = {}
        sol_obj = self.pool['sale.order.line']
        rit_obj = self.pool['res.integrated.trade']
        if 'integrated_trade_do_not_propagate' not in context.keys():
            ctx = context.copy()
            ctx['integrated_trade_do_not_propagate'] = True
            for pol in self.browse(cr, uid, ids, context=context):
                rit = rit_obj._get_integrated_trade_by_partner_company(
                    cr, uid, pol.order_id.partner_id.id,
                    pol.order_id.company_id.id, 'in', context=context)
                sol_obj.unlink(
                    cr, rit.supplier_user_id.id,
                    [pol.integrated_trade_sale_order_line_id.id],
                    context=ctx)
        res = super(purchase_order_line, self).unlink(
            cr, uid, ids, context=context)
        return res
