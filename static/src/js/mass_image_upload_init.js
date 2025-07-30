odoo.define('crm_with_image.mass_image_upload_init', function (require) {
    "use strict";

    const MassImageUploader = require('crm_with_image.mass_image_upload');

    odoo.ready(function () {
        const uploader = new MassImageUploader();
        uploader.appendTo(document.body);
    });
});
