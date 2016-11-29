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
    var self, modal, modal_subtitle, content_body, modal_controls, spinner, aoi_form, format_type;

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
            $('#area-info').css("display", "none");
          }
          else {
            // not sure 
          }
          
          $('.max-area-hectares').html(_formatNum(_maxAreaHectares));

          callbackSuccess();

          _toggleSpinner(false);
        },
        'error': function(jqXHR, textStatus, errorThrown) {
          console.log(jqXHR);
          console.log(jqXHR.responseText);

          if (jqXHR.status == 403) {
            console.log('todo');
          }

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
      console.log(areaM2);
      console.log(areaHect);
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
              'http://maps.gov.bc.ca/arcserver/rest/services/province/roads_wm/MapServer/tile/{z}/{y}/{x}', 
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
      $("#mow-err").hide();
      $("#consent-check").change(function() {
        if (this.checked) 
          $("#consent-terms").css("display", "none");
        else
          $("#consent-terms").css("display", "block");
      });
      _fetchMaxDownloadableArea(_initSuccess, _initFailed);
    };

    var _initSuccess = function() {
      $("#mow-ready").show();
      $("#mow-err").hide();

      //listen to order button clicks
      var orderBtn = modal_controls.find('#order-btn')
      orderBtn.off('click');
      orderBtn.on('click', _placeOrder);

      _showMap();
    };

    var _initFailed = function() {
      $("#mow-ready").hide();
      $("#mow-err").show();
    };

    var _toggleSpinner = function(on_off) {
      spinner.toggleClass('enable', on_off);      
    };

    var _formatNum = function(x) {
      return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    };

    var _placeOrder = function() {
      for (var key in self.aoi) {
          console.log('LAT: ' + self.aoi[key].lat);
          console.log('LNG: ' + self.aoi[key].lng);
      }

      var aoi_data = {
        'object_name': self.options.object_name,
        'aoi': self.aoi,
        'emailAddress': aoi_form.find('#email1').val(),
        'EPSG': aoi_form.find('#map_projection').val(),
        'formatType': format_type,
        'featureItems': [
          {'featureItem': self.options.object_name}
        ]          
      };

      console.log(aoi_data);

      $.ajax({
        'url': self.options.aoi_create_order_url,
        'method': 'POST',
        'data': JSON.stringify(aoi_data),
        'contentType': 'application/json; charset=utf-8',
        'success': function(result, status) {
          console.log(result);
        },
        'error': function(jqXHR, textStatus, errorThrown) {
          console.log(jqXHR.responseText);
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
                format_type = event.target.id;                
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
