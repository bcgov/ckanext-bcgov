"use strict";

this.ckan.module('edc_pow', function($, _){
	var self, opt, pkg, pow_order;

	var pow_initialized = false;

	var get_ofi_url = function(endpoint, secure = false) {
		if (secure) {
			return opt.ofi_secure_url + endpoint;
		} else {
			return opt.ofi_public_url + endpoint;
		}
	}

	var get_pow_url = function(endpoint, secure = false) {
		if (secure) {
			return opt.pow_secure_url + endpoint;
		} else {
			return opt.pow_public_url + endpoint;
		}
	}

	return {
		/*
		defaults have been parameterized.
		Parameters passed to the module:

		General params:
		* env
		* pkg
		* secure_site
		* past_orders_nbr
		* custom_aoi_url
		* persist_config
		* user_pow_ui
		* order_source

		OFI Endpoint defaults:
		* ofi_endpoint_url
		* ofi_endpoint_protocol
		* ofi_endpoint_pow_ui_path

		Order defaults:
		* aoi_type
		* aoi
		* ordering_application
		* format_type
		* crs_type
		* metada_url
		*/

		initialize: function() {
			console.log('initializing module "edc_pow"');

			// Ckan Issue #3287 -> https://github.com/ckan/ckan/issues/3287
			// if data-module-* attributes are None from templates,
			// an empty string, etc. these are initialized as `true` in `this.options`
			//
			// set an empty string for `env`, indicates to not use a bcgov subdomain environment
			// eg. use prod if env isn't set in the config
			this.options.env = (typeof this.options.env == "string" && this.options.env.length == 0) || typeof this.options.env == "boolean" ? '' : String(this.options.env)
			// do the same for aoi
			this.options.aoi = (typeof this.options.aoi == "string" && this.options.aoi.length == 0) || typeof this.options.aoi == "boolean" ? '' : String(this.options.aoi)
			// set type to boolean value
			this.options.secure_site = (this.options.secure_site == "True")
			console.log("this.options");
			console.log(this.options);

			// convinence option vars
			self = this;
			opt = this.options;
			pkg = this.options.pkg;

			// load JS dependencies.
			var scripts = [
				'/script/lib/xdLocalStorage.min.js',
				'/script/pow/dwds-POW-api.js'
			];

			scripts.map(function(script) {
				var el = document.createElement('script');
				el.type = 'text/javascript';
				el.src = get_pow_url(script);
				document.body.appendChild(el);
			});

			$('.edc-pow-button').on('click', this.startOrder);
		},

		startOrder: function(event) {
		/*
			console.log(
				'Object Name: ' + pkg.object_name +
				' Package_id: ' + pkg.id +
				' Title: ' + pkg.title);
		*/

			var public_url = get_ofi_url('/public/');
			var secure_url = get_ofi_url('/secure/');

			// Callback function once the dwds finishes initializing
			var run_pow = (pow_initialized) ? self.runOrder : self.initPow;

			dwdspowapi.initialize(public_url, secure_url, opt.custom_aoi_url, opt.past_orders_nbr, opt.secure_site, opt.persist_config, run_pow);
		},

		initPow: function(pow_ready) {
			pow_initialized = pow_ready;

			(!pow_ready)
				? alert('The POW Configuration could not be read from the config cookie and URL parmaters were not provided.')
				: console.log('dwdspowapi::initialize Initialized')

			dwdspowapi.orderData = {
				emailAddress: '',
				aoiType: opt.api_type,
				aoi: opt.aoi,
				clippingMethodTypeId: opt.clipping_method_type_id,
				orderingApplication: opt.ordering_application,
				formatType: opt.format_type,
				crsType: opt.crs_type,
				prepackagedItems: '',
				featureItems: [
					{
						featureItem: pkg.object_name,
						filterValue: '',
						layerMetadataUrl: null,
						layerName: pkg.title,
						filterType: 'No Filter',
						layerMetadataUrl: opt.metadata_url + pkg.name,
						pctOfMax: null
					}
				],
			};

			pow_order = new dwdspowapi.Order(dwdspowapi.orderData, opt.use_pow_ui);
			console.log('dwdspowapi Order Pesisted');

			self.runOrder(pow_ready);
		},

		runOrder: function(pow_ready) {
			(opt.use_pow_ui)
				? self.dwdsPowUi()
				: pow_order.submitOrder(self.powOrderSuccess, self.powOrderFail)
		},

		dwdsPowUi: function() {
			var qs = {
				publicUrl: get_ofi_url('/public/'),
				secureUrl: get_ofi_url('/secure/'),
				customAoiUrl: opt.custom_aoi_url,
				pastOrdersNbr: opt.past_orders_nbr,
				secureSite: opt.secure_site ||(opt.pkg['download_audience'] == 'Government') ,
				orderSource: opt.order_source
			};

			// Create url with query params from above
			var url = get_pow_url( opt.ofi_pow_ui_path,
															(opt.pkg['download_audience'] == 'Government') // true == "user secure POW URL"
														) + $.param(qs);

			window.open(url, "_blank", "resizable=yes, scrollbars=yes, titlebar=yes, width=800, height=900, top=10, left=10");
		},

		powOrderSuccess: function(orderID) {
			alert('Order Id: ' + orderID);
		},

		powOrderFail: function(error) {
			alert('Order Error: ' + error);
		},
	}
});
