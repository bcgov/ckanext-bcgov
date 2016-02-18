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
		var warningText = "This browser is not supported.  Please use another browser.";
		var $warningDiv = $('<div>' + warningText + "</div>").addClass('alert alert-danger');
		$primaryDiv.prepend($warningDiv);
		
	}
});