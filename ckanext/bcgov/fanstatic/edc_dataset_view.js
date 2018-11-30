
(function($) {
    $(document).ready(function() {
        $('.show-disqus').click(function() {
            $('.comments-modal-btn').hide();
            $('#new-comment-box').show();
            var dsq = document.createElement('script'); dsq.type = 'text/javascript'; dsq.async = true;
            dsq.src = '//' + disqus_shortname + '.disqus.com/embed.js';
            (document.getElementsByTagName('head')[0] || document.getElementsByTagName('body')[0]).appendChild(dsq); 
            
      });

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
    
/*    $("#comment-submit").click(function() {
    	console.log("Testing comment submit");
		var data = new FormData();
			data.append("thread", disqus_identifier)
			data.append("author_email", 'test@test.com');
			data.append("author_name", 'Anonymous');
			data.append("message", $("#field-message").val());
		    var requesst = $.ajax({
		        					url: "/api/3/action/post_comment",
		        					type: 'POST',
		        					data: data,
		        					dataType: 'text',
		        					processData: false,
		        					contentType: false,
		        					success : function (data) {
		        						alert("Done");
		        					}
		    				});
    }); */
})(jQuery);