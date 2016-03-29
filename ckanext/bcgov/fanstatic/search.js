
(function($) {
    $(document).ready(function() {
        // constructs the suggestion engine
        var engine = new Bloodhound({
          name: 'package_search',
          local: [],
          remote: {
            url: '/api/3/action/package_autocomplete?q=%QUERY',
            filter: function(response) {
                return response.result;
            }
          },
          datumTokenizer: function(d) {
            return Bloodhound.tokenizers.whitespace(d.title);
          },
          queryTokenizer: Bloodhound.tokenizers.whitespace
        });



        // kicks off the loading/processing of `local` and `prefetch`
        engine.initialize();

        $('.search:not(.gov)').typeahead({
          hint: true,
          highlight: true,
          minLength: 4
        },
        {
          name: 'datasets',
          displayKey: 'title',
          // `ttAdapter` wraps the suggestion engine in an adapter that
          // is compatible with the typeahead jQuery plugin
          source: engine.ttAdapter()
        });
    });

    $(document).on('click', '.facet-expand-collapse', function() {
    	var id = $(this).attr('id');
    	var target_class = ".more-"+ id;
    	if ($(this).hasClass("expanded")) {
    		$(this).removeClass("expanded");
    		$(target_class).each( function() {
    			$(this).css("display", "none");
    		});
    	}
    	else {
    		$(this).addClass("expanded");
    		$(target_class).each( function() {
    			$(this).css("display", "block");
    		});
    	}
    });
    
    $(document).on('typeahead:selected', function(e, suggestion, dataset) {
      var name = suggestion.name;
      window.location.href = window.location.protocol+"//"+window.location.host + '/dataset/' + name;
    });
    
    $("#btn-search-submit").on('click', function(){    
    	var search_query = $("#field-search-query").val();
    	
    	if (search_query) {
    		$('#field-order-by').val('score desc, record_publish_date desc');
    	}
    });
    
})(jQuery);


