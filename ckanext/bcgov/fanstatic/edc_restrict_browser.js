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
	var isChrome = false;


	// please note,
	// that IE11 now returns undefined again for window.chrome
	// and new Opera 30 outputs true for window.chrome
	// but needs to check if window.opr is not undefined
	// and new IE Edge outputs to true now for window.chrome
	// and if not iOS Chrome check
	// so use the below updated condition
	//as of Chrome 71 chrome no longer has the window.chrome.webstore that used to be the way this checked
	//https://stackoverflow.com/a/13348618/9627526 has a continuously updated check
<<<<<<< HEAD

=======
	
>>>>>>> brandon/ckanext-653
	var isChromium = window.chrome;
	var winNav = window.navigator;
	var vendorName = winNav.vendor;
	var isOpera = typeof window.opr !== "undefined";
	var isIEedge = winNav.userAgent.indexOf("Edge") > -1;
	var isIOSChrome = winNav.userAgent.match("CriOS");

	if (isIOSChrome) {
	   // is Google Chrome on IOS
		isChrome = false;
	} else if(
	  isChromium !== null &&
	  typeof isChromium !== "undefined" &&
	  vendorName === "Google Inc." &&
	  isOpera === false &&
	  isIEedge === false
	) {
	   isChrome = true;
	} else {
	   isChrome = false;
	}

	if(isFirefox || isChrome) {
		return true;
	}
	else {
		return false;
	}

}

$(function() {
	//Ckanext-bcgov#685 remove check
	// if(!isUsingSupportedBrowser()) {
	//
	// 	// Remove page content
	// 	var $primaryDiv = $('.primary div.module-content')
	// 	$primaryDiv.html('');
	//
	// 	// Insert a warning
	// 	var warningText = "You are attempting to update or edit BC Data Catalogue content using a non-supported web browser or version. Supported browsers are Google Chrome (downloadable from <a href=\"https://www.google.com/chrome/\" target=\"_blank\">https://www.google.com/chrome/</a>) and Firefox (downloadable from <a href=\"https://www.mozilla.org/en-US/firefox/new/\" target=\"_blank\">https://www.mozilla.org/en_US/firefox/new/</a>). Not all version of these browsers are supported. If you are seeing this message and you are using Firefox or Chrome, then please report this problem to DataBC Catalogue Services.";
	// 	var $warningDiv = $('<div>' + warningText + "</div>").addClass('alert alert-danger');
	// 	$primaryDiv.prepend($warningDiv);
	//
	// }
});
