from openerp.osv import osv, fields
import datetime
from openerp import netsvc
from openerp import tools
import time

class client(osv.Model):
    _inherit='res.partner'
    _columns={
              'vehicle_ids':fields.one2many('autorepair.vehicle','client_id',string="Vehicle Owner"),
        }


class vehicle(osv.Model):
    _name='autorepair.vehicle'

    _columns={
              'register': fields.char(string="Register Number",size=20,required=True),
              'client_id':fields.many2one('res.partner',required=True,domain="[('customer','=',True)]",string="Client"),
              'brand':fields.char(size=40,required=False,string="Brand"),
              'model':fields.char(size=40,required=False,string="Model"),
              'color':fields.char(size=10,required=False,string="Color"),
              'repair_ids':fields.one2many('autorepair.repair','vehicle_id',string="Repair Realized"),

            }
    _rec_name='register'
    _sql_constraints = [
        ('reference_register_unique',
        'UNIQUE(register)',
        'The register number already exist ')
     ]
    _order="register,client_id"


class repair(osv.Model):
    _name='autorepair.repair'
    
    def action_checkin(self, cr, uid, ids, context={}):
        return self.write(cr, uid, ids, {'state': 'checkin'}, context=context)
    
    def action_checkup(self, cr, uid, ids, context={}):
        return self.write(cr, uid, ids, {'state': 'checkup'}, context=context)
    
    def action_repair(self, cr, uid, ids, context={}):
        return self.write(cr, uid, ids, {'state': 'repair'}, context=context)
    
    def action_checkout(self, cr, uid, ids, context={}):
        return self.write(cr, uid, ids, {'state': 'checkout', 'out_date':time.strftime('%Y-%m-%d %H:%M:%S')}, context=context)
    
    def _amount(self, cr, uid, ids, field_name, arg, context=None):
        res= {}
        for repair in self.browse(cr, uid, ids, context=context):
            total = 0.0
            for detail in repair.detail_repair_ids:
                total += detail.units * detail.price
            res[repair.id] = total
        return res
    
    
    _columns={
              'repair_num': fields.char(string="Repair Number",required=True,readonly=True),
              'description':fields.text(string="Description",required=True),
              'vehicle_id':fields.many2one('autorepair.vehicle',required=True, string="Vehicle"),
              'in_date':fields.datetime(string="Check In",readonly=True),
              'out_date':fields.datetime(string="Check Out",readonly=True),
              'client_id':fields.related('vehicle_id','client_id',readonly=True,type='many2one',relation='res.partner',string="Client",store=True),
              'detail_repair_ids':fields.one2many('autorepair.detail_repair','repair_id',string="Detail Repair"),
              'total': fields.function(_amount, string='Total',store=True),
              'state': fields.selection([('checkin','Check In'),('checkup','Check Up'),('repair','Repair'),('checkout','Check Out')], string="State"),
              'color': fields.integer('Color'),
              }
    _rec_name='repair_num'
    _defaults={
        'state':'checkin',
        'in_date':time.strftime('%Y-%m-%d %H:%M:%S'),
        'out_date':False,
        'repair_num':lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid,'autorepair.repair'),

        }
    def onchange_vehicle_id(self, cr, uid, ids, vehicle_id,context={}):
        data = {'client_id': False}
        if vehicle_id:
            vehicle = self.pool.get('autorepair.vehicle').browse(cr, uid, vehicle_id, context)
            data.update({'client_id': vehicle.client_id.id})
        return {'value': data}
                


    
    def _check_dates(self, cr, uid, ids, context={}):
        for repair in self.browse(cr, uid, ids, context=context):
            if repair.out_date:
                if repair.out_date<repair.in_date:
                    return False
        return True

    _constraints = [
       
        (_check_dates,'Check out less than check in',['in_date','out_date']
         )      
    ]
    
    _sql_constraints = [
        ('repair_num_unique',
        'UNIQUE(repair_num)',
        'The repair number already exist ')
     ]
    _order="in_date"

class detail_repair(osv.Model):
    _name='autorepair.detail_repair'

    def create(self, cr, uid, vals, context=None):
        
        new_detail= super(detail_repair, self).create(cr, uid, vals, context=context)
        part_obj=self.pool.get('autorepair.part')
        part=part_obj.search(cr, uid,[('id','=',vals['part_id'])])
        for parts  in part_obj.browse(cr,uid,part):
            upd_part=part_obj.write(cr,uid,vals['part_id'],{
               'stock': parts.stock-vals['units']
            },context=context)
        return new_detail  
        
    def write(self, cr, uid,ids, vals, context=None):
        
        upd_detail= super(detail_repair, self).write(cr, uid,ids,vals, context=context)
        part_obj=self.pool.get('autorepair.part')
        
        for details in  self.browse(cr,uid,ids,context=context):
            part=part_obj.search(cr, uid,[('id','=',details.part_id.id)])
            for parts  in part_obj.browse(cr,uid,part):
                upd_part=part_obj.write(cr,uid,parts.id,{
                         'stock': parts.stock-vals['units']
            },context=context)
        return upd_detail
       
    
    def _total(self, cr, uid, ids, field_name, arg, context=None):
        if not ids:
            return {}
        cr.execute("SELECT r.id,COALESCE(SUM(r.units*r.price),0) AS total_line FROM autorepair_detail_repair r WHERE id IN %s GROUP BY r.id ",(tuple(ids),))
        res = dict(cr.fetchall())
        return res

    
    _columns={
              'repair_id':fields.many2one('autorepair.repair',required=True,string="Repair Number"),
              'part_id':fields.many2one('autorepair.part',required=True,string="Part Number"),
              'units':fields.integer(string="Units",size=4),
              'price':fields.float(string="Price"),
              'total_line': fields.function(_total, string='Total')
              }
    _defaults={
        'units':1,
        'price':0
        }
    
    def onchange_part_id(self, cr, uid, ids, part_id,context=None):
        res = {}
        if part_id:
            part = self.pool.get('autorepair.part').browse(cr, uid, part_id, context=context)
            res['price'] = part.price
        return {'value': res}


    def _check_unit_in_stock(self, cr, uid, ids, context={}):
        for repair in self.browse(cr, uid, ids, context=context):
            if repair.units>repair.part_id.stock:
                raise osv.except_osv(_('Stock'), _('No sufficient units in stock'))
                return False
        return True

    _constraints = [
        (_check_unit_in_stock,'No sufficient units in stock',['unit']
         ),
     ]
    

class part(osv.Model):
    _name='autorepair.part'

    _columns={
              'reference': fields.char(string="Part Number",size=20,required=True),
              'description':fields.text(string="Description",required=True),
              'price':fields.float(string="Actual Price",required=True,digits=(10,2)),
              'stock':fields.integer(string="Stock Level",required=True)
                        }
    _defaults={
        'price':0,
        'stock':1,
        }
    _rec_name='reference'
    def _check_price_no_negative(self, cr, uid, ids, context={}):
        for part in self.browse(cr, uid, ids, context=context):
            if part.price<0:
                return False
        return True
    def _check_stock_no_negative(self, cr, uid, ids, context={}):
        for part in self.browse(cr, uid, ids, context=context):
            if part.stock<0:
                return False
        return True

    _constraints = [
        (_check_price_no_negative,'Negatives prices not allowed',['price']
         ),
        (_check_stock_no_negative,'Negatives stock levels not allowed',['stock']
         )      
    ]
    
    _sql_constraints = [
        ('reference_part_unique',
        'UNIQUE(reference)',
        'The part number already exist ')
     ]
    _order="reference,description"

