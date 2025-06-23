from odoo import models, fields, api
import logging
from io import BytesIO
from PIL import Image
import base64

_logger = logging.getLogger(__name__)

class FotosEquitacon(models.Model):
    _name = 'fotos.equitacion'
    _description = 'Fotos de Equitación'

    link_folder = fields.Char(string="Enlace de imagen")
    year = fields.Date(string="Año del Evento")
    jump_height = fields.Selection([
        ('0.80', '0.80 m'),
        ('0.90', '0.90 m'),
        ('1.00', '1.00 m')
    ], string="Altura del Salto")