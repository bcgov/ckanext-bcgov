
(function($) {
    $(document).ready(function() {
        $('#permalinkLink').click(function(e){
            $('#permalinkModal').modal();
            $('#permalinkModal').show();
            e.preventDefault();
            e.stopPropagation();
        });

        $('#permalinkModal span.close').click(function(e){
            $('#permalinkModal').hide();
        });
        
        $('#copyPermalink').click(function(e) {
            $('#permalinkLinkInput').select();
            document.execCommand("copy");
            $('#permalinkCopiedStatus').innerHTML = "Copied";
        });
    });
})(jQuery);