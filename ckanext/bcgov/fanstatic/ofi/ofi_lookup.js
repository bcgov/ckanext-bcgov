/**
 * DataBC CITZ EDC
 *
 * HighwayThree Solutions Inc.
 * Author: Jared Smith <github@jrods>
 *
**/
'use strict';

this.ckan.module('ofi_lookup', function($, _) {
  var self, modal, ofi_form, resources_show, spinner, object_name;

  return {
    options: {
      protocol: 'https',
      host_name: 'delivery.apps.gov.bc.ca',
      port: '',
      order_path: '/pub/dwds-ofi/',
      order_secure_path: '/pub/dwds-ofi/secure/',
    },
    initialize: function() {
      self = this;
      modal = this.el;
      ofi_form = this.$('#ofi-lookup-form');
      resources_show = this.$('#resources');
      spinner = this.$('#loading');
      object_name = this.options.objectName;

      // when the page refreshes, object_name go back to what's specified in the package
      this.$('#object-name').val(object_name);
      this.$('#add-resource').on('click', this._copyResourceToForm);
      ofi_form.submit(this.searchForObject);

      if (object_name) {
        this._callOFIService("security/productAllowedByFeatureType/" + object_name, true, true);
        modal.modal('show');
      } else {
        console.log("No object name in package.");
      }
    },
    _createURL: function(webService, isSecure) {
      var o = this.options;
      return o.protocol + "://"
              + o.host_name
              + ((o.port === "" || o.port === undefined) ? "" : ":" + o.port)
              + ((isSecure) ? o.order_secure_path : o.order_path)
              + webService;
    },
    _copyResourceToForm: function() {
      console.log("TODO add resource info to the form");

      modal.modal('hide');
    },
    searchForObject: function(event) {
      event.preventDefault();

      console.log('Making secure call:', this.secure.checked);
      console.log('Including credentials:', this.include_creds.checked);

      self._callOFIService("security/productAllowedByFeatureType/" + this.object_name.value,
        this.secure.checked,
        this.include_creds.checked);
      modal.modal('show');
    },
    _toggleSpinner: function(on_off) {
      resources_show.toggleClass('hidden', on_off);
      spinner.toggleClass('enable', on_off);
    },
    _callOFIService: function(service_name, is_secure, include_creds) {
      var httpRequest = new XMLHttpRequest();
      var ofi_url = this._createURL(service_name, is_secure);

      httpRequest.timeout = 30000; // ms
      httpRequest.withCredentials = include_creds;

      httpRequest.onreadystatechange = function () {
        if (httpRequest.readyState == XMLHttpRequest.OPENED) {
          console.log('Calling:', ofi_url);
          self._toggleSpinner(true); // turn on
        }

        if (httpRequest.readyState == XMLHttpRequest.DONE) {
          console.log(httpRequest);

          // testing, TODO: use http status codes for error handling
          if (httpRequest.responseText) {
            var data = JSON.parse(httpRequest.responseText);
            self._showResults(data);
          } else {
            self._showResults(`Please open dev tools, api call did not work.
              <br /><br />
              Expecting error:
              <br />
              * Cross-Origin Request Blocked -> Reason: CORS header 'Access-Control-Allow-Origin' does not mach '*'
              `);
          }
        }
      };

      httpRequest.open('GET', ofi_url, true);
      httpRequest.setRequestHeader('Accept', '*/*');
      httpRequest.send();
    },
    _showResults: function(data) {
      if (typeof data == 'object') {
        resources_show.html(object_name + " is " + ( !data['allowed'] ? "not" : "") + " available.");
      } else {
        resources_show.html('<div><p>' + data + '</p></div>');
      }
      this._toggleSpinner(false); // turn off
    },
    teardown: function() {

    }
  };
});
