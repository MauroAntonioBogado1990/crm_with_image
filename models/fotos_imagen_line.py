from odoo import models, fields

class FotosEquitacionImagenLine(models.Model):
    _name = 'fotos.equitacion.image.line'
    _description = 'Línea de imagen para Equitación'

    equitacion_id = fields.Many2one('fotos.equitacion', string='Foto de Equitación', ondelete='cascade')
    image_file = fields.Binary(string='Imagen', required=True)
    filename = fields.Char(string='Nombre de archivo')
    #is_category_logo = fields.Boolean(string="Usar como imagen de categoría")

