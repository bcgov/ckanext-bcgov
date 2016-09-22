// Amazon Side Bar Menu- by JavaScript Kit (www.javascriptkit.com)
// Date created: March 15th, 2014
// Visit JavaScript Kit at http://www.javascriptkit.com/ for full source code

document.createElement("nav") // for IE

var govNav = {

	defaults: {
		animateduration: 200,
		showhidedelay: [0, 200],
		hidemenuonclick: false
	},

	setting: {},
	menuzindex: 1000,
	touchenabled: !!('ontouchstart' in window) || !!('ontouchstart' in document.documentElement) || !!window.ontouchstart || !!window.Touch || !!window.onmsgesturechange || (window.DocumentTouch && window.document instanceof window.DocumentTouch),

	showhide:function($li, action, setting){
		clearTimeout( $li.data('showhidetimer') )
		if (action == 'show'){
			$li.data().showhidetimer = setTimeout(function(){
				$li.addClass('selected')
				$li.addClass('open')
				$li.find(".level-trigger").addClass('open')
				$li.data('$submenu')
					.data('fullyvisible', false)
					.css({zIndex: govNav.menuzindex++})
					.fadeIn(setting.animateduration, function(){
						$(this).data('fullyvisible', true)
					})
				}, this.setting.showhidedelay[0])
		}
		else{
			$li.data().showhidetimer = setTimeout(function(){
				$li.removeClass('selected')
				$li.removeClass('open')
				$li.find(".level-trigger").removeClass('open')
				if($li.data("$submenu")) {
					$li.data('$submenu').stop(true, true).fadeOut(setting.animateduration)
					var $subuls = $li.data('$submenu').find('.issub').css({display: 'none'})
					if ($subuls.length > 0){
						$subuls.data('$parentli').removeClass('selected')
					}
				}
			}, this.setting.showhidedelay[1])
		}
	},

	setupmenu:function($menu, setting){
		var $topul = $menu.children('ul:eq(0)')

		function addevtstring(cond, evtstr){
			return (cond)? ' ' + evtstr : ''
		}

		$topul.find('li>div, li>ul').each(function(){ // find drop down elements
			var $parentli = $(this).parent('li')
			var $dropdown = $(this)
			$parentli
				.addClass('hassub')
				.data({$submenu: $dropdown, showhidetimer: null})
				.on('mouseenter click', function(e) {
				//	if($(window).width() > 768||(e.type=='click')){
				//		govNav.showhide($(this).closest("li"), 'show', setting)
				//	}
					if($(window).width() > 768) {
						if($("#header").hasClass("collapsed-header")) {
							//if((e.type=='click')) {
							//	govNav.showhide($(this).closest("li"), 'show', setting);
							//}
							// ignore the mouseenter event
						} else {
							govNav.showhide($(this).closest("li"), 'show', setting);
						}
					}
					else {
						if((e.type=='click')){
							govNav.showhide($(this).closest("li"), 'show', setting)
						}
					}

				})
				.on('click', function(e){
					e.stopPropagation()
				})
				.children('a').on('click', function(e){
					//e.preventDefault() // prevent menu anchor links from firing
				})
			$parentli.find(".level-trigger")
				.on('click', function(e){
					if($(this).hasClass("open")){
						govNav.showhide($(this).closest("li"), 'hide', setting)
					}else{
						govNav.showhide($(this).closest("li"), 'show', setting)
					}
				})
				.on('click', function(e){
					e.stopPropagation()
				})
				.children('a').on('click', function(e){
					//e.preventDefault() // prevent menu anchor links from firing
				})
			$dropdown
				.addClass('issub')
				.data({$parentli: $parentli})
				.on('mouseleave' + addevtstring(setting.hidemenuonclick/* || govNav.touchenabled*/, 'click'), function(e){
					if ($(this).data('fullyvisible') == true){
						govNav.showhide($(this).data('$parentli'), 'hide', setting)
					}
					if (e.type == 'click'){
						e.stopPropagation()
					}
				})
		}) // end find
		$topul.on('click', function(e){
			if ($(this).data('fullyvisible') == true){
				govNav.showhide($(this).children('li.hassub.selected'), 'hide', setting)
			}
		})
		var $mainlis = $topul.children('li.hassub').on('mouseleave', function(){
			govNav.showhide($(this), 'hide', setting)
		})
	},

	init:function(options){
		var $menu = $('#' + options.menuid)
		this.setting = $.extend({}, options, this.defaults)
		this.setting.animateduration = Math.max(50, this.setting.animateduration)
		this.setupmenu($menu, this.setting)
	}

}

/********************************
* Collapse Menu
********************************/


$(document).ready(function(event) {
	$(".back-to-top").on("focus mousedown", function(e) {
		e.preventDefault();
	    $('html,body').animate({ scrollTop: 0 }, 'slow');
	});

	//var touchenabled = !!('ontouchstart' in window) || !!('ontouchstart' in document.documentElement) || !!window.ontouchstart || !!window.Touch || !!window.onmsgesturechange || (window.DocumentTouch && window.document instanceof window.DocumentTouch);
	var touchenabled = (('ontouchstart' in window) || (navigator.MaxTouchPoints > 0) || (navigator.msMaxTouchPoints > 0));

	$('#footerToggle > a').click(function(event) {
        event.preventDefault();
        toggleFooter(event);
    });

    //open/close menu when a user clicks, tabs over the govMainMenu
    // DATABC EDIT
    $('.menu-button').on("focus mousedown",function(e) {
       	toggleHeaderElements(this);
       	//addScrollableBurgerMenu();
        e.preventDefault();
	});

 	// DATABC EDIT
    // Handler for when the user clicks on the search button (mobile and collapsed header views only)
    $('.search-button').on("focus mousedown", function(e) {
    	toggleHeaderElements(this);
        e.preventDefault();
	});

	// DATABC EDIT
    // When the search field is toggled, move focus to the input field (mobile and collapsed header views only)
	$('#header-main-row1').on("shown.bs.collapse", function() {
		$('.header-search').addClass('overflow');
		$("input#global-search").focus();
	});
	$('#header-main-row1').on("hidden.bs.collapse", function() {
		$('.header-search').removeClass('overflow');
	});
    /*  DATABC OVERRIDE
	$('#header-main-row2').on("shown.bs.collapse", function() {
		if($("#header").hasClass("collapsed-header")) {
			addScrollableBurgerMenu();
		}
	});    */

    $("#govNavMenu li a").on("focus", function(e) {
        var list = $(this).closest("li").addClass("focus")
    }).on("blur", function(e) {
        var list = $(this).closest("li").removeClass("focus")
    });

    govNav.init({
    	menuid: 'govMainMenu'
    })
    //navigate menu with keyboard
    $(document).keydown(function(e) {
    	if($("#govNavMenu").is(":visible") && !$("#govNavMenu input").is(":focus")) {
    		var currentItem= $("#govNavMenu :focus").closest("li");
    	    switch(e.which) {
    	    	case 9: //tab - close menu
	    			setTimeout(function(){
	    				$('.menu-button').focus();
	 	           }, 100);
        	        break;
    	        case 37: // left - select parent list item
    	        	var prevItem=currentItem.closest("ul").closest("li");
    	        	prevItem.find("> a").focus();
					//if top level close menu
    	        	if(!prevItem.length>0){
    	        		$("#govNavMenu").each(function(){
    	        			$(this).addClass("hidden").removeAttr("style");
    	        			$(this).removeClass("expanded");
    	        		});
    	        	}else if(prevItem.hasClass("hassub")){
    					govNav.showhide(prevItem, 'show',govNav.setting);
    					if(currentItem.hasClass("hassub")){
        					govNav.showhide(currentItem, 'hide',govNav.setting);
    					}
    	        	}
    	        break;

    	        case 38: // up - open previous item in the current list
    	        	var prevItem=currentItem.closest("li").prev("li");
    	        	if(prevItem.length){
    	        		prevItem.find("> a").focus();
    	    		}
    	        	if(prevItem.hasClass("hassub")){
    					govNav.showhide(prevItem, 'show',govNav.setting);
    					if(currentItem.hasClass("hassub")){
        					govNav.showhide(currentItem, 'hide',govNav.setting);
    					}
    	        	}
    	        break;

    	        case 39: // right - select first item in the next sub list
    	        	var nextItem=currentItem.closest("li").find("ul li:first");
    	        	if(nextItem.length){
    	        		nextItem.find("> a").focus();
    	        	}
    	        	if(nextItem.hasClass("hassub")){
    	        		govNav.showhide(nextItem, 'show',govNav.setting);
    					if(currentItem.hasClass("hassub")){
    	        			govNav.showhide(currentItem, 'hide',govNav.setting);
    	        		}
    	        	}
    	        break;

    	        case 40: // down - open next item in the current list

    	        	var nextItem=currentItem.closest("li").next("li");
    	        	if(currentItem.closest("#govNavMenu").length<1){
    	        		nextItem=$("#govNavMenu ul.firstLevel li:first");
    	        	}

    	        	if(nextItem.length){
    	        		nextItem.find("> a").focus();
    	        	}
    	        	if(nextItem.hasClass("hassub")){
    	        		govNav.showhide(nextItem, 'show',govNav.setting);
    					if(currentItem.hasClass("hassub")){
    	        			govNav.showhide(currentItem, 'hide',govNav.setting);
    	        		}
    	        	}
    	        break;

    	        default: return; // exit this handler for other keys
    	    }
    	    e.preventDefault(); // prevent the default action (scroll / move caret)
    	}else if($(".explore ul:visible").length>0){
    		var currentItem= $(":focus");
    	    switch(e.which) {

    	        case 38: // up - open previous item in the current list
    	        	var prevItem=currentItem.closest("li").prev("li");
    	        	if(prevItem.length){
    	        		prevItem.find("> a").focus();
    	    		}
    	        break;

    	        case 40: // down - open next item in the current list
    	        	if(currentItem.hasClass("explore")){
    	    			//select first
    	        		currentItem.find("ul li:first > a").focus();
    	    		}else{
        	        	var nextItem=currentItem.closest("li").next("li");
        	        	if(nextItem.length){
        	        		nextItem.find("> a").focus();
        	        	}
    	    		}
    	        break;

    	        default: return; // exit this handler for other keys
    	    }
    	    e.preventDefault(); // prevent the default action (scroll / move caret)
    	}
	});
	$(".explore").on("click", function(e) {
	    var list = $(this).find("ul");
		if(!list.is(':visible')){
		    list.slideDown(200, 'linear', function () { });
		} else {
		    list.slideUp(200, 'linear', function () { });
		}
	});

	// Submit the search query when the search icon is clicked
	// Applies to the global search and burger menu theme search
    $(".search-trigger").on("click", function(e) {
    	var currentForm = $(e.currentTarget).closest("form");
    	if(currentForm.find(".searchbox").val() == ''){
    		alert("Please enter one or more search terms");
    		return false;
    	} else {
    		$(currentForm).submit();
    	}
    })

    $(".tile-sort-button").on("click", function(e) {
    	if($(this).hasClass("sortedByOrderWeight")) {
    		sortTiles("div.homepage-theme-tiles", "alphabetical");
    		$(this).removeClass("sortedByOrderWeight").addClass("sortedByAlphabetical");
    		$(this).attr("src", "/StaticWebResources/static/gov3/images/az-sort-button-on.png");
    		$(this).attr("alt", "Sort by popularity");
    		$(this).attr("title", "Sort by popularity");
    	}
    	else if($(this).hasClass("sortedByAlphabetical")) {
    		sortTiles("div.homepage-theme-tiles", "orderWeight");
    		$(this).removeClass("sortedByAlphabetical").addClass("sortedByOrderWeight");
    		$(this).attr("src", "/StaticWebResources/static/gov3/images/az-sort-button-off.png");
    		$(this).attr("alt", "Sort alphabetically");
    		$(this).attr("title", "Sort alphabetically");
    	}
		// Reset the first/last classes so the arrow styling is updated
		$(".homepage-theme-tiles .homepage-tile").removeClass("first last");
		$(".homepage-theme-tiles .homepage-tile").first().addClass("first");
		$(".homepage-theme-tiles .homepage-tile").last().addClass("last");
    });


    // cleanup for Facebook RSS feed entries
    cleanFacebookFeedEntries();

	// reset the top padding on the content
	var headerHeight = $("#header-main").height();
	var topOffset = headerHeight + 5;
	$("#themeTemplate, #subthemeTemplate, #topicTemplate").css("padding-top", topOffset).css("background-position", "right " + topOffset + "px");

	//Fix z-index youtube video embedding
	$(document).ready(function (){
	    $('iframe').each(function(){
	        var url = $(this).attr("src");
	        if(url.indexOf("youtube") > -1) {
	        	$(this).attr("src", url + "?wmode=transparent");
	    	}
	    });
	});

	// Clear out menu searchbox query suggestions when the user hovers away from the current theme
	$("#govMainMenu > ul > li").hover(function() {
		$("#govMainMenu > ul > li").find(".menu-searchbox").val("").addClass("placeholder");
		$("#govMainMenu > ul > li").find(".ss-gac-m").children().remove();
		$("#govMainMenu > ul > li input").blur();
	});

	// Clear cached query suggestions when focus goes into a search field
	$("input.searchbox, input.tile-searchbox, input.menu-searchbox").focus(function() {
		console.log("clearing query suggestions");
		ss_cached = [];
		ss_qshown = null;
	});

	// [RA-368] CS - when focus goes into a burger menu search field, force a scroll to top of page (fix for iPad landscape view)
	$("input.menu-searchbox").focus(function() {
		$("body").scrollTop(0);
	});

});

$(document).mouseup(function(e) {
	var touchenabled = !!('ontouchstart' in window) || !!('ontouchstart' in document.documentElement) || !!window.ontouchstart || !!window.Touch || !!window.onmsgesturechange || (window.DocumentTouch && window.document instanceof window.DocumentTouch);
	var target = $(e.target);

	// DATABC EDIT
	// Close the navigation menu when there is a click on the page somewhere other than the menu button or within the menu
	if(!target.hasClass("menu-button") && !target.parent().hasClass("menu-button") && target.closest("#govNavMenu").length == 0) {
		//$("#govNavMenu").removeClass("expanded").addClass("hidden");
		$("#header-main-row2").removeClass("in").attr('style', '');
	}

	// DATABC EDIT
	// Close the search box when there is a click on the page somewhere other than the search box or within the search box
	if(!target.hasClass("search-button") && !target.parent().hasClass("search-button") && target.closest(".header-search").length == 0) {
		$(".header-search").removeClass("in").removeClass('overflow').attr('style', '');
	}

	// Close any navigation tile menus
    $(".explore ul").not(target.closest(".explore").find("ul")).slideUp(200, 'linear', function () { });

});

var scrollTimer;
$(window).on("scroll", function() {

	// Clear timeout if one is pending
	if(scrollTimer) {
		clearTimeout(scrollTimer);
	}
	// Set timeout
	scrollTimer = setTimeout(function() {
		/*
		 * Re-position the "Back to top" button if it is touching the footer
		*/

//		console.log("$('#footer').offset().top: " + $("#footer").offset().top);
//		console.log("$('#footer').height(): " + $("#footer").height());
//		console.log("$(window).scrollTop(): " + $(window).scrollTop());
//		console.log("$(window).height(): " + $(window).height());
//		console.log("$(window).scrollTop() + $(window).height(): " + ($(window).scrollTop() + $(window).height()));

		if($(window).scrollTop() > 0) {
			$(".back-to-top").show();
		} else {
			$(".back-to-top").hide();
		}

		// Check if the footer is within the viewport and switch the position of the button accordingly
		var windowBottomCoordinate = $(window).scrollTop() + $(window).height();
		if(windowBottomCoordinate > $("#footer").offset().top) {
			$(".back-to-top").addClass("footer-overlap");
		} else {
			$(".back-to-top").removeClass("footer-overlap");
		}

		/*
		 * When the page is scrolled in desktop mode, collapse the header
		*/
	/*  DATABC OVERRIDE
		var scrollPosition = $(window).scrollTop();
		if(scrollPosition > 50 && $(window).width() >= 768) {
			if(!$("#header").hasClass("collapsed-header")) {
				$("#header-main > .container").hide();
				$("#header").addClass("collapsed-header");
				$("#header-main > .container").fadeIn("300");
			}
		} else {
			if($("#header").hasClass("collapsed-header")) {
				$("#header-main > .container").hide();
				$("#header").removeClass("collapsed-header");
				$("#header-main > .container").fadeIn("300", function() {
					// After the full header is fully loaded, readjust the top padding on content
					adjustContentPadding();
				})
			}
		}
		*/
	addScrollableBurgerMenu();

	}, 100); // Timeout in msec
});

// When page is resized
$(window).on("resize", function() {
	adjustContentPadding();
	addScrollableBurgerMenu();
});

// When page is loaded or window is resized
$(window).on("load resize", function() {

	// workaround for left nav collapsing on page load
	// Bootstrap known issue - https://github.com/twbs/bootstrap/issues/14282
	$('#leftNav').collapse({'toggle': false})

	//hide mobile topic menu
	 if ($(this).width() < 767) {
			$("#leftNav").removeClass('in')
	 }else{
			$("#leftNav").addClass('in').attr('style','')
	 }

	$('#leftNav').collapse({'toggle': true})

	// When our page loads, check to see if it contains and anchor
	scroll_if_anchor(window.location.hash);

	// Intercept all anchor clicks in the accessibility section and page content
	$("#access").on("click", "a", scroll_if_anchor);
	$("#main-content").on("click", "a", scroll_if_anchor);

});

// DATABC EDIT
function toggleHeaderElements(event) {
	var dataTarget = $(event).attr('data-target');
	var collapseTarget;

	if(dataTarget == "#header-main-row2") {
		collapseTarget = ".header-search";
	}
	else {
		collapseTarget = "#header-main-row2";
	}

	$(collapseTarget).removeClass('overflow').removeClass('in').attr('style', '');
}


function ieVersion() {
    var ua = window.navigator.userAgent;
    if (ua.indexOf("Trident/7.0") > 0)
        return 11;
    else if (ua.indexOf("Trident/6.0") > 0)
        return 10;
    else if (ua.indexOf("Trident/5.0") > 0)
        return 9;
    else
        return 0;  // not IE9, 10 or 11
}

var animate = 1;

function toggleFooter(event) {

	var ua = window.navigator.userAgent;
    var msie = ua.indexOf("MSIE ");
    if(msie < 0){
    	//check for IE 11
    	msie = ieVersion();
    }

	$("#footerCollapsible").css("height", $("#footerCollapsible").height());

	if (msie > 0) {
		$("#footerCollapsible").slideToggle(0, function() {
			// expand
			if($(this).is(":visible")) {
				$("#footer").addClass("expanded");
				$("#footerToggle a.footerExpand").hide();
				$("#footerToggle a.footerCollapse").show();
			}
			// collapse
			else {
				$("#footer").removeClass("expanded");
				$("#footerToggle a.footerExpand").show();
				$("#footerToggle a.footerCollapse").hide();
			}

			$('html, body').animate({
				scrollTop: $(document).height()
			}, 'slow');
		});
	}
	else{
		$("#footerCollapsible").slideToggle('slow', function() {
			// expand
			if($(this).is(":visible")) {
				$("#footer").addClass("expanded");
				$("#footerToggle a.footerExpand").hide();
				$("#footerToggle a.footerCollapse").show();
				animate = 0;
			}
			// collapse
			else {
				$("#footer").removeClass("expanded");
				$("#footerToggle a.footerExpand").show();
				$("#footerToggle a.footerCollapse").hide();
				animate = 1;
			}
		});

		if (animate == 1){
			$('html, body').animate({
				scrollTop: $(document).height()
			}, 'slow');
			var temp = animate;		//get animate var
		}
	}
}

function sortTiles(selector, sortType) {
    $(selector).children("div.homepage-tile").sort(function(a, b) {
        // Sort based on the Tile title
    	if(sortType == "alphabetical") {
        	var stringA = $(a).find(".tile-text > .title > a").text().toUpperCase();
            var stringB = $(b).find(".tile-text > .title > a").text().toUpperCase();
            return (stringA < stringB) ? -1 : (stringA > stringB) ? 1 : 0;
        }
    	// Sort based on the Tile order weight
        else if(sortType == "orderWeight") {
        	var intA = parseInt($(a).attr("data-order"));
            var intB = parseInt($(b).attr("data-order"));
            return (intA < intB) ? -1 : (intA > intB) ? 1 : 0;
        }
    }).appendTo(selector);
}

/**
 * Check an href for an anchor. If exists, and in document, scroll to it.
 * If href argument omitted, assumes context (this) is HTML Element,
 * which will be the case when invoked by jQuery after an event
 */
function scroll_if_anchor(href) {
   href = typeof(href) == "string" ? href : $(this).attr("href");

   // If href missing, ignore
   if(!href) return;

   // Do not trigger on mobile view
   if($(window).width() < 768) {
	   return;
   } else {
	   var fromTop = $("#header-main").height() + 20;

	   // Case #1 - href points to a valid anchor on the same page in the format "#foo"
	   if(href.charAt(0) == "#") {

		   var $target = $(href);

		   // If no element with the specified id is found, check for name instead (some of the GOV2 content is like this)
		   if(!$target.length)  {
			   $target = $("a[name='" + href.substring(1) + "']");
		   }

		   // Older browsers without pushState might flicker here, as they momentarily jump to the wrong position (IE < 10)
	       if($target.length) {
	           $('html, body').animate({ scrollTop: $target.offset().top - fromTop });
	       }
	   }
	   // Case #2 - href points to a valid anchor on the same page in the format "/gov/current/page#foo"
	   else if(href.indexOf("#") > -1) {

		   var targetHrefPath = href.split("#")[0];
		   var targetHrefHash = href.split("#")[1];

		   if(href.indexOf(location.pathname) > -1) {
			   var $target = $("#" + targetHrefHash);

			   if(!$target.length)  {
				   $target = $("a[name='" + targetHrefHash + "']");
			   }

		       if($target.length) {
		           $('html, body').animate({ scrollTop: $target.offset().top - fromTop });
		       }
		   }
	   }
   }
}

/**
 * Clean up links and image references coming from the Facebook Graph JSON feed.
 */
function cleanFacebookFeedEntries() {

	try {

	    // Process all feed entries and perform all cleanup required for Facebook feed items
	    $(".feedEntry").each(function() {
	    	var feedEntry = $(this);

	    	// Change image references so that a larger image is retrieved
		    feedEntry.find("img").each(function() {
		    	// https://fbexternal-a.akamaihd.net/safe_image.php?d=AQBJxwDdy74cYCcs&w=158&h=158&url=http%3A%2F%2Froyalbcmuseum.bc.ca%2Fassets%2Faboriginal-festival-770-360.jpg
		    	if($(this).attr("src").indexOf("https://fbexternal-a.akamaihd.net/safe_image.php") > -1) {
		    		// Images hosted on facebook
		    		if($(this).attr("src").indexOf("graph.facebook.com") > -1) {
			    		// if w=XXX and h=XXX parameters are specified, remove them so a large image is retrieved
			    		var cleanImgSrc = $(this).attr("src").replace(/w=[0-9]{3}&h=[0-9]{3}/gi, "");
			    		$(this).attr("src", cleanImgSrc);
		    		}
		    		// Images hosted externally
		    		else {
		    			var cleanImgSrc = $(this).attr("src").split("&url=")[1];

		    			// remove any additional parameters
		    			cleanImgSrc = cleanImgSrc.split("&")[0];
			    		cleanImgSrc = unescape(cleanImgSrc);
			    		$(this).attr("src", cleanImgSrc);
		    		}
		    	}

		    	// https://scontent.xx.fbcdn.net/hphotos-xtf1/v/t1.0-9/s130x130/11412352_1006579099360382_2608795475977532679_n.jpg?oh=9d08e3210a82714ba13a2de37d803c59&oe=56329FB4
		    	if($(this).attr("src").indexOf("https://scontent.xx.fbcdn.net") > -1) {
		    		//bigger_image="https://graph.facebook.com/" + picture_url_from_facebook.match(/_\d+/)[0].slice(1) + "/picture?type=normal";
		    		var imageId = $(this).attr("src").split("_")[1];
		    		cleanImgSrc = "https://graph.facebook.com/" + imageId + "/picture?type=normal";
		    		$(this).attr("src", cleanImgSrc);
		    	}
		    });

		    // Replace plain text URLs with a hyperlink
	    	feedEntry.find("p").each(function() {
		    	var inputText = $(this).text();
		        var replacedText = "";

		    	// Replace Links beginning with http://, https://, or www.
		    	var replacePattern1 = /(\b(https?:\/\/|www\.)[-A-Z0-9+&@#\/%?=~_|!:,.;]*[-A-Z0-9+&@#\/%=~_|])/gim;
		        replacedText = inputText.replace(replacePattern1, '<a href="$1">$1</a>');

		        // Add the protocol to any links that omit it
		        replacedText = replacedText.replace("<a href=\"www.", "<a href=\"http://www.");

		        // Facebook hashtag links
		        var replacePattern2 = /(^|\s)#([a-z\d-]+)/gi;
		        replacedText = replacedText.replace(replacePattern2, "$1<a href='http://www.facebook.com/hashtag/$2'>#$2</a>");

		    	$(this).html(replacedText);
		    });

	    	// Link up any message_tags found in the facebook post message
	    	feedEntry.find("span.messageTag").each(function() {
	    		var messageTag = $(this);
		    	//console.log(messageTag.text());
		    	var tag = messageTag.text();
		    	var tagName = tag.split("::")[0];
		    	var tagId = tag.split("::")[1];

		    	//console.log("Tag Name: " + tagName);
		    	//console.log("Tag ID: " + tagId);

		    	// Replace each tag found in the message body with a link
		    	feedEntry.find("p").each(function() {
		    		var pElement = $(this);
		    		var html = pElement.html();
		    		html = html.replace(tagName, "<a href='http://www.facebook.com/" + tagId + "'>" + tagName + "</a>");
		    		$(this).html(html);
		    		//console.log("New HTML: " + html);
		    	})
		    });

			// Open all feed entry links in a new window
		    feedEntry.find("a").each(function() {
		        $(this).attr("target", "_blank");
		    });
	    });
	}

	catch(err) {
		console.log("Error when attempting to clean Facebook RSS feed data");
		return;
	}
}

/**
 * If the burger menu overflows beyond the window height, make it scrollable so that all nav links can be accessed.
 */
function addScrollableBurgerMenu() {

	var $menu = $("#govNavMenu");

	// Reset the burger menu styles to normal
	$menu.css("height", "auto");
	$menu.css("width", "");
	$menu.css("overflow-y", "initial");
	$menu.removeClass("scrollable");

	// Position of the burger menu from the top of the page (px)
	var menuTopOffset = $("#header-main > .container").height();

	// If the QA banner is on the page, need to add its height to menuTopOffset
	if($(".qa-banner").length) {
		menuTopOffset = menuTopOffset + $(".qa-banner").height();
	}

	// If the header is in collapsed mode, need to add height of "header-links" to menuTopOffset
	if($("#header").hasClass("collapsed-header")) {
		menuTopOffset = menuTopOffset + $("#header-links").height();
	}

	//var overflow = $menu.offset().top + $menu.height() - $(window).height();
	var overflow = menuTopOffset + $menu.height() - $(window).height();
	//console.log("overflow:" + overflow);

	// If overflow is positive, burger menu is too long for the current window height, and some of the links may not be visible to the user
	// To fix this, set the burger menu height so that it goes to the bottom of the window, add a vertical scrollbar, and adjust other values as necessary
	if($(window).width() >= 750 && overflow > 0) {
		var newMenuHeight = $menu.height() - overflow;
		$menu.height(newMenuHeight);
		$menu.css("width", "auto");
		$menu.css("overflow-y", "scroll");
		$menu.addClass("scrollable");
	}
}

/**
 * Search box typing event. Configure the query suggestion variables based on which search box is active
 */
var timeoutId = 0;
function searchBoxKeypress(event, numDelay, searchBoxIndex) {
	// Remove placeholder text when the user starts typing in the search field
	var $textInputField = $(event.target);
    if($textInputField.val() == '') {
    	$textInputField.addClass('placeholder');
	} else {
		$textInputField.removeClass('placeholder');
	}

    // Burger menu search boxes
    if($textInputField.hasClass("menu-searchbox")) {
		window.ss_form_element = 'menu_suggestion_form_' + searchBoxIndex; // search form
		window.ss_popup_element = 'menu_search_suggest_' + searchBoxIndex; // search suggestion drop-down
    }
    // Tile flyout search boxes
    else if($textInputField.hasClass("tile-searchbox")) {
    	window.ss_form_element = 'tile_suggestion_form_' + searchBoxIndex; // search form
    	window.ss_popup_element = 'tile_search_suggest_' + searchBoxIndex; // search suggestion drop-down
    }
    // Mobile menu search boxes
    else if($textInputField.hasClass("mobile-menu-searchbox")) {
    	window.ss_form_element = 'mobile_menu_search_form_' + searchBoxIndex; // search form
    	window.ss_popup_element = 'mobile_menu_search_suggest_' + searchBoxIndex; // search suggestion drop-down
    }
    else {
    	window.ss_form_element = 'suggestion_form'; // search form
    	window.ss_popup_element = 'search_suggest'; // search suggestion drop-down
    }

	// Clear the cache of suggested queries
//	ss_cached = [];
//	ss_clear();
	console.log(window.ss_form_element);
	console.log(window.ss_popup_element);

	// If the keypress is an arrow (up/down/left/right), call the ss_handleKey function without using a timeout.
	// Otherwise, the user is typing the search query. Use the timeout so the search app is not flooded with requests.
    if(event.which == 37 || event.which == 38 || event.which == 39 || event.which == 40) {
    	ss_handleKey(event);
    } else {
    	clearTimeout(timeoutId);
    	timeoutId = setTimeout(function () {
    		ss_handleKey(event);
    	}, numDelay);
    }

}

/**
 * Reset the top padding on the content (to compensate for the fixed header)
 */
function adjustContentPadding() {
	var headerHeight = $("#header-main").height();
	var topOffset = headerHeight + 5;
	$("#themeTemplate, #subthemeTemplate, #topicTemplate").css("padding-top", topOffset).css("background-position", "right " + topOffset + "px");
}

/**
 * Handlers for "Information Tiles"
 */

$(window).on("load resize",function(e) {

	// Keep the width of the query suggest dropdown equal to the tile content width
	$(".homepage-tile").each(function() {
		var querySuggestWidth = $(this).width();
		// If a homepage theme tile ("How may we help you" section), need to account for the icon width
		if($(this).find(".tile-icon").length > 0 && $(window).width() > 768) {
			querySuggestWidth = querySuggestWidth - $(this).find(".tile-icon").outerWidth();
		}
		$(this).find("table.ss-gac-m").width(querySuggestWidth);
	});

	if($(window).width() < 768) {
		// Calculate the width of the mobile menu search elements dynamically
		var mobileNavWidth = $(window).width() - 50;
		$(".mobile-menu-search > .homepage-tile").width(mobileNavWidth);
	}
});

$(document).ready(function() {

	// Handler for when the magnifying glass icon is clicked
    $(".homepage-theme-tiles .tile-search, .mobile-menu-search .tile-search").on("click", function(e) {

    	e.stopPropagation();

    	var $homepageTile = $(e.currentTarget).closest(".homepage-tile");
    	var $flyout = $homepageTile.find(".tile-search-flyout");

    	// If there is already a flyout being animated, do not proceed
    	if($(".tile-search-flyout").is(":animated")) return;

    	// Flyout is already expanded, so execute the search
    	if($homepageTile.hasClass("flyout-expanded")) {
    		var $form = $flyout.find("form");
  	    	$form.submit();
    	}
    	// Expand flyout from right to left
    	else {
    		closeTileFlyouts();

    		$homepageTile.addClass("flyout-expanded");

    		// Slide the flyout from right to left
        	($flyout).animate({
        	    left: "0"
        	}, 800, function() {
            	$flyout.find("input[name='q']").focus();
        	} );
    	}
    })

	// Handler for when a tile flyout input field is clicked into
    $(".tile-search-flyout input[name='q']").on("click", function(e) {
    	e.stopPropagation();
    })

	// Handler for when the Popular Services search button is clicked
    $(".popular-services-search .tile-search").on("click", function(e) {
    	var $homepageTile = $(e.currentTarget).closest(".homepage-tile");
    	var $flyout = $homepageTile.find(".tile-search-flyout");
    	var $form = $flyout.find("form");
  	    $form.submit();
	})

	// Handler for submission of the flyout forms. Validate the form input before submitting
	$(".tile-search-flyout > form").submit(function(e) {
		var $textInput = $(this).find("input[name='q']");
	    if($textInput.val() == '') {
		    e.preventDefault();
	    	closeTileFlyouts();
		}
	})
});

function closeTileFlyouts() {

	// If there is a flyout currently being animated, do not proceed
	if($(".tile-search-flyout").is(":animated")) return;

	$(".homepage-tile").removeClass("flyout-expanded");
	// Reset text inputs
	$(".homepage-tile").find("input[name='q']").val("");
	// Add placeholder background image
	$(".homepage-tile").find("input[name='q']").addClass("placeholder");
	// Reset left property so the flyout doesn't display
	$(".homepage-tile .tile-search-flyout").css("left", "");
	// Remove any query suggestions
	$(".homepage-tile table.ss-gac-m").empty();
}
