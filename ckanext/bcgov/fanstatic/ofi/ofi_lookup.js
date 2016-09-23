 /**
  * DataBC CITZ EDC
  *
  * HighwayThree Solutions Inc.
  * Author: Jared Smith <github@jrods>
  *
 **/
'use strict';

this.ckan.module('ofi_lookup', function($, _) {
  var self, modal, resources_show, spinner, object_name;

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
      resources_show = this.$('#resources');
      spinner = this.$('#loading');
      object_name = this.options.objectName;

      this.$('#object-name').val(object_name);
      this.$('#search-object').on('click', this.searchForObject);
      this.$('#add-resource').on('click', this.copyResourceToForm);

      if (object_name) {
        this._callOFIService("security/productAllowedByFeatureType/" + object_name, true);
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
    copyResourceToForm: function() {
      console.log("TODO add resource info to the form");

      modal.modal('hide');
    },
    searchForObject: function() {
      var new_object_name = self.$('#object-name').val();
      if (new_object_name) {
        self._callOFIService("security/productAllowedByFeatureType/" + new_object_name, true);
        modal.modal('show');
      }
    },
    _toggleSpinner: function(on_off) {
      resources_show.toggleClass('hidden', on_off);
      spinner.toggleClass('enable', on_off);
    },
    _callOFIService: function(service_name, is_secure) {
      var httpRequest = new XMLHttpRequest();
      var ofi_url = this._createURL(service_name, is_secure);

      httpRequest.timeout = 30000; // ms
      httpRequest.withCredentials = true;

      httpRequest.onreadystatechange = function () {
        if (httpRequest.readyState == XMLHttpRequest.OPENED) {
          console.log('Calling', ofi_url);
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

/*

var ofi_results, add_resource, resources_show, spinner, object_name;

// TODO: add option from config ini file
var ofi_protocol          = 'https';
var ofi_host_name         = 'delivery.apps.gov.bc.ca';
var ofi_port              = '';
var ofi_order_path        = '/pub/dwds-ofi/';
var ofi_order_secure_path = '/pub/dwds-ofi/secure/';

var create_order_filtered = 'order/createOrderFiltered';

window.addEventListener('DOMContentLoaded', function() {
  ofi_results = $('#ofi-results');
  add_resource = $('#add-resource');
  resources_show = document.getElementById('resources');
  spinner = document.getElementById('loading');
  object_name = document.getElementById('object_name').value;

  var ofi_form = {
    "aoiType": "0",
    "aoi": "",
    "crsType": "0",
    "clippingMethodType": "0",
    "formatType": "3",
    "useAOIBounds": "0",
    "aoiName": "092B061,092C070",
    "prepackagedItems": "",
    "featureItems": [
      {
        "featureItem": object_name,
        "filterValue": "objectid is 0"
      }
    ]
  }

  //call_ofi_service(create_order_filtered, false, ofi_form);

  //call_ofi_service("security/productAllowedByFeatureType/" + object_name, true);

  add_resource.click(copy_resource_to_form);
});

window.addEventListener('load', function() {
  //ofi_results.modal('show');
});

// From https://delivery.apps.gov.bc.ca/ext/dwds-ofi-tester/
var createURL = function(webService, isSecure) {
  return ofi_protocol + "://"
          + ofi_host_name
          + ((ofi_port === "" || ofi_port === undefined) ? "" : ":" + ofi_port)
          + ((isSecure) ? ofi_order_secure_path : ofi_order_path)
          + webService;
};

var call_ofi_service = function(service_name, isSecure, form) {
  var httpRequest = new XMLHttpRequest();
  var ofi_url = createURL(service_name, isSecure);

  form = (form ? JSON.stringify(form) : null);
  var method = (form ? 'POST' : 'GET');

  httpRequest.timeout = 30000; // ms
  httpRequest.withCredentials = true;

  httpRequest.onreadystatechange = function () {
    if (httpRequest.readyState == XMLHttpRequest.OPENED) {
      console.log('calling', ofi_url);
      start_loading();
    }

    if (httpRequest.readyState == XMLHttpRequest.HEADERS_RECEIVED) {
      console.log('received', httpRequest.status);
    }

    if (httpRequest.readyState == XMLHttpRequest.DONE) {
      if (httpRequest.status == 200) {
        parse_results(httpRequest.responseText);
      } else if (httpRequest.status == 400) {

      } else {

      }
    }
  };

  httpRequest.open(method, ofi_url, true);

  if (form && method === 'POST') {
    //httpRequest.setRequestHeader('Accept', 'application/json;charset=UTF-8');
    httpRequest.setRequestHeader('Content-Type', 'application/json');
  }

  httpRequest.send(form);
};

var parse_results = function(responseText) {
  var response = JSON.parse(responseText);

  console.log(response);

  post_results(response);
};

var post_results = function(results) {
  results = JSON.stringify(results);
  var results_element = document.createElement('div').appendChild(document.createTextNode(results));

  resources_show.appendChild(results_element);

  finish_loading();
};

var copy_resource_to_form = function() {
  console.log("TODO add resource info to the form");

  ofi_results.modal('hide');
};

var start_loading = function() {
  resources_show.style.display = "none";
  spinner.classList.toggle('enable');
};

var finish_loading = function() {
  resources_show.style.display = "block";
  spinner.classList.toggle('enable');
};
*/
