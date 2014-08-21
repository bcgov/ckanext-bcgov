(function($, wb) {

    var acceptedTerms = false;
    var promiseModal = $.Deferred();
    var $termsModal = $('#comment-terms-modal');
    var addCommentContext = '';
    var apiList = '/disqus/posts/list';
    var apiPostCreate = '/disqus/posts/create';
    var $threadContainer = $('#disqus_thread');
    var $numCommentsContainer = $('#disqus_num_comments');
    var $addCommentContainer = $('#disqus_add_comment');
    var $commentBox = $addCommentContainer.find('.message');
    var $messagesContainer = $('#disqus_messages');
    var $addCommentForm = $('#comment_box form');

    $(document).ready(function() {

        var commentDiv = $threadContainer.find('.post').clone();
        var emptyCommentDiv = $threadContainer.find('.empty').clone();
        var loaderDiv = $threadContainer.find('.loader').clone();
        $threadContainer.html(loaderDiv);

        var commentTheadJson;
        getCommentThread(disqus_identifier).done(function(json) {
            commentTheadJson = json;
            updateCommentCount(json.response.length);
            $addCommentContainer.show();

            if(json.response.length == 0) {
                $threadContainer.html(emptyCommentDiv);
            }
            else {
                $threadContainer.html('');
                var comments = json.response;
                comments = comments.reverse(); // reverse order so parents are populated first

                for (x in comments) {
                    var comment = comments[x];

                    if(isValidComment(comment)) {
                        var newComment = commentDiv.clone();
                        newComment.attr('id', 'post-' + comment.id);
                        newComment.find('.post-author').html(comment.author.name);
                        newComment.find('.post-time').html($('<a>').attr('href', '#post-' + comment.id).html($.timeago(comment.createdAt + 'Z')));
                        newComment.find('.post-body').html(comment.message);
                        if(!comment.parent)
                            $threadContainer.append(newComment);
                        else {
                            var parentId = comment.parent;
                            $('#post-' + parentId + ' .post-replies').first().append(newComment);
                            $('#post-' + parentId + ' .post-menu .post-menu-collapse').first().closest('li').show();
                        }
                    }
                }
            }

            // If the user has loaded a permalink to a post
            // then move the page to it
            if(window.location.hash) {
              var postId = window.location.hash;
              if($(postId).length > 0) {
                $(postId).find('.post-content').first().addClass('permalink');
                $('html, body').animate({
                    scrollTop: $(postId).offset().top
                }, 500);
              }
            }
        });

        // Present the Terms of Use modal (once) when the user
        // clicks on a textarea inside the "Add Comment" form
        $(document).on('click', 'form .message', function() {

            // Store the clicked element
            var formElement = this;

            // The form container
            var $form = $(this).closest('form');

            // Only present (and handle) the Terms Modal once
            if(!acceptedTerms) {
                $termsModal.modal();
                promiseModal.done(function() {
                    acceptedTerms = true;
                    clearMessage();
                    setTimeout(function() {
                        $(formElement).focus();
                    }, 0);
                }).fail(function() {
                    addMessage('You must accept the Terms of Use in order to post comments.', 'info');
                    promiseModal = $.Deferred();
                });
            }

            promiseModal.done(function() {
                $form.find('.author_information').slideDown();
            });
        });

        // Presents a form inside the comment thread to reply
        // to a specific post
        $(document).on('click', '.post .post-menu-reply', function(e) {
            e.preventDefault();
            var $replyFormContainer = $(this).closest('.post').find('.post-reply-form').first();
            var postId = $(this).closest('.post').attr('id').replace('post-', '');

            // Only add the form if it isn't already there
            if($replyFormContainer.children().length == 0) {
                var $commentForm = $addCommentForm.clone();
                $commentForm.attr('id', '');
                $commentForm.attr('data-reply-to', postId);
                $replyFormContainer.append($commentForm);
            }

            // Force the click event on the textarea, which will
            // cause the Terms of Use modal to appear if the user
            // hasn't accepted the ToU yet.  If they accepted
            // previously, then focus the textarea
            var $textarea = $replyFormContainer.find('.message').first();
            $textarea.click();
            $(this).toggleClass('active');
            if(acceptedTerms) {
                if($(this).hasClass('active')) {
                    $('#post-' + postId).find('.post-reply-form').first().slideDown();
                }
                else {
                    $('#post-' + postId).find('.post-reply-form').first().slideUp();
                }
                setTimeout(function() {
                    $textarea.focus();
                }, 0);
            }
        });

        $(document).on('click', '.post .post-menu-collapse', function(e) {
            e.preventDefault();
            var $replies = $(this).closest('.post').find('.post-replies').first();
            if($replies.is(':visible')) {
                $(this).html('Expand');
            }
            else {
                $(this).html('Collapse');
            }
            $replies.slideToggle();
        });

        $(document).on('submit', '.disqus-comments form', function(e) {
            e.preventDefault();
            clearMessage();

            var errors = {
                'message': 'Please enter a comment.',
                'author_name': 'Please enter a name',
                'author_email': 'Please enter an email.'
            };

            var $formContainer = $(this);
            var $errorsContainer = $(this).find('.errors', $(this));
            $errorsContainer.hide();

            var formErrors = '';
            var formValues = {};
            $(this).find(':input:not(:submit)').each(function() {
                var val = $(this).val();
                var fieldName = $(this).attr('name');
                if(!val) {
                    formErrors += errors[fieldName] + '<br>';
                }
                else {
                    formValues[fieldName] = val;
                }
            });

            if($formContainer.attr('data-reply-to')) {
                $formContainer.append($('<input>').attr('type', 'hidden').attr('name', 'parent').val($formContainer.attr('data-reply-to')));
            }

            // If there were form errors, return them to the user
            // Otherwise, submit the form
            if(formErrors) {
                $errorsContainer.html(formErrors);
                $errorsContainer.slideDown();
            }
            else {
                createComment(disqus_identifier, $formContainer).done(function(json) {
                    $formContainer.trigger('reset');
                    if(json.code == 0 && json.response.isApproved) {
                        var parentId = $formContainer.attr('data-reply-to');
                        var newComment = $(commentDiv).clone();
                        newComment.find('.post-author').html(formValues['author_name']);
                        newComment.find('.post-time').html('less than a minute ago');
                        newComment.find('.post-body').html(formValues['message']);
                        newComment.attr('id', 'post-' + json.response.id);
                        if(parentId == 0 || !parentId) {
                            $threadContainer.find('.empty').remove();
                            $threadContainer.append(newComment);
                        }
                        else {
                            $('#post-' + parentId).find('.post-replies').first().append(newComment);
                            $('#post-' + parentId + ' .post-menu .post-menu-reply').removeClass('active');
                            $('#post-' + parentId + ' .post-menu .post-menu-collapse').first().closest('li').show();
                            $formContainer.remove();
                        }
                        updateCommentCount($threadContainer.find('.post').length);
                        $(newComment).hide();
                        $(newComment).fadeIn();
                        $('html, body').animate({
                            scrollTop: $(newComment).offset().top
                        }, 500);
                    }
                    else if(json.code == 0 && !json.response.isApproved) {
                        var parentId = $formContainer.attr('data-reply-to');
                        if(parentId != 0 && parentId) {
                            $('#post-' + parentId + ' .post-menu .post-menu-reply').removeClass('active');
                            $formContainer.remove();
                        }
                        addMessage('Thank you for your comment.  Once approved it will appear on this page.', 'success');
                    }
                    else if(json.code == 4) {
                        addMessage('Anonymous commenting is not permitted.  Please sign in before commenting.', 'danger');
                    }
                    else {
                        addMessage('There was an error posting your comment.  Please try again.', 'danger');
                    }
                }).fail(function() {
                    addMessage('There was an error posting your comment.  Please try again later.', 'danger');
                });
            }
        });

        $(document).on('click', '.post .post-time a', function(e) {
            e.preventDefault();
            $('#disqus_thread .post .post-content').removeClass('permalink');
            $(this).closest('.post').find('.post-content').first().addClass('permalink');
            window.location.hash = $(this).closest('.post').attr('id');
        });

        // If the terms are accepted, resolve the
        // promise object
        $('.terms-accept').click(function() {
            promiseModal.resolve();
        });

        // If the terms are declined, reject the
        // promise object
        $('.terms-decline').click(function() {
            promiseModal.reject();
        });
    });


    function getCommentThread(ident) {
        return $.ajax({
            url: apiList,
            data: 'thread=' + ident,
            method: 'GET',
            dataType: 'json',
            done: function(json) {
                return json;
            },
            fail: function(response) {
                console.log(response);
            }
        });
    }

    function createComment(ident, form) {
        return $.ajax({
            url: apiPostCreate,
            data: 'ident=' + ident + '&' + form.serialize(),
            method: 'POST',
            dataType: 'json',
            done: function(json) {
                return json;
            },
            fail: function(response) {
            }
        });
    }

    function updateCommentCount(numComments) {
        if(numComments == 1)
            var commentsString = 'comment';
        else
            var commentsString = 'comments';
        $numCommentsContainer.html(numComments + ' ' + commentsString);

    }

    function isValidComment(comment) {
        return !comment.isSpam && !comment.isDeleted && comment.isApproved
    }

    function addMessage(message, type) {
        clearMessage();
        $messagesContainer.append($('<div>').addClass('alert alert-' + type).html(message));
        $messagesContainer.slideDown();
    }

    function clearMessage() {
        $messagesContainer.html('');
    }

})(jQuery);