from openerp.osv import osv, fields
import datetime
from openerp import tools

class client(osv.Model):
    _name='res.partner'
    _inherit='res.partner'
    _columns={
              'vehicle_ids':fields.one2many('autorepair.vehicle','client_id',string="Vehicle Owner"),
              'client':    fields.boolean(string="Is client"),
        }


class vehicle(osv.Model):
    _name='autorepair.vehicle'

    _columns={
              'register': fields.char(string="Register Number",size=20,required=True),
              'client_id':fields.many2one('res.partner',required=True,domain="[('client','=',True)]"),
              'brand':fields.char(size=40,required=False,string="Brand"),
              'model':fields.char(size=40,required=False,String="Model"),
              'color':fields.char(size=10,required=False,String="Color"),
              'repair_ids':fields.one2many('autorepair.repair','vehicle_id',string="Repair Realized"),
      
            }
    
    _sql_constraints = [
        ('reference_register_unique',
        'UNIQUE(register)',
        'The register number already exist ')
     ]
    _order="register,client"


class repair(osv.Model):
    _name='autorepair.repair'

    _columns={
              'repair_num': fields.integer(string="Repair Number",required=True),
              'description':fields.text(string="Description",required=True),
              'vehicle_id':fields.many2one('autorepair.vehicle',required=True),
              'in_date':fields.date(string="Check In"),
              'out_date':fields.date(string="Check Out"),
              'hours':fields.float(string="Hours",digits=(6,2)),
              'client_id':fields.related('vehicle_id','name',readonly=True,type='many2one',relation='res.partner')
              }
    _defaults={
        'hours':1,
        'in_date':fields.date.today,
        'out_date':fields.date.today
        }

    def _check_hours_no_negative(self, cr, uid, ids, context={}):
        for repair in self.browse(cr, uid, ids, context=context):
            if repair.hours<0:
                return False
        return True
    def _check_dates(self, cr, uid, ids, context={}):
        for repair in self.browse(cr, uid, ids, context=context):
            if repair.repair_id.out_date<repair.repair_id.in_date:
                return False
        return True

    _constraints = [
        (_check_hours_no_negative,'Negatives hours not allowed',['hours']
         ),
        (_check_dates,'Check out less than check in',['in_date','out_date']
         )      
    ]
    
    _sql_constraints = [
        ('repair_id_unique',
        'UNIQUE(repair_id)',
        'The repair number already exist ')
     ]
    _order="in_date,client_id"

class detail_repair(osv.Model):
    _name='autorepair.detail_repair'

    _columns={
              'repair_id':fields.many2one('autorepair.repair',required=True,string="Repair Number"),
              'part_id':fields.many2one('autorepair.part',required=True,string="Part Number"),
              'units':fields.integer(string="Units",size=4),
              'price':fields.related('part_id','price',readonly=True,type='many2one',relation='autorepair.part'),
              'vehicle_id':fields.related('repair_id','register',readonly=True,type='many2one',relation='autorepair.vehicle'),
              'client_id':fields.related('vehicle_id','name',readonly=True,type='many2one',relation='res.partner'),

              }
    _defaults={
        'units':1,
        'price':0
        }

    def _check_unit_no_negative(self, cr, uid, ids, context={}):
        for repair in self.browse(cr, uid, ids, context=context):
            if repair.hours<=0:
                return False
        return True

    _constraints = [
        (_check_unit_no_negative,'Negatives or zero units not allowed',['unit']
         ),
     
    ]

    _order="repair_id,client_id"



class part(osv.Model):
    _name='autorepair.part'

    _columns={
              'reference': fields.char(string="Part Number",size=20,required=True),
              'description':fields.text(string="Description",required=True),
              'price':fields.float(string="Price Unit",required=True,digits=(10,2)),
              'stock':fields.integer(string="Stock Level",required=True)
                        }
    _defaults={
        'price':0,
        'stock':1,
        }

    def _check_price_no_negative(self, cr, uid, ids, context={}):
        for part in self.browse(cr, uid, ids, context=context):
            if part.price<0:
                return False
        return True
    def _check_stock_no_negative(self, cr, uid, ids, context={}):
        for part in self.browse(cr, uid, ids, context=context):
            if part.qualify<0:
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

