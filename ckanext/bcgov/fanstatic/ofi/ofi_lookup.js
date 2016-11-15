/**
 * DataBC CITZ EDC
 *
 * HighwayThree Solutions Inc.
 * Author: Jared Smith <jrods@github>
 *
 * OFI Modal Controller
 *
**/
"use strict";

this.ckan.module('ofi_lookup', function($, _) {
  var self, modal, ofi_form, content_body, spinner;

  return {
    options: {
      // defaults
    },
    initialize: function() {
      self = this;
      modal = this.el;
      ofi_form = this.$('#ofi-lookup-form');
      content_body = this.$('#resources');
      spinner = this.$('#loading');

      this._toggleSpinner(true);

      console.log(this.options);

      var open_modal = this.options.ofi_results.open_modal;
      var success = this.options.ofi_results.success;
      var content = this.options.ofi_results.content;

      if (success) {
        if (content instanceof Object) {
          var prompt;
          //if (content['allowed']) {
            prompt = '<div>Object is avaiable, would you like to add all the resource links?</div>';
            this.$('#add-resources').click(this._getResourceForm);
          //} else {
          //  prompt = '<div>Object is not avaiable, please contact your administrator.</div>';
          //  this.$('#add-resources').remove();
          //}
          this._showResults(prompt);
        } 
      } else {
        this._showResults(content);
        this.$('#add-resources').remove();
      }

      if (open_modal) {
        modal.modal('show');
      }
    },
    _getResourceForm: function(event) {
      event.preventDefault();

      self._toggleSpinner(true);

      $.ajax({
        'url': self.options.ofi_geo_resource_form_url,
        'method': 'POST',
        'data': JSON.stringify({
          'pkg_id': self.options.package_id,
          'object_name': self.options.object_name
        }),
        'contentType': 'application/json; charset=utf-8',
        'dataType': 'html',
        'success': function(data, status) {
          //self._resizeModal();

          self._showResults(data);

          console.log(ofi_form);
        },
        'error': function() {

        }
      });
    },
    _toggleSpinner: function(on_off) {
      // TODO: Adjust spinner location
      //       Disable 'Add' in modal when spinner is enabled
      //       Include a 'Cancel' button for the api call
      content_body.toggleClass('hidden', on_off);
      spinner.toggleClass('enable', on_off);
    },
    _showResults: function(data) {
      content_body.html(data);

      this._toggleSpinner(false); // turn off
    },
    _resizeModal: function(pos) {
      if (pos.width)
        modal.style.width = pos.width;

      if (pos.height)
        modal.style.height = pos.height;
    },
    teardown: function() {

    }
  };
});
