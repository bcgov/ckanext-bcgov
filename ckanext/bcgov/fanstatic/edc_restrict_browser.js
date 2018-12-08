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
		var warningText = "You are attempting to update or edit BC Data Catalogue content using a non-supported web browser or version. Supported browsers are Google Chrome (downloadable from <a href=\"https://www.google.com/chrome/\" target=\"_blank\">https://www.google.com/chrome/</a>) and Firefox (downloadable from <a href=\"https://www.mozilla.org/en-US/firefox/new/\" target=\"_blank\">https://www.mozilla.org/en_US/firefox/new/</a>). Not all version of these browsers are supported. If you are seeing this message and you are using Firefox or Chrome, then please report this problem to DataBC Catalogue Services.";
		var $warningDiv = $('<div>' + warningText + "</div>").addClass('alert alert-danger');
		$primaryDiv.prepend($warningDiv);
		
	}
});