
from openerp.osv import fields, osv, orm

class wizard_report_repairs_aeroo(osv.TransientModel):
    _name='autorepair.wizard_report_repairs_aeroo'
    
    def out_format_get (self, cr, uid, context={}):
        obj = self.pool.get('report.mimetypes')
        ids = []
        list = []
         
        ids = obj.search(cr, uid, ['|', '|',('code','=','oo-xls'), ('code','=','oo-ods'),('code','=','oo-pdf')])
        #only include format pdf that match with ods format.
        for type in obj.browse(cr, uid, ids, context=context):
            if type.code == 'oo-pdf' and type.compatible_types == 'oo-odt':
                list.append(type.id)
            elif type.code == 'oo-xls' or type.code == 'oo-ods':
                list.append(type.id)
 
        # If read method isn't call, the value for out_format "disappear",
        # the value is preserved, but disappears from the screen (a rare bug)
        res = obj.read(cr, uid, list, ['name'], context)
        return [(str(r['id']), r['name']) for r in res] 
    
    _columns={
              'date_from': fields.date(string="Start Date",required=True),
              'date_to': fields.date(string="End Date",required=True),
              'client_ids':fields.many2many('res.partner',required=True,domain="[('customer','=',True)]",string="Client"),
              'out_format': fields.selection(out_format_get, 'Print Format',requered=True),
              }
    
    def pre_print_report_aeroo(self, cr, uid, ids, data, context=None):       
        if context is None:
            context = {}
        data['form'] = self.read(cr, uid, ids, ['date_from','date_to','client_ids','out_format'], context=context)[0]                       
        for field in ['client_ids']:
            if isinstance(data['form'][field], tuple):
                data['form'][field] = data['form'][field][0]         
        return data
 
    def _print_report_aeroo(self, cr, uid, ids, data, context=None):
        data = self.pre_print_report_aeroo(cr, uid, ids, data, context=context)
        res = {}
        mimetype = self.pool.get('report.mimetypes')
        report_obj = self.pool.get('ir.actions.report.xml')
        report_name = ''
        
        if context is None:
            context = {}

        #=======================================================================
        # onchange_in_format method changes variable out_format depending of 
        # which in_format is choosed. 
        # If out_format is pdf -> call record in odt format and if it's choosed
        # ods or xls -> call record in ods format.
        # ods and xls format are editable format, because they are arranged 
        # to be changed by user and, for example, user can check and change info.    
        #=======================================================================
      
        #=======================================================================
        # If mimetype is PDF -> out_format = PDF (search odt record)
        # If mimetype is xls or ods -> search ods record. 
        # If record doesn't exist, return a error.
        #=======================================================================
       
        #=======================================================================
        # Create two differents records for each format, depends of the out_format
        # selected, choose one of this records
        #=======================================================================
         
        #1. Find out_format selected
        out_format_obj = mimetype.browse(cr, uid, [int(data['form']['out_format'])], context)[0]

        #2. Check out_format and set report_name for each format
        if out_format_obj.code == 'oo-pdf':
            report_name = 'test2_odt' 
           
        elif out_format_obj.code == 'oo-xls' or out_format_obj.code == 'oo-ods': 
            report_name = 'test2_ods'
         
        # If there not exist name, it's because not exist a record for this format   
        if report_name == '':
            raise osv.except_osv(_('Error !'), _('There is no template defined for the selected format. Check if aeroo report exist.'))
             
        else:
            #Search record that match with the name, and get some extra information
            report_xml_id = report_obj.search(cr, uid, [('report_name','=', report_name)],context=context)
            report_xml = report_obj.browse(cr, uid, report_xml_id, context=context)[0]
            data.update({'model': report_xml.model, 'report_type':'aeroo', 'id': report_xml.id})
            
            #Write out_format choosed in wizard
            report_xml.write({'out_format': out_format_obj.id}, context=context)
           
            return {
                  'type': 'ir.actions.report.xml',
                  'report_name': report_name,
                  'datas': data,
                  'context':context
              }

    def check_report(self, cr, uid, ids, context={}):        
            data={}
            return self._print_report_aeroo(cr, uid, ids, data, context=context)
            

    