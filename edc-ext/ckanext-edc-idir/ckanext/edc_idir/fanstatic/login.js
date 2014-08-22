
            $("#login").submit(function(e)
                {   $('.flash-messages').html('')
                    $('#field-login').each(function() 
                        {
                            if ($(this).val() == '') 
                                {   
                                    $(this).addClass('highlight');
                                    $('.flash-messages').append($('<div>').addClass('alert alert-error').html('* Name is required.'));
                                    e.preventDefault();
                                    
                                }
                        }
                    );
                    $('#field-password').each(function() 
                        {
                            if ($(this).val() == '') 
                                {   
                                    $(this).addClass('highlight');
                                    $('.flash-messages').append($('<div>').addClass('alert alert-error').html('* Password is required.'));
                                    e.preventDefault();
                                    
                                }
                        }
                    );


                    
                }   
            );
        