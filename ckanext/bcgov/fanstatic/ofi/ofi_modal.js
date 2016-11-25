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

      if (this.options.object_name == 'False') {
        return;
      }

      console.log(this.options);

      var open_modal = this.options.ofi_results.open_modal;
      var success = this.options.ofi_results.success;
      var content = this.options.ofi_results.content;
      var ofi_exists = this.options.ofi_results.ofi_exists;

      if (success) {
        if (content instanceof Object) {
          modal_controls.find('#ofi-confirm').on('click',this._getResourceForm);
        } 
      }
      else if (ofi_exists) {
        modal_controls.find('#ofi-delete').on('click', this._removeOFIResources);
        modal_controls.find('#ofi-edit').on('click', this._editOFIResources);
      } else {
        this._showResults(content);
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
          modal_subtitle.text('Add OFI Resources');

          modal_controls.find('#ofi-confirm')
            .off('click', self._getResourceForm)
            .on('click', self._createResources)
            .text('Save');

          self._initDatepicker();
        },
        'error': function() {

        }
      });
    },
    _createResources: function(event) {
      event.preventDefault();
      self._toggleSpinner(true);
      modal_subtitle.text('Popluating Dataset');
      
      var form_as_obj = self._serializeArray(ofi_form);

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
        'success': function(data, status) {
          self._showResults(data);

          modal_controls.find('#ofi-cancel')
            .text('Close')
            .on('click', self._backToExistingStart);

          modal_controls.find('#ofi-confirm')
            .off('click', self._createResources)
            .text('Finish')
            .on('click', self._redirectToDatasetPage);

          self._toggleSpinner(false);
        },
        'error': function(jqXHR, textStatus, errorThrown) {
          console.log(jqXHR.responseText);
          self._toggleSpinner(false);
        }
      });
    },
    _removeOFIResources: function(event) {
      self._showResults('<h4>Are you sure you want to remove all OFI resources for this dataset?</h4>');
      modal_subtitle.text('Removing Resources');

      var back_button = $('<button id="ofi-back" class="btn btn-danger">No</button>');
      back_button.on('click', self._backToExistingStart);

      modal_controls.find('#ofi-edit')
        .off('click', self._editOFIResources)
        .off('click', self._updateOFIResources)
        .text('Yes')
        .prop('id', 'ofi-confirm-remove')
        .on('click', self._actuallyRemoveResources)
        .before(back_button);

      modal_controls.find('#ofi-delete').remove();
      modal_controls.find('#ofi-cancel').remove();
    },
    _editOFIResources: function(event) {
      self._toggleSpinner(true);
      modal_subtitle.text('Editing Resources');

      $.ajax({
        'url': self.options.ofi_edit_resources_url,
        'method': 'GET',
        'data': {
          'package_id': self.options.package_id,
          'object_name': self.options.object_name
        },
        'contentType': 'application/json; charset=utf-8',
        'success': function(data, status) {
          self._showResults(data);

          modal_controls.find('#ofi-edit')
            .off('click', self._editOFIResources)
            .text('Save')
            .on('click', self._updateOFIResources);

          modal_controls.find('#ofi-cancel')
            .text('Cancel')
            .on('click', self._backToExistingStart);
          
          self._initDatepicker();
        },
        'error': function(jqXHR, textStatus, errorThrown) {
          console.log(jqXHR);
          self._toggleSpinner(false);
        }
      })
    },
    _updateOFIResources: function(event) {
      self._toggleSpinner(true);

      var form_as_obj = self._serializeArray(ofi_form);

      $.ajax({
        'url': self.options.ofi_edit_resources_url,
        'method': 'POST',
        'data': JSON.stringify({
          'package_id': self.options.package_id,
          'object_name': self.options.object_name,
          'secure': true,
          'ofi_resource_info': form_as_obj
        }),
        'contentType': 'application/json; charset=utf-8',
        'success': function(data, status) {
          self._showResults(data);

          modal_controls.find('#ofi-cancel')
            .text('Close');

          modal_controls.find('#ofi-edit')
            .off('click', self._updateOFIResources)
            .text('Edit')
            .on('click', self._editOFIResources)
        },
        'error': function(jqXHR, textStatus, errorThrown) {
          console.log(jqXHR.responseText);
          self._toggleSpinner(false);
        }
      });
    },
    _actuallyRemoveResources: function(event) {
      self._toggleSpinner(true);

      $.ajax({
        'url': self.options.ofi_remove_resources_url,
        'method': 'POST',
        'data': JSON.stringify({
          'package_id': self.options.package_id,
          'object_name': self.options.object_name,
        }),
        'contentType': 'application/json; charset=utf-8',
        'success': function(data, status) {
          if(data.success) {
            modal_subtitle.text('Removed Resources');
            self._showResults('<h4>OFI resources have been removed from the dataset.</h4>');

            modal_controls.find('#ofi-back').remove();
            modal_controls.find('#ofi-confirm-remove')
              .off('click', self._actuallyRemoveResources)
              .text('Finish')
              .on('click', self._redirectToDatasetPage);
          }
        },
        'error': function(jqXHR, textStatus, errorThrown) {
          self._showResults('<div>There was an error with removing ofi resources.</div>');

          modal_controls.find('#ofi-back').remove();
          modal_controls.find('#ofi-confirm-remove').remove();

          console.log(jqXHR);
        }
      });
    },
    _redirectToDatasetPage: function(event) {
      // redirects to the dataset page
      // uses the form action to redirect to the dataset,
      // bit of a hack but quick and dirty
      ofi_form.prop('action', self.options.to_dataset_page_url);
      ofi_form.submit();
    },
    _backToExistingStart: function(event) {
      /* 
       * This resets the modal to the begin if there's ofi resources in the dataset
       */

      self._showResults('<div>OFI Resources are present in this dataset.</div>');
      modal_subtitle.text('Manage');

      modal_controls.find('#ofi-back').remove();

      /* TODO, example, just why in the fuck this is a thing
       */
      if (modal_controls.has('#ofi-edit').length) {
        modal_controls.find('#ofi-edit')
          .off('click', self._updateOFIResources)
          .text('Edit')
          .on('click', self._editOFIResources);
      }
      else if (modal_controls.has('#ofi-confirm').length) {
        modal_controls.find('#ofi-confirm')
          .off('click', self._redirectToDatasetPage)
          .text('Edit')
          .prop('id', 'ofi-edit')
          .on('click', self._editOFIResources);
      }
      else if (modal_controls.has('#ofi-confirm-remove').length) {
        modal_controls.find('#ofi-confirm-remove')
          .off('click', self._actuallyRemoveResources)
          .text('Edit')
          .prop('id', 'ofi-edit')
          .on('click', self._editOFIResources);
      }

      // if ofi-delete button doesn't exist
      if (modal_controls.has('#ofi-delete').length == 0) {
        var delete_button = $('<button id="ofi-delete" class="btn btn-danger pull-left">Delete</button>');
        delete_button.on('click', self._removeOFIResources);

        modal_controls.find('#ofi-edit')
          .before(delete_button);
      }      

      // if ofi-cancel exists
      if (modal_controls.has('#ofi-cancel').length) {
        modal_controls.find('#ofi-cancel')
          .off('click', self._backToExistingStart)
          .text('Cancel');        
      }
      else {
        var cancel_button = $('<button id="ofi-cancel" class="btn" data-dismiss="modal" aria-hidden="true">Cancel</button>');
        modal_controls.find('#ofi-edit').before(cancel_button);
      }      
    },
    _initDatepicker: function() {
      this.$("#ofi-field-data_collection_start_date")
        .datepicker({
          dateFormat: "yy-mm-dd",
          showOtherMonths: true,
          selectOtherMonths: true
        });
      this.$("#ofi-field-data_collection_end_date")
        .datepicker({
          dateFormat: "yy-mm-dd",
          showOtherMonths: true,
          selectOtherMonths: true
        });
    },
    _toggleSpinner: function(on_off) {
      // TODO: Include a 'Cancel' button for the api call
      //content_body.toggleClass('hidden', on_off);
      spinner.toggleClass('enable', on_off);      
    },
    _showResults: function(data) {
      content_body.html(data);

      this._toggleSpinner(false); // turn off
    },
    _serializeArray: function(form) {
      // makes a plain obj from the form
      return form.serializeArray()
        .reduce(function(a, x) { a[x.name] = x.value; return a; }, {});
    },
    teardown: function() {

    }
  };
});
