from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_photographer = fields.Boolean(string="¿Es fotógrafo?", default=False)
    instagram_account = fields.Char(string="Cuenta de Instagram")
    bank_account_info = fields.Text(string="Información de cuentas bancarias")
    bank_alias = fields.Char(string="Alias Bancario")
    bank_cbu_cvu = fields.Char(string="CBU/CVU")
