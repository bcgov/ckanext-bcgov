/**
 * DataBC CITZ EDC
 *
 * HighwayThree Solutions Inc.
 * Author: Jared Smith <jrods@github>, Brock Anderson <brock@bandersgeo.ca>
 *
 * MOW Modal Window
 *
**/
"use strict";

this.ckan.module('edc_mow', function($, _) {
    var self, modal, modal_subtitle, content_body, modal_controls, spinner, aoi_form, format;

    var _map = null;
    var _maxAreaHectares = null;
    var _initialCenterLatLon = [53.5, -128];
    var _initialZoom = 4;

    var _fetchMaxDownloadableArea = function(callbackSuccess, callbackErr) {
      if (_maxAreaHectares){
        callbackSuccess();
        return;
      }

      _toggleSpinner(true);

      $.ajax({
        'url': self.options.mow_max_aoi_url,
        'data': {
          'secure': (self.options.secure_call !== 'False' ? true : false),
          'object_name': self.options.object_name,
          'package_id': self.options.package_id
        },
        'success': function(data, status) {
          console.log(data);
          if (data.success) {
            data.datastore_response.records.forEach(function(record, index) {
              if (record.FEATURE_TYPE === self.options.object_name) {
                _maxAreaHectares = parseInt(record.MAXAOISIZEHA);
                return;
              }
            });
          }
          else if (data.records_found === 0) {
            _maxAreaHectares = 0;
            $('#area-info').hide();
          }
          else {
            modal_subtitle.text('Error');

            $('#mow-err').html(data);
            callbackErr();

            _toggleSpinner(false);
            return false;
          }

          $('.max-area-hectares').html(_formatNum(_maxAreaHectares));

          callbackSuccess();
          _toggleSpinner(false);
        },
        'error': function(jqXHR, textStatus, errorThrown) {
          console.log(jqXHR);
          console.log(jqXHR.responseText);

          $('#mow-err').html(jqXHR.responseText);

          callbackErr();
          _toggleSpinner(false);
        }
      });
    };

    var _mapViewChanged = function(e) {
      var bounds = _map.getBounds();
      var latLonList = [
        bounds.getSouthWest(),
        bounds.getNorthWest(),
        bounds.getNorthEast(),
        bounds.getSouthEast(),
        bounds.getSouthWest()]

      self.aoi = latLonList;
      var areaM2 = L.GeometryUtil.geodesicArea(latLonList)
      var areaHect = Math.round(areaM2 * 0.0001);

      $('#selected-area').html(_formatNum(areaHect))

      if (areaHect < _maxAreaHectares || _maxAreaHectares == 0) {
        //$('#order-btn').removeClass("disabled");
        $('#order-btn').prop('disabled', false);
        $('#area-warning').hide();
      }
      else {
        //$('#order-btn').addClass("disabled")
        $('#order-btn').prop('disabled', true);
        $('#area-warning').show();
      }
    };

    var _showMap = function() {
      if (!_map) {
        var bcgovRoadsLayer =
          L.tileLayer(
              'https://maps.gov.bc.ca/arcserver/rest/services/province/roads_wm/MapServer/tile/{z}/{y}/{x}',
              {
                attribution: '&copy; Government of British Columbia',
                minZoom: 4,
                maxZoom: 17
              }
            );

        _map = L.map('map', {layers: [bcgovRoadsLayer]});

        _map.on("zoomend", _mapViewChanged);
        _map.on("moveend", _mapViewChanged);
      }
      _map.setView(_initialCenterLatLon, _initialZoom);
    };

    var _initStart = function() {
      $("#mow-ready").hide();
      $('#mow-order').hide();
      _removeDebugMsg();
      _removeAllErrorMsg();

      if (!document.getElementById("order-btn")) {
        modal_controls.append('<button id="order-btn" class="btn btn-primary">Place order</button>');
      }

      modal_subtitle.text('Pan and zoom this map to select the geographic area.');

      var consent_check = $("#consent-check");

      if (consent_check.prop('checked')) {
        $("#consent-terms").hide()
      }

      consent_check.change(function() {
        if (this.checked)
          $("#consent-terms").hide();
        else
          $("#consent-terms").show();
      });
      _fetchMaxDownloadableArea(_initSuccess, _initFailed);
    };

    var _initSuccess = function() {
      $("#mow-ready").show();
      _removeAllErrorMsg();

      //listen to order button clicks
      var orderBtn = modal_controls.find('#order-btn')
      orderBtn.off('click');
      orderBtn.on('click', _placeOrder);

      _showMap();
    };

    var _initFailed = function() {
      $("#mow-ready").hide();
      $("#mow-err").show();
      modal_controls.find('#order-btn').remove();
    };

    var _toggleSpinner = function(on_off) {
      spinner.toggleClass('enable', on_off);
    };

    var _formatNum = function(x) {
      return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    };

    var _checkForm = function() {
      var form_check = true;
      var error_html = '';

      var consent = $("#consent-check").prop('checked');
      if (!consent) {
        error_html += '<div><strong>Error:</strong> You must accept the term and conditions.</div>';
        $("#consent").addClass('error error-missing');
        form_check = false;
      } else {
        $("#consent").removeClass('error error-missing');
      }

      var email = $.trim($('#email1').val());
      if (email === '') {
        error_html += '<div><strong>Error:</strong> Please provide an email address.</div>';
        $("#email").addClass('error error-missing');
        form_check = false;
      } else {
        $("#email").removeClass('error error-missing');
      }

      if (!form_check) {
        $('#mow-err').html(error_html).show();
      }

      return form_check;
    };

    var _removeAllErrorMsg = function() {
      $('#mow-err').empty().hide();
      $("#consent").removeClass('error error-missing');
      $("#email").removeClass('error error-missing');
    };

    var _removeDebugMsg = function() {
      $('#mow-debug').empty().hide();
    };

    var _placeOrder = function() {
      _toggleSpinner(true);

      if (_checkForm() == false) {
        _toggleSpinner(false);
        return false;
      }

      var aoi_data = {
        'object_name': self.options.object_name,
        'aoi': self.aoi,
        'consent': $("#consent-check").prop('checked'),
        'emailAddress': $.trim(aoi_form.find('#email1').val()),
        'EPSG': aoi_form.find('#map_projection').val(),
        'format': format,
        'featureItems': [
          {'featureItem': self.options.object_name,'filterValue': ''}
        ]
      };

      console.log(aoi_data);

      $.ajax({
        'url': self.options.aoi_create_order_url,
        'method': 'POST',
        'data': JSON.stringify({
          'aoi_params': aoi_data
        }),
        'contentType': 'application/json; charset=utf-8',
        'success': function(data, status) {
          console.log(data)
          var order_resp = data.order_response;

          _removeAllErrorMsg();
          _removeDebugMsg();

          if (order_resp.Status == 'SUCCESS') {
            modal_subtitle.text('Order Success');
            $('#mow-order').html('<h3>Success</h3><h4>The order has been placed and will be sent to the provided email address.</h4><p>Order ID: ' + order_resp.Value + '</p>');

            $('#mow-order').show();
            $('#mow-ready').hide();
            modal_controls.find('#order-btn').remove();
          }
          else {
            modal_subtitle.text('Error');
            $('#mow-err').html('<strong>Error:</strong> ' + order_resp.Description);

            modal_controls.find('#order-btn').remove();

            $('#mow-ready').hide();
            $('#mow-err').show();

            var debug_info = '';
            debug_info += '<p>URL: ' + data.api_url + '</p>';

            if (data.sm_url)
              debug_info += '<p>SM URL: ' + data.sm_url + '</p>';
            
            debug_info += '<p>Order Response: ' + data.order_response + '</p>' +
                          '<pre>' +
                          JSON.stringify(data.order_sent, function(key, value) {
                            if (key == 'aoi') {
                              return $("<div>").text(value).html();
                            } else {
                              return value;
                            }
                          }, '\t') + '</pre>';

            $('#mow-debug').html(debug_info);
            $('#mow-debug').show();
          }

          _toggleSpinner(false);
        },
        'error': function(jqXHR, textStatus, errorThrown) {
          console.log(jqXHR);
          console.log(jqXHR.responseText);

          _removeAllErrorMsg();
          _removeDebugMsg();

          if (jqXHR.status === 400) {
            var err = JSON.parse(jqXHR.responseText);

            if (err) {
              var error_html = '';
              if (err.invalid_email) {
                error_html += '<div><strong>Error:</strong> Please provide a valid email address.</div>';
                $("#email").addClass('error error-missing');
              }

              if (err.no_consent) {
                error_html += '<div><strong>Error:</strong> You must accept the term and conditions.</div>';
                $("#consent").addClass('error error-missing');
              }

              if (err.order_failed) {
                error_html += '<div><strong>Error:</strong> Order Failure - ' + err.order_response.Description;
              }

              if (err.api_url || err.order_response || err.order_sent || err.sm_url) {
                var debug_info = '';

                debug_info += '<p>Order URL: ' + err.api_url + '</p>';

                if (err.sm_url)
                  debug_info += '<p>Secure SM get URL: ' + err.sm_url + '</p>';

                if (err.sm_uuid)
                  debug_info += '<p>UUID: ' + err.sm_uuid + '</p>';

                var response = null;
                if (err.order_response) {
                  response = err.order_response;
                }
                else if (err.sm_resp) {
                  response = err.sm_resp;
                }

                debug_info += '<p>Order Response: ' + response + '</p>' +
                              '<pre>' +
                              JSON.stringify(err.order_sent, function(key, value) {
                                if (key == 'aoi') {
                                  return $("<div>").text(value).html();
                                } else {
                                  return value;
                                }
                              }, '\t') + '</pre>';

                $('#mow-debug').html(debug_info);
                $('#mow-debug').show();
              }

              $('#mow-err').html(error_html).show();
            }

          }

          _toggleSpinner(false);
        }
      });
     };

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
            aoi_form = this.$('#aoi-order-form');

            $.map($('.edc-mow-button'), function(button) {
              $(button).on('click', function(event) {
                // allows the button for the specified resource to give its format type to be passed to the server
                event.preventDefault();
                format = event.target.id;
                $("#edc-mow").modal("show");
              });
            });

            //capture the bootstrap event fired when the modal window is actually
            //shown.
            //perform any initialization that can't be done until the modal window is actually
            //visible
            $("#edc-mow").on("shown.bs.tab", function(event) {
              _initStart();
            });
        },
        teardown: function() {}
    };
});
