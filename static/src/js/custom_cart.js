//se agrega este assets para poder realizar la llamada de vista de odoo

odoo.define('custom_popup_controller', function (require) {
    "use strict";

    var ajax = require('web.ajax');
    var Dialog = require('web.Dialog');

    function mostrarDatosFotografo() {
        ajax.jsonRpc("/photographer/info", 'call', {}).then(function (result) {
            new Dialog(null, {
                title: "Información del Fotógrafo",
                size: 'medium',
                $content: $('<div>').html(result.html),
                buttons: [{
                    text: "Continuar al checkout",
                    classes: "btn-primary",
                    click: function () {
                        window.location.href = "/shop/checkout?express=1";
                    }
                }]
            }).open();
        });
    }

    // 🔥 Esto es CLAVE para que esté disponible globalmente
    window.mostrarDatosFotografo = mostrarDatosFotografo;
});