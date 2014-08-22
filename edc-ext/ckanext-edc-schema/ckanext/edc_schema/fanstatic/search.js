
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

        $('.search').typeahead({
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
})(jQuery);