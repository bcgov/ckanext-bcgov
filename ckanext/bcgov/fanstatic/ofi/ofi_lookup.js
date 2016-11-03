/**
 * DataBC CITZ EDC
 *
 * HighwayThree Solutions Inc.
 * Author: Jared Smith <github@jrods>
 *
 *
 * OFI Prototype
 *
**/
"use strict";

this.ckan.module('ofi_lookup', function($, _) {
  var self, modal, ofi_form, resources_show, spinner;

  return {
    options: {
      // defaults
    },
    initialize: function() {
      self = this;
      modal = this.el;
      ofi_form = this.$('#ofi-lookup-form');
      resources_show = this.$('#resources');
      spinner = this.$('#loading');

      console.log(this.options.ofi_results);
      console.log(typeof this.options.ofi_results.open_modal);

      var open_modal = this.options.ofi_results.open_modal;
      var success = this.options.ofi_results.success;
      var content = this.options.ofi_results.content;

      if (success) {
        if (content instanceof Object) {
          var prompt;
          if (content['allowed']) {
            prompt = '<div>Object is avaiable, would you like to add all the resource links?</div>';
          } else {
            prompt = '<div>Object is not avaiable, please contact your administrator.</div>';
          }
          this._showResults(prompt);
        } 
      } else {
        this._showResults(content);
      }

      if (open_modal) {
        modal.modal('show');
      }
    },
    _toggleSpinner: function(on_off) {
      // TODO: Adjust spinner location
      //       Disable 'Add' in modal when spinner is enabled
      //       Include a 'Cancel' button for the api call
      resources_show.toggleClass('hidden', on_off);
      spinner.toggleClass('enable', on_off);
    },
    _showResults: function(data) {
      resources_show.html(data);

      this._toggleSpinner(false); // turn off
    },
    teardown: function() {

    }
  };
});
