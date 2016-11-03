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
          if (content['allowed']) {
            prompt = '<div>Object is avaiable, would you like to add all the resource links?</div>';
            this.$('#add-resources').click(this._addResources);
          } else {
            prompt = '<div>Object is not avaiable, please contact your administrator.</div>';
            this.$('#add-resources').remove();
          }
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
    _addResources: function(event) {
      event.preventDefault();
      console.log(this.options.ofi_populate_dataset);
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
    teardown: function() {

    }
  };
});
