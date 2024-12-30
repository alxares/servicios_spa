{
    'name': 'Gestión de Servicios del Spa',
    'version': '1.1',
    'summary': 'Gestión de servicios de spa y automatización de cotizaciones y ventas.',
    'description': """
        Este módulo permite gestionar empleados, servicios y cotizaciones del spa, 
        integrándose con los módulos de ventas y punto de venta. Incluye datos 
        de ejemplo para facilitar las pruebas y reglas de acceso personalizadas.
    """,
    'author': 'Alexander Arguello',
    'category': 'Sales',
    'depends': [
        'base',
        'hr',
        'sale',
        'contacts',
        'point_of_sale'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/spa_service_view.xml',
        'views/spa_service_action.xml',
        'data/spa_service_demo.xml'  # Agregado para incluir datos de demostración
    ],
    'demo': [
        'data/spa_service_demo.xml'  # Archivo de demostración para pruebas
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',  # Recomendado para aclarar el tipo de licencia
}
