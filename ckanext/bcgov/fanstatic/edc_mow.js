/**
 * DataBC CITZ EDC
 *
 * HighwayThree Solutions Inc.
 * Author: Jared Smith <jrods@github>
 *
 * MOW Modal Window
 *
**/
"use strict";

this.ckan.module('edc_mow', function($, _) {
    var self, modal, modal_subtitle, content_body, modal_controls, spinner;

    return {
        options: {
          // defaults
        },
        initialize: function() {
            self = this;
            modal = this.el;
            content_body = this.$('#mow-content');
            spinner = this.$('#loading');
            modal_subtitle = this.$('#modal-subtitle');
            modal_controls = this.$('.modal-footer');

            console.log(this.options);

        },
        teardown: function() {

        }
    };
});
