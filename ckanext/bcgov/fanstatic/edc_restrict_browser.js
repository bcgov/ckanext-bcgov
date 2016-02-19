/**
 * Checks on page load what browser is being used.
 * If the browser is not Chrome or Firefox, the page
 * content is removed and a warning is displayed.
 *
 * Include this script on any pages where functionality
 * should be disabled for unsupported browsers.
 */

/**
 * Returns true if current browser is supported,
 * false otherwise.
 *
 * Supported browsers:
 * - Google Chrome
 * - Mozilla Firefox
 * 
 * @return {Boolean}
 */
function isUsingSupportedBrowser() {

	// Detect browser via feature detection rather than userAgent
	
	// Firefox API to install add-ons
	var isFirefox = typeof InstallTrigger !== 'undefined';

	// A global object inserted by Chrome
	var isChrome = !!window.chrome && !!window.chrome.webstore;

	if(isFirefox || isChrome) {
		return true;
	}
	else {
		return false;
	}

}

$(function() {
	if(!isUsingSupportedBrowser()) {
		
		// Remove page content
		var $primaryDiv = $('.primary div.module-content')
		$primaryDiv.html('');

		// Insert a warning
		var warningText = "You are attempting to update or edit Data Catalogue content with a non-supported web browser. Catalogue Editors must use either <a href=\"https://www.google.com/chrome/\" target=\"_blank\">Google Chrome</a> or <a href=\"https://www.mozilla.org/en-US/firefox/new/\" target=\"_blank\">Firefox</a> when editing catalogue content. OCIO provides copies of these web browsers that can be downloaded and installed by all end users on government workstations in its <a href=\"https://selfservecentre.gov.bc.ca/\">Self-Serve Centre</a> – or they may be obtained directly from <a href=\"https://www.google.com/chrome/\" target=\"_blank\">https://www.google.com/chrome/</a> or <a href=\"https://www.mozilla.org/en-US/firefox/new/\" target=\"_blank\">https://www.mozilla.org/en-US/firefox/new/</a>.";
		var $warningDiv = $('<div>' + warningText + "</div>").addClass('alert alert-danger');
		$primaryDiv.prepend($warningDiv);
		
	}
});