//$("#wb-pnl").html("<header class=\"modal-header\"><div class=\"modal-title\">Menu</div></header>  <div class=\"modal-body\">    <section class=\"srch-pnl\">        <form class=\"section site-search simple-input\" action=\"http://www2.gov.bc.ca/gov/search\" method=\"get\" onsubmit=\"javascript:this.keywords.value=this.keywords.value.toLowerCase();\">          <div class=\"field\">            <label for=\"field-sitewide-search-imprt\">Search</label>            <input type=\"hidden\" value=\"2E4C7D6BCAA4470AAAD2DCADF662E6A0\" name=\"id\">            <input type=\"text\" onkeyup=\"searchBoxKeypress(event)\" autocomplete=\"off\" value=\"\" name=\"q\" placeholder=\"Enter a keyword or phrase to search\" class=\"searchbox\" id=\"global-search-imprt\">            <button class=\"btn-search\" type=\"submit\"><i class=\"icon-search\"></i></button>          </div>        </form>    </section>    <nav role=\"navigation\" typeof=\"SiteNavigationElement\" id=\"sec-pnl\" class=\"sec-pnl wb-menu\"><h3></h3>      <ul class=\"list-unstyled mb-menu\" role=\"menu\">        <li class=\"no-sect\"><a class=\"mb-item\" role=\"menuitem\" aria-setsize=\"5\" aria-posinset=\"1\" tabindex=\"0\" href=\"/\">Datasets</a></li>        <li class=\"no-sect\"><a class=\"mb-item\" role=\"menuitem\" aria-setsize=\"5\" aria-posinset=\"2\" tabindex=\"-1\" href=\"/organization\">Organizations</a></li>        <li class=\"no-sect\"><a class=\"mb-item\" role=\"menuitem\" aria-setsize=\"5\" aria-posinset=\"3\" tabindex=\"-1\" href=\"/group\">Groups</a></li>        <li><details><summary class=\"mb-item\" role=\"menuitem\" aria-setsize=\"5\" aria-posinset=\"4\" aria-haspopup=\"true\" tabindex=\"-1\"> Stay Up To Date</summary>          <ul class=\"list-unstyled mb-sm\" role=\"menu\" aria-expanded=\"false\" aria-hidden=\"true\">            <li><a role=\"menuitem\" aria-setsize=\"3\" aria-posinset=\"1\" tabindex=\"-1\" href=\"/feeds/recent.rss\" title=\"Subscribe to New data\"><span>Subscribe to New Data</span></a></li>            <li><a role=\"menuitem\" aria-setsize=\"3\" aria-posinset=\"2\" tabindex=\"-1\" href=\"http://.disqus.com/latest.rss\">Subscribe to Catalogue Comments</a></li>            <li><a role=\"menuitem\" aria-setsize=\"3\" aria-posinset=\"3\" tabindex=\"-1\" href=\"http://blog.data.gov.bc.ca/feed/\" target=\"_blank\">Subscribe to Blog Posts</a></li>          </ul></details>        </li>        <li class=\"no-sect\"><a class=\"mb-item\" role=\"menuitem\" aria-setsize=\"5\" aria-posinset=\"5\" tabindex=\"-1\" href=\"/about\">About</a></li>      </ul>    </nav>    <nav role=\"navigation\" typeof=\"SiteNavigationElement\" id=\"sm-pnl\" class=\"sm-pnl wb-menu\">      <h3>DataBC</h3>      <ul class=\"list-unstyled mb-menu\" role=\"menu\">        <li class=\"no-sect\"><a class=\"mb-item\" role=\"menuitem\" aria-setsize=\"6\" aria-posinset=\"1\" tabindex=\"0\" href=\"''/dbc/about/index.page\">What is DataBC?</a></li>        <li class=\"no-sect\"><a class=\"mb-item wb-navcurr\" role=\"menuitem\" aria-setsize=\"6\" aria-posinset=\"2\" tabindex=\"-1\" href=\"/dataset\" title=\"databc Home\">Data Catalogue</a></li>        <li class=\"no-sect\"><a class=\"mb-item\" role=\"menuitem\" aria-setsize=\"6\" aria-posinset=\"3\" tabindex=\"-1\" href=\"''/dbc/geographic/index.page\">Geographic Services</a></li>        <li class=\"no-sect\"><a class=\"mb-item\" role=\"menuitem\" aria-setsize=\"6\" aria-posinset=\"4\" tabindex=\"-1\" href=\"http://blog.data.gov.bc.ca/\">Blog</a></li>        <li class=\"no-sect\"><a class=\"mb-item\" role=\"menuitem\" aria-setsize=\"6\" aria-posinset=\"5\" tabindex=\"-1\" href=\"http://developer.gov.bc.ca/\">Developers</a></li>        <li class=\"no-sect\"><a class=\"mb-item\" role=\"menuitem\" aria-setsize=\"6\" aria-posinset=\"6\" tabindex=\"-1\" href=\"''/forms/dbc/contact/index.html\">Contact</a></li>      </ul>    </nav>  </div><button class=\"mfp-close overlay-close\" title=\"Close: Menu (escape key)\">×<span class=\"wb-inv\"> Close: Menu (escape key)</span></button>")
$(document).ready(function(){
    createModalContent($("#wb-pnl"));
    $("#hidden-btn").click(function(){
        $("#wb-pnl").toggle();
    $(".overlay-close").click(function(){
        $("#wb-pnl").hide();
    })
    });
});

   /*
   create the html of dropdown menu for smaller browser screens
   */
   createModalContent = function($obj) {
     var $menubar = $(".wb-menu").find(".menu"),
         $menu = $menubar.find("> li > a"),
         $secnav = $("#wb-sec"),
         search = document.getElementById( "wb-srch"),
         panel = ""
         allProperties = [];
     if ( search !== null ) {
 			panel += "<section class='srch-pnl'>" +
 				search.innerHTML
 					.replace( /h2>/i, "h3>" )
 					.replace( /(for|id)="([^"]+)"/gi, "$1='$2-imprt'" ) +
 				"</section>";
 		}

    //add secondary menu
    if ( $secnav.length !== 0 ) {
			allProperties.push([
				$secnav.find( "> ul > li > *:first-child" ).get(),
				"sec-pnl",
				$secnav.find( "h2" ).html()
			]);
    }

    //add site menu
    if ( $menubar.length !== 0 ) {
			allProperties.push([
				$menu.get(),
				"sm-pnl",
				$(".wb-menu").find( "h2" ).html()
			]);
		}

    panel += createMobilePanelMenu(allProperties);
    // populate DOM
    $obj.html("<header class='modal-header'><div class='modal-title'>" +
			             "menu</div></header><div class='modal-body'>" +
			             panel + "</div>");
    $obj.addClass(" wb-overlay modal-content overlay-def wb-panel-r");
    closeText = "Close: Menu (escape key)";
    overlayClose = "<button class='mfp-close overlay-close " +
			"' title='" + closeText + "'>&#xd7;<span class='wb-inv'> " +
			closeText + "</span></button>";

		$obj.append( overlayClose );
   }

   /* The following funtions are copied from wet-boew.js */
   /**
   	 * @method createCollapsibleSection
   	 * @return {string}
     */
 	createCollapsibleSection = function( section, sectionIndex, sectionsLength, $items, itemsLength ) {

 		// Use details/summary for the collapsible mechanism
 		var k, $elm, elm, $item, $subItems,
 			$section = $( section ),
 			posinset = "' aria-posinset='",
 			menuitem = "role='menuitem' aria-setsize='",
 			sectionHtml = "<li><details>" + "<summary class='mb-item" +
 				( $section.hasClass( "wb-navcurr" ) || $section.children( ".wb-navcurr" ).length !== 0 ? " wb-navcurr'" : "'" ) +
 				"' " + menuitem + sectionsLength + posinset + ( sectionIndex + 1 ) +
 				"' aria-haspopup='true'>" + $section.text() + "</summary>" +
 				"<ul class='list-unstyled mb-sm' role='menu' aria-expanded='false' aria-hidden='true'>";

 		// Convert each of the list items into WAI-ARIA menuitems
 		for ( k = 0; k !== itemsLength; k += 1 ) {
 			$item = $items.eq( k );
 			$elm = $item.find( "> a, > details > summary" );
 			elm = $elm[ 0 ];
 			if ( elm.nodeName.toLowerCase() === "a" ) {
 				sectionHtml += "<li>" + $item[ 0 ].innerHTML.replace(
 						/(<a\s)/,
 						"$1 " + menuitem + itemsLength +
 							posinset + ( k + 1 ) +
 							"' tabindex='-1' "
 					) + "</li>";
 			} else {
 				$subItems = $elm.parent().find( "> ul > li" );
 				sectionHtml += createCollapsibleSection( elm, k, itemsLength, $subItems, $subItems.length );
 			}
 		}

 		return sectionHtml + "</ul></details></li>";
 	},
  /**
  * @method createMobilePanelMenu
  * @param {array} allProperties Properties used to build the menu system
  * @return {string}
  */
 createMobilePanelMenu = function( allProperties ) {
   var panel = "",
     sectionHtml, properties, sections, section, parent, $items,
     href, linkHtml, i, j, len, sectionsLength, itemsLength;

   // Process the secondary and site menus
   len = allProperties.length;
   for ( i = 0; i !== len; i += 1 ) {
     properties = allProperties[ i ];
     sectionHtml = "";
     sections = properties[ 0 ];
     sectionsLength = sections.length;
     for ( j = 0; j !== sectionsLength; j += 1 ) {
       section = sections[ j ];
       href = section.getAttribute( "href" );
       $items = $( section.parentNode ).find( "> ul > li" );
       itemsLength = $items.length;

       // Collapsible section
       if ( itemsLength !== 0 ) {
         sectionHtml += createCollapsibleSection( section, j, sectionsLength, $items, itemsLength );
       } else {
         parent = section.parentNode;

         // Menu item without a section
         if ( parent.nodeName.toLowerCase() === "li" ) {
           linkHtml = parent.innerHTML;

         // Non-list menu item without a section
         } else {
           linkHtml = "<a href='" +
             parent.getElementsByTagName( "a" )[ 0 ].href + "'>" +
             section.innerHTML + "</a>";
         }

         // Convert the list item to a WAI-ARIA menuitem
         sectionHtml += "<li class='no-sect'>" +
           linkHtml.replace(
             /(<a\s)/,
             "$1 class='mb-item' " + "role='menuitem' aria-setsize='" +
               sectionsLength + "' aria-posinset='" + ( j + 1 ) +
               "' tabindex='-1' "
           ) + "</li>";
       }
     }

     // Create the panel section
     panel += "<nav role='navigation' typeof='SiteNavigationElement' id='" +
       properties[ 1 ] + "' class='" + properties[ 1 ] + " wb-menu'>" +
       "<h3>" + properties[ 2 ] + "</h3>" +
       "<ul class='list-unstyled mb-menu' role='menu'>" +
       sectionHtml + "</ul></nav>";
   }

   return panel.replace( /list-group-item/gi, "" ) + "</div>";
 }
