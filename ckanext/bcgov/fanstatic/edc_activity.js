function remove_actor_link() {
	$(".actor>a").each(function(){
		   user_name  = $(this).text();
		   console.log(user_name);
		   $(this).replaceWith(user_name);
		});	
}

$(document).bind('DOMSubtreeModified',function(){
	remove_actor_link();	
});
	
