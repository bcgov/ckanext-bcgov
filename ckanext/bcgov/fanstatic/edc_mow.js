/**
 * DataBC CITZ EDC
 *
 * HighwayThree Solutions Inc.
 * Author: Jared Smith <jrods@github>
 *
 * MOW Modal Window
 *
**/
"use strict";

this.ckan.module('edc_mow', function($, _) {
    var self, modal, modal_subtitle, content_body, modal_controls, spinner;

    var _map = null;
    var _maxAreaHectares = null;

    var _getMaxDownloadArea = function(callbackSuccess, callbackErr) {
      _toggleSpinner(true);

      //simulate async ajax call to fetch the dataset with the maximum 
      //downloadable area for this dataset
      setTimeout(function() {
        console.log("todo: fetch the resource that gives the max downloadable area for this dataset.  for now just assume a max area of 5000000 hectares");
        _maxAreaHectares = 5000000;
        $('.max-area-hectares').html(_formatNum(_maxAreaHectares));
        callbackSuccess();
        _toggleSpinner(false);
      }, 2000);
    }

    var _mapViewChanged = function(e) {
      var bounds = _map.getBounds();
      var latLonList = [
        bounds.getSouthWest(), 
        bounds.getNorthWest(), 
        bounds.getNorthEast(), 
        bounds.getSouthEast(), 
        bounds.getSouthWest()]
      var areaM2 = L.GeometryUtil.geodesicArea(latLonList)
      var areaHect = Math.round(areaM2 * 0.0001);
      $('#selected-area').html(_formatNum(areaHect))

      if (areaHect < _maxAreaHectares) {
        //$('#order-btn').removeClass("disabled");
        $('#order-btn').prop('disabled', false);
        $('#area-warning').hide();
      }
      else {
        //$('#order-btn').addClass("disabled")
        $('#order-btn').prop('disabled', true);
        $('#area-warning').show();
      }
    }

    var _showMap = function() {

      var bcgovRoadsLayer =  
        L.tileLayer(
            'http://maps.gov.bc.ca/arcserver/rest/services/province/roads_wm/MapServer/tile/{z}/{y}/{x}', {
            attribution: '&copy; Government of British Columbia',
            minZoom: 4,
            maxZoom: 17,
            });

      var initialCenterLatLon = [53.5, -128];
      var initialZoom = 4;
      _map = L.map('map', {layers: [bcgovRoadsLayer]}) 
      
      _map.on("zoomend", _mapViewChanged)
      _map.on("moveend", _mapViewChanged)
      
      _map.setView(initialCenterLatLon, initialZoom);
    }

    var _initSuccess = function() {
      $("#mow-ready").show();
      $("#mow-err").hide();

      modal_controls.find('#order-btn').on('click', _placeOrder);

      _showMap();
    }

    var _initFailed = function() {
      $("#mow-ready").hide();
      $("#mow-err").show();
    }

    var _toggleSpinner = function(on_off) {
      spinner.toggleClass('enable', on_off);      
    }

    var _formatNum = function(x) {
      return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    }

    var _placeOrder = function() {
      console.log("todo: place the order");
    }

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

            //capture the bootstrap event fired when the modal window is actually
            //shown.  
            //at this time invalidate the map to ensure it fills the expected 
            //screen real estate
            $("#edc-mow").on("shown.bs.tab", function() {
                _getMaxDownloadArea(_initSuccess, _initFailed)
            });

        },
        teardown: function() {}
    };
});
