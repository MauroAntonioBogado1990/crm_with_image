from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
from io import BytesIO
from PIL import Image
import base64
import re
import unicodedata

_logger = logging.getLogger(__name__)

def slug(text):
    if not text:
        return 'evento'
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    text = re.sub(r'[^\w\s-]', '', text).strip().lower()
    return re.sub(r'[-\s]+', '-', text)

class FotosEquitacon(models.Model):
    _name = 'fotos.equitacion'
    _description = 'Fotos de Equitación'

    name = fields.Char(string="Nombre")
    year = fields.Date(string="Año del Evento")
    jump_height = fields.Selection([('0.80', '0.80 m'), ('0.90', '0.90 m'), ('1.00', '1.00 m')],string="Altura del Salto")
    watermark_image = fields.Binary(string="Marca de Agua")
    image_ids = fields.One2many('fotos.equitacion.image.line', 'equitacion_id', string='Imágenes')
    mass_upload_images = fields.Many2many('ir.attachment', string="Imágenes Cargadas")
    #link = fields.Char(string="Link externo")
    #bono
    bono = fields.Boolean(string="bono")
    public_category_id = fields.Many2one(
        'product.public.category',
        string='Categoría de destino',
        required=False
    )

    def _process_image(self, original_image_b64, watermark_image_b64=False):
        if not original_image_b64:
            return False

        try:
            image = Image.open(BytesIO(base64.b64decode(original_image_b64))).convert("RGB")

            # Comprimir
            compressed_buffer = BytesIO()
            image.save(compressed_buffer, format='JPEG', quality=40)
            compressed_image = Image.open(BytesIO(compressed_buffer.getvalue())).convert("RGBA")

            if watermark_image_b64:
                watermark = Image.open(BytesIO(base64.b64decode(watermark_image_b64))).convert("RGBA")
                # Redimensionar watermark al 30% del ancho
                wm_max_width = int(compressed_image.width * 0.3)
                if watermark.width > wm_max_width:
                    ratio = wm_max_width / float(watermark.width)
                    wm_height = int(watermark.height * ratio)
                    watermark = watermark.resize((wm_max_width, wm_height), Image.LANCZOS)

                # Posicionar en el centro
                pos_x = (compressed_image.width - watermark.width) // 2
                pos_y = (compressed_image.height - watermark.height) // 2

                # Crear capa transparente para mezclar
                layer = Image.new('RGBA', compressed_image.size, (0, 0, 0, 0))
                layer.paste(watermark, (pos_x, pos_y), watermark)
                compressed_image = Image.alpha_composite(compressed_image, layer)

            # Guardar como JPEG final
            output = BytesIO()
            compressed_image.convert("RGB").save(output, format='JPEG', quality=50)
            return base64.b64encode(output.getvalue())

        except Exception as e:
            _logger.error(f"Error procesando imagen: {e}", exc_info=True)
            return False
            
    def action_enviar_varias_fotos(self):
        self.ensure_one()

        if not self.public_category_id:
            raise UserError("Debés seleccionar una categoría de destino.")

        for attachment in self.mass_upload_images:
            processed_image_b64 = self._process_image(attachment.datas, self.watermark_image)
            if not processed_image_b64:
                continue

            self.env['product.template'].create({
                'name': attachment.name,
                'image_1920': processed_image_b64,
                'website_published': True,
                'year': self.year,
                'jump_height': self.jump_height,
                #'link': self.link,
                'equitacion_id': self.id,
                'public_categ_ids': [(6, 0, [self.public_category_id.id])],
            })

        return {'type': 'ir.actions.act_window_close'}

