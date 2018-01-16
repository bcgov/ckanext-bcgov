"use strict";

this.ckan.module('edc_pow', function($, _){
	var self, dwds_url;

	var publicUrl = 'https://' + env + '.apps.gov.bc.ca/pub/dwds-ofi/public/' ;
	var secureUrl = 'https://' + env + '.apps.gov.bc.ca/pub/dwds-ofi/secure/' ;

	var pastOrdersNbr = '5';
	var secureSite = JSON.parse('false');
	var customAoiUrl = 'http://maps.gov.bc.ca/ess/hm/aoi/';

	// change this to false to bypass the POW UI and submit the order directly using the pow api
	var usePowUi = false;
	var pow_initialized = false;

	var _initAndOpenPOW = 

	return {
		options: {
			env: 'delivery',
			dwds_url: 
		},

		initialize: function() {
				self = this;
				console.log('initializing module "edc_pow"');

				var dwds_url = 'https://' + this.options.env + '.apps.gov.bc.ca/pub/dwds-ofi';

				// load JS dependencies.
				var script = document.createElement('script');
				script.type = 'text/javascript';
				script.src = 'https://delivery.apps.gov.bc.ca/pub/dwds-ofi/script/lib/xdLocalStorage.min.js';
				document.body.appendChild(script);

				var script = document.createElement('script');
				script.type = 'text/javascript';
				script.src = 'https://delivery.apps.gov.bc.ca/pub/dwds-ofi/script/pow/dwds-POW-api.js';
				document.body.appendChild(script);

				this.el.on('click', this.startOrder);
		},

		startOrder: function(event) {
			console.log(
				'Object Name: ' + self.options.object_name +
				' Package_id: ' + self.options.package_id +
				' Title: ' + self.options.package_title);
			
			if ( !pow_initialized) {
				_initAndOpenPOW(self.options.object_name, self.options.package_id, self.options.package_title, self.options.package_name);
				pow_initialized = true;
			}
			else {
				if (usePowUi) {
					window.open('https://' + env + '.apps.gov.bc.ca/pub/dwds-ofi/jsp/dwds_pow_current_order.jsp?' +
								'publicUrl=https%3A%2F%2F' + env + '.apps.gov.bc.ca%2Fpub%2Fdwds-ofi%2Fpublic%2F&' +
								'secureUrl=https%3A%2F%2F' + env + '.apps.gov.bc.ca%2Fpub%2Fdwds-ofi%2Fsecure%2F&' +
								'customAoiUrl=http%3A%2F%2F' + env + '.maps.gov.bc.ca%2Fess%2Fhm%2Faoi%2F&' +
								'pastOrdersNbr=' + pastOrdersNbr + '&' +
								'secureSite=' + secureSite + '&' +
								'orderSource=imap4m',
								"_blank", "resizable=yes, scrollbars=yes, titlebar=yes, width=800, height=900, top=10, left=10");
							// window.open('https://test.apps.gov.bc.ca/pub/dwds-ofi/jsp/dwds_pow_current_order.jsp?publicUrl=https%3A%2F%2Fdelivery.apps.gov.bc.ca%2Fpub%2Fdwds-ofi%2Fpublic%2F&secureUrl=https%3A%2F%2Fdelivery.apps.gov.bc.ca%2Fpub%2Fdwds-ofi%2Fsecure%2F&customAoiUrl=http%3A%2F%2Fdelivery.maps.gov.bc.ca%2Fess%2Fhm%2Faoi%2F&pastOrdersNbr=5&secureSite=false&orderSource=imap4m', "_blank", "resizable=yes, scrollbars=yes, titlebar=yes, width=800, height=900, top=10, left=10");

				} else {
					console.log(powOrder);
					//result = powOrder.validate();
					//alert('result of order validation is ' + result);
					powOrder.submitOrder(function(orderID) {
						alert('Order Id: ' + orderID);
					}, function() {
						alert('error')
					});
				}
			}
		},

		initPow: function(object_name, package_id, package_title, package_name) {
			var initState = dwdspowapi.initialize(publicUrl, secureUrl, customAoiUrl, pastOrdersNbr, secureSite, true, function(initState) {
					if (initState) {
						// this is "null" unless we are called back from the Custom AOI Tool
						var submittedAOI = 'null';

						// proections used for converting shapfile to aoi gml
						//Proj4js.defs["EPSG:3857"] = "+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +wktext  +no_defs";
						//Proj4js.defs["EPSG:3005"] = "+proj=aea +lat_1=50 +lat_2=58.5 +lat_0=45 +lon_0=-126 +x_0=1000000 +y_0=0 +ellps=GRS80 +datum=NAD83 +units=m +no_defs";

						//DwdsPow.Init.activateOrder(submittedAOI);
						//alert('Initialized');
						console.log('dwdspowapi::initialize Initialized');

					} else {
						alert('The POW Configuration could not be read from the config cookie and URL parmaters were not provided.');
					}

					dwdspowapi.orderData = {
						emailAddress: '',
						aoiType: '4',
						aoi: '',
						orderingApplication: 'BCDC',
						aoiName: '092B061,092C070',
						formatType: '3',
						crsType: '4',
						clippingMethodType: '0',
						useAOIBounds: '0',
						prepackagedItems: '',
						featureItems: [
							{
								featureItem: object_name,
								filterValue: '',
								layerMetadataUrl: null,
								layerName: package_title,
								filterType: 'Query Filter',
								layerMetadataUrl: 'https://catalogue.data.gov.bc.ca/dataset/' + package_name,
								pctOfMax: null
							}
						],
					};

					var powOrder = new dwdspowapi.Order(dwdspowapi.orderData, usePowUi);
					//alert('order persisted');
					console.log('_initAndOpenPOW::dwdspowapi Order Pesisted');

					if (usePowUi) {
						window.open('https://' + env + '.apps.gov.bc.ca/pub/dwds-ofi/jsp/dwds_pow_current_order.jsp?' +
								'publicUrl=https%3A%2F%2F' + env + '.apps.gov.bc.ca%2Fpub%2Fdwds-ofi%2Fpublic%2F&' +
								'secureUrl=https%3A%2F%2F' + env + '.apps.gov.bc.ca%2Fpub%2Fdwds-ofi%2Fsecure%2F&' +
								'customAoiUrl=http%3A%2F%2F' + env + '.maps.gov.bc.ca%2Fess%2Fhm%2Faoi%2F&' +
								'pastOrdersNbr=' + pastOrdersNbr + '&' +
								'secureSite=' + secureSite + '&' +
								'orderSource=imap4m',
								"_blank", "resizable=yes, scrollbars=yes, titlebar=yes, width=800, height=900, top=10, left=10");

					} else {
						//result = powOrder.validate();
						//alert('result of order validation is ' + result);
						powOrder.submitOrder(function(orderID) {
							alert('Order Id: ' + orderID);
						}, function() {
							alert('error')
						});
					}

				});
		}
	}
})