from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_photographer = fields.Boolean(string="¿Es fotógrafo?", default=False,store=True)
    instagram_account = fields.Char(string="Cuenta de Instagram",store=True)
    bank_account_info = fields.Text(string="Información de cuentas bancarias",store=True)
    bank_alias = fields.Char(string="Alias Bancario",store=True)
    bank_cbu_cvu = fields.Char(string="CBU/CVU",store=True)
    

    
