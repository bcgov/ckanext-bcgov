$("#imageFile").change(function() {
	var filename = $("#imageFile").val().replace("C:\\fakepath\\","");
	$("#new_image_filename").val(filename);
});

$("#selectImageButton").click(function() {
//	console.log("Select Image button Clicked!");
	$("#imageFile").trigger('click');
});

//$("#uploadButton").bind('click', function (e) {
//	$('#imageFile').fileupload('add', {
//		fileInput: $('#imageFile')
//	});
/*	$('#imageFile').fileupload({
		add: function (e, data) {
			data.submit();
		},
		done: function (e, data) {
			alert('done');
			$("#removeImageBtn").removeAttr('disabled');
			$("#uploaded_image").val(data);
			$("#field-image_delete").val('0');
			$('#dataset_img').attr('src', data).load(function(){
			    this.width;  
			});
		}
	});
*///	var new_filename =  $("#new_image_filename").val();
//	
//	var data = new FormData();
//	data.append("exisiting_filename", $("#uploaded_image").val());
//	var requesst = $.ajax({
//							url: "/dataset/upload_file",
//        					type: 'POST',
//        					data: data,
//        					dataType: 'text/html',
//        					processData: false,
//        					contentType: false,
//        					success : function (data) {
//        						$("#removeImageBtn").removeAttr('disabled');
//        						$("#uploaded_image").val(data);
//        						$("#field-image_delete").val('0');
//        						$('#dataset_img').attr('src', data).load(function(){
//        						    this.width;  
//        						});
//        					}
//    				});
//});

$("#removeImageBtn").click(function() {
	
	
//	$("#uploaded_image").val('');
	$("#field-image_delete").val(1);
	$("#new_image_filename").val('');
	$('#dataset_img').attr('src', '');
	$("#removeImageBtn").attr('disabled', 'disabled');	
/*	
	var data = new FormData();
	data.append("filename", $("#uploaded_image").val());
	data.append("id", $("#edc_pkg_id").val());

	var requesst = $.ajax({
							url: "/dataset/remove_file",
        					type: 'POST',
        					data: data,
        					dataType: 'text',
        					processData: false,
        					contentType: false,
        					success : function (data) {
        						$("#removeImageBtn").attr('disabled', 'disabled');
        						$("#uploaded_image").val('');
        						$("#new_image_filename").val('');
        						$('#dataset_img').attr('src', '');
        					}
    				});
    				
*/
});

$(function() {
	var $dataset_image = $("#dataset_img");
	var image_src = $dataset_image.attr("src");
	
	if (image_src) {
		$("#removeImageBtn").removeAttr('disabled');
	}
	else {
		$("#removeImageBtn").attr('disabled', 'disabled');	
	}
	
	$('#imageFile').fileupload({
		url: '/dataset/upload_file',
		forceIframeTransport: false,
		dataType: 'json',
		autoUpload: true,
		add: function (e, data) {
			data.context = $('#uploadButton').click(function () {
				data.submit();
			});
		},
		done: function (e, data) {
			$("#removeImageBtn").removeAttr('disabled');
			$("#uploaded_image").val(data.result.files[0].url);
			$("#field-image_delete").val('0');
			$('#dataset_img').attr('src', data.result.files[0].url).load(function(){
			    this.width;  
			});
		}
	}); 
		
});