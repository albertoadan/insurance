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
import datetime
from datetime import datetime
from dateutil import parser
from dateutil.relativedelta import relativedelta
  
# Classe Python per la definició de l'objecte que gestiona els recursos "Motius de baixa"
class insurance_cancellation_reason(osv.osv):
    _name = 'insurance.cancellation.reason'
   
    _columns = {
      'name': fields.char('Reason for cancellation',size=60, required=True),
    }
    
    _order = 'name'         # Per veure's ordenats per nom
    _log_access = False     # Doncs no cal auditar les modificacions sobre aquesta taula
    
    _sql_constraints = [
        ('name_unique','unique(name)','The name must be unique!')
    ]   
insurance_cancellation_reason()

# Classe Python per la definició de l'objecte que gestiona els recursos "Pòlisses"

class insurance_policy(osv.osv):
    _name = 'insurance.policy'
    
    # ATENCIÓ
    # Com volem mostrar una pòlissa quan sigui necessari en camps many2one?
    # Només el número (id)? Sembla poca informació... 
    # És més lògic mostrar la concatenació de id + nom assegurança + nom client
    # Per aconseguir-ho tenim diverses possibilitats:
    # Possibilitat 1: Camp de tipus "function" que sigui la concatenació dels 3 camps i que s'anomeni "name"
    # Possibilitat 2: Camp de tipus "funcion" que sigui la concatenació dels 3 camps i que no s'anomeni "name"
    #                 En aquest cas, caldrà _rec_name='nomDelCamp'
    # Possibilitat 3: Implementar el mètode name_get
    # Però... si en un camp many2one sense widget="selection", l'usuari intenta escriure el valor a cercar, 
    # hi ha problemes si no es disposa del camp 'name'. Concretament apareix un error similar a:
    # Invalid field 'name' in domain expression ['&', ('active', '=', 1), ('name', u'ilike', u'1')]
    # Això no passa si el camp many2one té widget="selection", ja que l'usuari no hi pot escriure i només
    # hi ha la possibilitat de desplegar els registres.
    # En el formulari de "sinistres", sembla adequat posar el camp policy_id sense widget="selection" per
    # a què l'usuari hi pugui escriure (fent una cerca sensitiva al text introduït per l'usuari).
    # Conclusió: Introduim el camp 'name' de tipus "function" (suposem que la funció serà "_name_get_fnc")
    # Ho podem fer de dues maneres:
    # Mètode 1, dissenyant el mètode name_get (va bé tenir-lo) i que _name_get_fnc l'utilitzi
    # def name_get(self, cr, uid, ids, context=None):
        # res = []
        # records = self.browse(cr, uid, ids, context)
        # for r in records:
            # res.append((r['id'],str(r.id)+" - "+r.product_id.name+" - "+ r.customer_id.name))
        # return res   
    # def _name_get_fnc(self, cr, uid, ids, prop, unknow_none, context):
        # res = self.name_get(cr, uid, ids, context) 
        # return dict(res)
    # Mètode 2, dissenyant _name_get_fnc sense utilitzar el mètode name_get:
    def _name_get_fnc(self, cr, uid, ids, prop, unknow_none, context):
        res = {}
        records = self.browse(cr, uid, ids, context)
        for r in records:
            res[r.id]=str(r.id)+" - "+r.product_id.name+" - "+ r.customer_id.name
        return res    
        
    def _expiration_date(self, cr, uid, ids, field_name, arg, context):   
        result = {}
        for rec in self.browse(cr, uid, ids, context=context):
            expiration_date=""
            for renovacio in rec.renewal_ids:
                if expiration_date<renovacio.expiration_date:
                    expiration_date=renovacio.expiration_date
                    result[rec.id] = renovacio.expiration_date
                # print 'Expiration:',result[rec.id]
        return result

    def _last_price(self, cr, uid, ids, field_name, arg, context):   
        result = {}
        for rec in self.browse(cr, uid, ids, context=context):
            expiration_date=""
            for renovacio in rec.renewal_ids:
                if expiration_date<renovacio.expiration_date:
                    expiration_date=renovacio.expiration_date
                    result[rec.id] = renovacio.price
                # print 'Last price:',result[rec.id]
        return result
        
    def _is_renewal_editable(self, cr, uid, ids, field_name, arg, context):   #ISIDRE
        result = {}
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.cancellation_date!=False:    # Pregunta per conèixer si el camp conté valor
                # Quan la pòlissa ja està cancel·lada, no es pot modificar
                # També es podria comprovar utilitzant el camp "active"
                result[rec.id]=False
            else:
                expiration_date=''
                for renovacio in rec.renewal_ids:
                    if renovacio.expiration_date>expiration_date:
                        expiration_date = renovacio.expiration_date    
                        paid =renovacio.paid
                # El bucle anterior cerca si la darrera renovació està pagada i ho guarda a "paid"
                # En cas que estigui pagada, podem procedir a la renovació en cas que estem en els 
                # dos darrers mesos abans de la data de venciment:
                if paid==True:
                    result[rec.id]=(datetime.today()+relativedelta(months=2)).strftime('%Y-%m-%d')>=expiration_date
                else:
                    result[rec.id]=True       
        # print 'Renovable?',expiration_date, paid, result[rec.id]
        return result
       
    _columns = {
        'product_id': fields.many2one('product.product','Insurance', required=True, select=1),
        'customer_id': fields.many2one('res.partner', 'Policyholder', required=True, select=1, domain=[('customer','=',True)]),
        'supplier_id': fields.many2one('res.partner', 'Insurance broker',required=True, select=1, domain=[('supplier','=',True)]),
        # Els camps "customer_id" i "supplier_id" porten domini per assegurar que en tota l'aplicació, aquests camps només puguin
        # tenir un determinat tipus de tercer (res.partner) i els corresponents desplegables ja només mostren la informació possible
        'effective_date': fields.date('Effective date', required=True),
        'effective_time': fields.float('Effective hour', required=True),
        'type_expiration': fields.selection([('annual','Annual'),('biannual','Biannual'),('quarterly','Quarterly'),('monthly','Monthly')],
                                            'Type of expiration',required=True),
        'cancellation_date': fields.date('Cancelled date', readonly=True),
        'cancellation_reason_id': fields.many2one('insurance.cancellation.reason','Reason for cancellation'),
        'active': fields.boolean('Active', required=True),
        'renewal_ids':fields.one2many('insurance.policy.renewal','policy_id','Renewals'),
        'claim_ids':fields.one2many('insurance.policy.claim','policy_id','Claims'),
        'expiration_date':fields.function(_expiration_date,type='date',string='Expiration date'),
        # El camp "expiration_date" es necessita per mostrar la data de venciment en la vista tree de pòlisses
        'is_renewal_editable':fields.function(_is_renewal_editable,type='boolean',string='Is renewal editable'),
        # El camp "is_renewal_editable" l'utilitzem per fer de només lectura la graella de renovacions d'una pòlissa
        'name':fields.function(_name_get_fnc,string='Policy',type='char',size=128,store=True),
        # Cal que el camp "name" estigui enregistrat a la BD (store=True)? No, però si ho està, els camps "many2one" 
        # cap a insurance.policy, seran sensitius al text introduït per l'usuari (és a dir, a mida que l'usuari va 
        # escrivint, es mostren únicament els camps que tenen algun tros de cadena coincident amb el què ha escrit l'usuari
        'last_price':fields.function(_last_price,type='float',string='Last price'),
        # El camp "last_price" s'ha cregut convenient afegir-lo i així l'utilitza l'assistent generate_renewals
        # De no existir, el seu càlcul s'hauria d'haver implementat dins l'assistent
    }
    
    _defaults = {
        'active':1,
    }

    # El seguent mètode s'executa en el moment d'enregistrar per primera vegada una pòlissa i, com indicava l'enunciat
    # genera la primera renovació. El preu, com que no és conegut, es deixa a zero... L'usuari el podrà modificar.
    def create (self, cr, uid, values, context=None):
        id = super(insurance_policy,self).create(cr, uid, values, context=context)
        # La instrucció anterior efectua l'enregistrament de la nova assegurança
        # i obtenim l'id, que el necessitem per crear la primera renovació
        valors={}
        valors['policy_id']=id
        valors['effective_date']=values['effective_date']
        # print values['type_expiration']
        if values['type_expiration']=='annual':
            valors['expiration_date']=parser.parse(values['effective_date'])+relativedelta(years=1)
        elif values['type_expiration']=='biannual':
            valors['expiration_date']=parser.parse(values['effective_date'])+relativedelta(months=6)
        elif values['type_expiration']=='quarterly':
            valors['expiration_date']=parser.parse(values['effective_date'])+relativedelta(months=4)
        else:
            valors['expiration_date']=parser.parse(values['effective_date'])+relativedelta(months=1)
        valors['paid']=False
        obj_renewal = self.pool.get("insurance.policy.renewal")
        idr = obj_renewal.create(cr, uid, valors, context=context)
        return id

    # El seguent mètode és per no permetre eliminar cap pòlissa
    def unlink(self, cr, uid, ids, context=None):
        raise osv.except_osv(_('Invalid action !'), _('Is not possible to delete a policy.'))
        return 
    
    # El seguent mètode és per controlar, en el moment d'enregistrar la modificació d'una pòlissa, si s'ha donat de
    # baixa i, en aquest cas, posem el camp "active" a fals.
    def write(self, cr, uid, ids, values, context=None):
        if 'cancellation_reason_id' in values and values['cancellation_reason_id']!=None:
            values['cancellation_date']=datetime.today();
            values['active']=0;
        return super(insurance_policy, self).write(cr, uid, ids, values, context=context)

insurance_policy()

class insurance_policy_renewal(osv.osv):
    _name = 'insurance.policy.renewal'
  
    _columns = {
      'policy_id': fields.many2one('insurance.policy', 'Policy', required=True, ondelete='cascade'),
      'effective_date': fields.date('Effective date', required=True),
      'expiration_date': fields.date('Expiration date', readonly=True),
      'price': fields.float('Price'),
      'text': fields.text('Text'),
      'paid': fields.boolean('Paid?'),
    }

insurance_policy_renewal();
    
class insurance_policy_claim(osv.osv):
    _name = 'insurance.policy.claim'
    
    _columns = {
      'policy_id': fields.many2one('insurance.policy', 'Policy', required=True, ondelete='cascade'),
      'claim_date': fields.date('Claim date', required=True),
      'claim_time': fields.float('Claim time', required=True),
      'text': fields.text('Text', required=True),
      'police_report': fields.boolean('Police report'),
      'amount_lost': fields.float('Amount lost'),
      'amount_paid': fields.float('Amount paid'),
      'photo_ids': fields.one2many('insurance.policy.claim.photo','claim_id','Photos'),
      'product_id': fields.related('policy_id','product_id',type='many2one',relation='product.product', string='Insurance'),
      'customer_id': fields.related('policy_id','customer_id',type='many2one',relation='res.partner', string='Policyholder'),
      # Els camps product_id i customer_id són necessaris per poder mostrar en les vistes "form" i "tree" de sinistres
      # la informació del tipus d'assegurança i el prenedor de l'assegurança
    }

    def _check_amount_lost_positive(self, cr, uid, ids, context=None):
        for claim in self.browse(cr, uid, ids, context=context):
            if claim.amount_lost<0:
                return False
        return True

    def _check_amount_paid_positive(self, cr, uid, ids, context=None):
        for claim in self.browse(cr, uid, ids, context=context):
            if claim.amount_paid<0:
                return False
        return True

    def _check_amount_lost_paid(self, cr, uid, ids, context=None):
        for claim in self.browse(cr, uid, ids, context=context):
            if claim.amount_lost<claim.amount_paid:
                return False
        return True

    def _check_claim_date_expiration(self, cr, uid, ids, context=None):
        for claim in self.browse(cr, uid, ids, context=context):
            if claim.claim_date>claim.policy_id.expiration_date:
                return False
        return True
        
    def _check_claim_date_today(self, cr, uid, ids, context=None):
        for claim in self.browse(cr, uid, ids, context=context):
            if claim.claim_date>datetime.today().strftime("%Y-%m-%d"):
                return False
        return True

        
    _constraints = [
        (_check_amount_lost_positive, 'Error! The amount lost can not be negative', ['amount_lost']),
        (_check_amount_paid_positive, 'Error! The amount paid can not be negative', ['amount_paid']),
        (_check_amount_lost_paid, 'Error! The amount paid can not be greater than amount lost', ['amount_lost','amount_paid']),
        (_check_claim_date_expiration, 'Error! The claim date must be before date expiration', ['claim_date']),
        (_check_claim_date_today, 'Error! The claim date can not be after today', ['claim_date']),
    ]
       
    _order='claim_date desc,claim_time desc'
insurance_policy_claim();

class insurance_policy_claim_photo(osv.osv):
    _name = 'insurance.policy.claim.photo'
    
    _columns = {
        'claim_id': fields.many2one('insurance.policy.claim','Claim', required=True, ondelete='cascade'),
        'description': fields.text('Description'),
        'photo': fields.binary('Photo'),
    }
insurance_policy_claim_photo()
