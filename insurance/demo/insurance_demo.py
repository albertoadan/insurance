##############################################################################
#
# Copyright (c) 2014 Institut Obert de Catalunya (http://ioc.xtec.cat) 
#                    All Rights Reserved.
#                    Author: Isidre Guixà <iguixa@xtec.cat>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.related
#
##############################################################################

from osv import osv, fields

class insurance_policy_renewal(osv.osv):
    _name = 'insurance.policy.renewal'
    _inherit = 'insurance.policy.renewal'
  
    def set_price_paid_data_demo(self, cr, uid, ids, *args):
        # print args
        # Es suposa que args[0] conté el diccionari {'price':..., 'paid':...}
        self.write(cr, uid, ids, args[0])
        return True
        
insurance_policy_renewal();
    
