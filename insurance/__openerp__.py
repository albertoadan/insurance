{
        "name" : "insurance",
        "version" : "0.EAC3.1314S2",
        "author" : "Institut Obert de Catalunya",
        "website" : "http://ioc.xtec.cat",
        "category" : "Unknown",
        "description": """
          Module prepared by "Institut Obert de Catalunya" 
          to learn the use of the OpenObject framework 
          in order to adapt OpenERP and create new modules.
          
          It is part of the learning materials for the module
          "Sistemes de gestió empresarial" in the course
          "CFS Desenvolupament d'aplicacions multiplataforma".
        """,
        "depends" : ['base','product','jasper_reports','base_report_designer'],
        "init_xml" : [ ],
        "demo_xml" : ['demo/insurance_demo.xml'],
        "update_xml" : ['security/insurance_security.xml',
                        'security/ir.model.access.csv',
                        'insurance_view.xml',
                        'wizard/insurance_generate_renewals_view.xml',
                        'insurance_statistics.xml',
                        'report/insurance_policies_reports.xml',
                       ],
        "installable": True
}
