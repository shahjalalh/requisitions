{
    'name': 'Requisition',
    'summary': """Requisition""",
    'description': """
        Requisition module helps officially request or take products before createing RFQ in purchase:
            - 1
            - 2
            - 3
    """,
    'author': "Shahjalal Hossain",
    'website': "https://github.com/shahjalalh",
    'category': 'Purchase',
    'version': '1.0',
    'depends': ['base', 'account', 'purchase', 'stock'],
    'data': [
        'views/requisition_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
