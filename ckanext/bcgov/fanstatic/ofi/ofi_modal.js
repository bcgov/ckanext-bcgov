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

this.ckan.module('ofi_modal', function($, _) {
  var self, modal, modal_subtitle, ofi_form, content_body, modal_controls, spinner;

  return {
    options: {
      // defaults
    },
    initialize: function() {
      self = this;
      modal = this.el;
      content_body = this.$('#resources');
      spinner = this.$('#loading');
      modal_subtitle = this.$('#modal-subtitle');
      ofi_form = this.$('#ofi-lookup-form');
      modal_controls = this.$('.modal-footer');

      this._toggleSpinner(true);

      if (this.options.object_name == 'False') {
        //this._showResults('<div>No \'Object Name\' exists for this dataset. Add an \'Object Name\' to the dataset, for OFI.</div>');
        //modal_subtitle.text('No Object Name');
        //modal_controls.find('#ofi-confirm').remove();
        return;
      }

      console.log(this.options);

      var open_modal = this.options.ofi_results.open_modal;
      var success = this.options.ofi_results.success;
      var content = this.options.ofi_results.content;

      if (success) {
        if (content instanceof Object) {
          var prompt;
          //if (content['allowed']) {
            prompt = '<h4 style="text-align:center;">Object is avaiable, would you like to add all the resource links?</h4>';
            modal_controls.find('#ofi-confirm').on('click',this._getResourceForm);
          //} else {
          //  prompt = '<div>Object is not avaiable, please contact your administrator.</div>';
          //  modal_controls.find('#ofi-confirm').remove();
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
          'package_id': self.options.package_id,
          'object_name': self.options.object_name
        }),
        'contentType': 'application/json; charset=utf-8',
        'dataType': 'html',
        'success': function(data, status) {
          self._showResults(data);
          modal_controls.find('#ofi-confirm')
            .off('click', self._getResourceForm)
            .on('click', self._createResources)
            .text('Submit');
          modal_subtitle.text('Add OFI Resources');

          self.$("#ofi-field-data_collection_start_date").datepicker({ dateFormat: "yy-mm-dd", showOtherMonths: true, selectOtherMonths: true });
          self.$("#ofi-field-data_collection_end_date").datepicker({ dateFormat: "yy-mm-dd", showOtherMonths: true, selectOtherMonths: true });
        },
        'error': function() {

        }
      });
    },
    _createResources: function(event) {
      event.preventDefault();
      self._toggleSpinner(true);
      modal_subtitle.text('Popluating Dataset');

      // makes a plain obj from the form
      var form_as_obj = ofi_form.serializeArray()
        .reduce(function(a, x) { a[x.name] = x.value; return a; }, {});

      $.ajax({
        'url': self.options.ofi_populate_dataset_url,
        'method': 'POST',
        'data': JSON.stringify({
          'package_id': self.options.package_id,
          'object_name': self.options.object_name,
          'secure': true,
          'ofi_resource_info': form_as_obj
        }),
        'contentType': 'application/json; charset=utf-8',
        'success': function(data,status) {
          self._showResults(data);
          modal_controls.find('#ofi-confirm')
            .off('click', self._createResources)
            .text('Finish');
          self._toggleSpinner(false);
        },
        'error': function(jqXHR, textStatus, errorThrown) {
          console.log(jqXHR.responseText);
          self._toggleSpinner(false);
        }
      });
    },
    _toggleSpinner: function(on_off) {
      // TODO: Adjust spinner location
      //       Disable 'Add' in modal when spinner is enabled
      //       Include a 'Cancel' button for the api call
      //content_body.toggleClass('hidden', on_off);
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
