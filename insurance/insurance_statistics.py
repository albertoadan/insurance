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
from tools.translate import _

class insurance_statistics(osv.osv):
    _name = 'insurance.statistics'
    _description = 'Statistics on insurance'
    _auto = False
    _columns = {
        'name': fields.char('Insurance', size=64, readonly=True),
        'policy_nbr': fields.integer('# of policies', readonly=True),
        'claim_nbr': fields.integer('# of claims',readonly=True),
        'ratio': fields.float('Ratio claims/policies', readonly=True),
    }
    _order = 'ratio desc'
   
    def init(self, cr):
      cr.execute("""
        create or replace view insurance_statistics as (
          select
            pro.id as id,
            pro.name_template as name,
            count(distinct ip.id) as policy_nbr,
            count(ipc.id) as claim_nbr,
            1.*count(ipc.id)/count(distinct ip.id)*100 as ratio
          from product_product pro join insurance_policy ip
                                   on ip.product_id = pro.id
                                   left join insurance_policy_claim ipc
                                   on ipc.policy_id = ip.id
          group by pro.id, pro.name_template
          order by ratio desc
        )
      """)  
    # Com que el join entre product_product i insurance_policy és un "inner join", ja només agafem
    # els productes que tenen alguna pòlissa; la resta no té sentit agafar-los.
    # El join entre insurance_policy i insurance_policy_claim ha de ser "left join" per assegurar que
    # s'agafin les pòlisses per les que encara no hi hagi cap sinistre.
insurance_statistics()
