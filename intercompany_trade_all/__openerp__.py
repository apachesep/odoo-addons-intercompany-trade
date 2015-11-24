# -*- encoding: utf-8 -*-
##############################################################################
#
#    Intercompany Trade - ALL module for OpenERP
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
{
    'name': 'Intercompany Trade - ALL',
    'version': '1.0',
    'category': 'Intercompany Trade',
    'description': """
Module for Intercompany Trade
===========================

Copyright, Authors and Licence:
-------------------------------
    * Copyright: 2015, GRAP: Groupement Régional Alimentaire de Proximité;
    * Author:
        * Sylvain LE GAL (https://twitter.com/legalsylvain);
    * Licence: AGPL-3 (http://www.gnu.org/licenses/);""",
    'author': 'GRAP',
    'website': 'http://www.grap.coop',
    'license': 'AGPL-3',
    'depends': [
        'intercompany_trade_account',
        'intercompany_trade_base',
        'intercompany_trade_fiscal_company',
        'intercompany_trade_product',
        'intercompany_trade_purchase_discount',
        'intercompany_trade_purchase_order_reorder_lines',
        'intercompany_trade_purchase_package_qty',
        'intercompany_trade_purchase_sale',
        'intercompany_trade_sale_margin',
        'intercompany_trade_sale_order_dates',
        'intercompany_trade_stock',
    ],
}
