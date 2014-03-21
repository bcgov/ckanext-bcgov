// Flyout behavior configs
var _easingSpeed = 400;
var _flyoutPadding = 46;
$.easing.def = "easeInOutExpo";

// Global variables
var _overlay;
var _clickedIndex = -1;
var _themeCount = 0;
var _browserSpecificPaddingAdjustment = 1;
var _browserSpecificLastPositionAdjustment = -3;


$(document).ready(function(){
	SetupMenus();
	iOSCheck();
});


function SetupMenus () {
    _overlay = $("div#overlay");
    _overlay.css("height", $(document).height());

    CalculateBrowserSpecificPaddingAdjustment();

    BindTopMenuEvents();

    BindOverlayEvents();
};

function BindOverlayEvents (){
    _overlay.add($(".overlayControls")).click(function () {
        HideMenus();
    });

    $(window).resize(function () {
        HideMenus();
    });
}

function CalculateBrowserSpecificPaddingAdjustment () {
    /*
    if ($.browser.msie && ($.browser.version == 7.0)) {
        _browserSpecificPaddingAdjustment = 1;
        _browserSpecificLastPositionAdjustment = 1;
    }

    if ($.browser.msie && ($.browser.version == 8.0)) {
        _browserSpecificPaddingAdjustment = -10;
        _browserSpecificLastPositionAdjustment = -4;
    }

    if ($.browser.msie && ($.browser.version >= 9.0)) {
        _browserSpecificPaddingAdjustment = -8;
        _browserSpecificLastPositionAdjustment = -4;
    }

    if ($.browser.mozilla) {
        _browserSpecificPaddingAdjustment = 1;
        _browserSpecificLastPositionAdjustment = -3;
    }
    */
}

function ShowTopNavigation (triggerElement) {
    var flyoutDivObject = GetFlyoutDivObjectFromMenuItem(triggerElement)
    triggerElement = $(triggerElement);

    SetFlyoutPosition(flyoutDivObject, triggerElement.index());

    HideTopNavigation();
    // Easings: http://jqueryui.com/demos/effect/easing.html
    flyoutDivObject.slideDown(_easingSpeed);
    triggerElement.addClass('activeNav');
}

function GetFlyoutDivObjectFromMenuItem (triggerElement) {
    var requestedFlyoutId = $(triggerElement).attr('section');
    return $("#" + requestedFlyoutId);
}

function SetFlyoutPosition (flyoutObject, menuIndex) {
    var documentWidth = $(document).width();
    var containerWidth = $('.themes menu').width();
    var flyoutWidth = flyoutObject.width();

    var basePadding = Math.floor((documentWidth - containerWidth) / 2);
    var itemSpacing = Math.ceil((containerWidth - flyoutWidth) / (_themeCount - 1));

    var positionLimit = basePadding + containerWidth - flyoutWidth - _flyoutPadding;
    var flyoutPosition = basePadding + (itemSpacing * menuIndex) - _flyoutPadding + _browserSpecificPaddingAdjustment;

    if (flyoutPosition > positionLimit) {
        flyoutPosition = positionLimit;
    }

    if (menuIndex == (_themeCount - 1)) {
        flyoutPosition += _browserSpecificLastPositionAdjustment;
    }

    flyoutObject.css('left', flyoutPosition);
}

function HideTopNavigation () {
    $("#navigation .themes .activeNav").removeClass('activeNav');
    $("#flyouts .flyout").hide();
}

function BindTopMenuEvents () {
    $('.flyoutMenuItem').each(function (clickedIndex, flyoutMenuItem) {
        if ($(flyoutMenuItem).attr('section'))_themeCount++;

        $(".clickTrigger", flyoutMenuItem).click(function (event) {
            if (_clickedIndex == clickedIndex) {
                HideMenus();
            }
            else
            {
                ShowOverlay();
                ShowTopNavigation(flyoutMenuItem);
                _clickedIndex = clickedIndex;
            }

            event.stopPropagation();
            return false;
        });

    });
}

function ShowOverlay () {
    _overlay.show();
}

function HideOverlay () {
    _overlay.hide();
}

function HideMenus () {
    HideOverlay();
    HideTopNavigation();
    _clickedIndex = -1;
}

function iOSCheck () {
	if(navigator.userAgent.match(/iPhone|iPod|iPad/i)) {
		//alert("ios detected");
		$(".clickTrigger").remove();
		$(".flyoutMenuItem a").css("margin-right", "21px");
	}
}
