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
  var self, modal, ofi_form, resources_show, spinner, object_name;

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
      object_name = this.options.object_name;

      console.log(this.options.ofi_api);

      // when the page refreshes, object_name go back to what's specified in the package
      this.$('#object-name').val(object_name);
      this.$('#add-resource').on('click', this._copyResourceToForm);
      ofi_form.submit(this.searchForObject);

      if (object_name) {
        modal.modal('show');
      } else {
        console.log("No object name in package.");
      }
    },
    searchForObject: function(event) {
      event.preventDefault();

      modal.modal('show');
    },
    _toggleSpinner: function(on_off) {
      // TODO: Adjust spinner location
      //       Disable 'Add' in modal when spinner is enabled
      //       Include a 'Cancel' button for the api call
      resources_show.toggleClass('hidden', on_off);
      spinner.toggleClass('enable', on_off);
    },
    _showResults: function(data) {
      resources_show.html("");

      this._toggleSpinner(false); // turn off
    },
    teardown: function() {

    }
  };
});
