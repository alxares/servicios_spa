import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError

# Configuración del logger para el registro de eventos
_logger = logging.getLogger(__name__)

class SpaService(models.Model):
    """
    Modelo para gestionar los servicios de un spa, asignando empleados, clientes y servicios específicos.
    Permite la creación de órdenes de venta y de punto de venta según los servicios seleccionados.
    """
    _name = 'spa.service'
    _description = 'Servicios del Spa'

    # Campos del modelo
    employee_id = fields.Many2one('hr.employee', string='Empleado', required=True, 
                                  help="Empleado asignado para realizar el servicio.")
    client_id = fields.Many2one('res.partner', string='Cliente', required=True, 
                                help="Cliente al que se le proporcionará el servicio.")
    service_ids = fields.Many2many('product.template', string='Servicios', 
                                   help="Lista de servicios seleccionados para el cliente.")
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('confirmed', 'Confirmado'),
        ('sale_order', 'Orden de Venta Creada'),
        ('pos_order', 'Orden de Punto de Ventas Creada'),
    ], default='draft', string='Estado', help="Estado actual del servicio del spa.")

    def _validate_order_data(self):
        """
        Valida los datos necesarios para crear órdenes.

        Levanta una excepción si faltan datos clave como cliente, empleado o servicios.
        """
        if not self.client_id:
            raise UserError(_("Debe seleccionar un cliente para continuar."))
        if not self.employee_id:
            raise UserError(_("Debe asignar un empleado para continuar."))
        if not self.service_ids:
            raise UserError(_("Debe seleccionar al menos un servicio."))

    def _prepare_order_lines(self):
        """
        Prepara las líneas para las órdenes de venta.

        Genera una lista de diccionarios con la información de los servicios seleccionados,
        incluyendo el producto, cantidad y precio unitario.

        :return: Lista de líneas de orden formateadas.
        """
        order_lines = []
        for service in self.service_ids:
            price_unit = service.list_price  # Precio del servicio basado en el precio listado.
            order_lines.append((0, 0, {
                'product_id': service.id,
                'name': service.name,
                'product_uom_qty': 1,
                'price_unit': price_unit,
            }))
        return order_lines

    def _get_open_pos_session(self):
        """
        Busca una sesión abierta de punto de venta.

        Lanza una excepción si no hay ninguna sesión abierta disponible.

        :return: ID de la sesión abierta.
        """
        pos_session = self.env['pos.session'].search([('state', '=', 'opened')], limit=1)
        if not pos_session:
            raise UserError(_("No hay ninguna sesión abierta de Punto de Venta."))
        return pos_session.id

    def create_sale_order(self):
        """
        Crea una orden de venta basada en los servicios seleccionados.

        Valida los datos necesarios y genera un registro en el modelo de órdenes de venta.
        Actualiza el estado del servicio a 'sale_order'.

        :return: Registro de la orden de venta creada.
        """
        self.ensure_one()
        self._validate_order_data()

        sale_order = self.env['sale.order'].create({
            'partner_id': self.client_id.id,
            'order_line': self._prepare_order_lines(),
        })

        self.write({'state': 'sale_order'})
        _logger.info("Orden de venta creada: ID %s", sale_order.id)
        return sale_order

    def create_pos_order(self):
        """
        Crea una orden de punto de venta basada en los servicios seleccionados.

        Valida los datos necesarios y genera un registro en el modelo de órdenes de POS.
        Actualiza el estado del servicio a 'pos_order'.

        :return: Registro de la orden de POS creada.
        """
        self.ensure_one()
        self._validate_order_data()

        pos_session_id = self._get_open_pos_session()
        order_lines = [(0, 0, {
            'product_id': service.id,
            'price_unit': service.list_price,
            'qty': 1,
        }) for service in self.service_ids]

        pos_order = self.env['pos.order'].create({
            'partner_id': self.client_id.id,
            'lines': order_lines,
            'session_id': pos_session_id,
        })

        self.write({'state': 'pos_order'})
        _logger.info("Orden de POS creada: ID %s", pos_order.id)
        return pos_order

    def set_to_draft(self):
        """
        Reinicia el estado del registro a 'borrador'.

        Permite reutilizar el registro para nuevas asignaciones o correcciones.
        """
        self.write({'state': 'draft'})
