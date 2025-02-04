// LIKE BTN JS START 12/12/2024
document.addEventListener("DOMContentLoaded", function() {
    let visibilityFlag = false;  // Flag to track visibility state
    const sortedPostsUrl = '/ajax/sorted-posts/'; // Define the URL globally
    // Map to store the button and count elements by postId for faster access
    const elementsMap = new Map();
     
    // Fetch and render the sorted posts from the backend
    function fetchSortedPosts() {
        fetch(sortedPostsUrl, {
            method: 'GET',
            headers: {
                'Cache-Control': 'no-cache'  // Disable caching to get fresh data
            }
        })
        .then(response => response.json())  // Parse the JSON response
        .then(data => {
            console.log('Fetched Posts:', data.posts);  // Log the fetched posts data for debugging
        
            const postsContainer = document.getElementById('posts-container');
            postsContainer.innerHTML = '';  // Clear any existing posts

            let mainContentHTML = `
                <div class="content-container" style="display: flex;">
                    <div class="main-content" style="width: 70%;">`;

            data.posts.forEach(post => {
                let truncatedContent = post.content.split(' ').slice(0, 30).join(' ') + ' ';
                truncatedContent += `<a href="${post.url}" class="see-more-txt">see more</a>`;

                mainContentHTML += `
                    <div class="post" id="post-${post.id}">
                        <h2><a href="${post.url}">${post.title}</a></h2>
                        <p>Posted - ${post.published_at}</p>
                        ${post.image_url ? `<div class="post-image"><a href="${post.url}"><img src="${post.image_url}" alt="${post.title}" class="responsive-image"></a></div>` : ''}
                        <p>${truncatedContent}</p>
                        <div class="actions">
                            <form method="POST" id="like-form-${post.id}">
                                <button type="button" class="like-btn" id="like-btn-${post.id}" data-post-id="${post.id}">
                                    Like (<span id="like-count-${post.id}">${post.likes_count}</span>)
                                </button>
                            </form>
                            <a href="${post.url}#comments" class="comment-btn">
                                <button type="button" data-id="${post.id}">
                                    Comments (<span id="comment-count-${post.id}">${post.comments_count}</span>)
                                </button>
                            </a>

                            <button class="share-btn" onclick="toggleShareMenu(${post.id})">Share</button>
                            <!-- Share Button -->
                            <div class="share-btn-container">
                                <div id="share-menu-${post.id}" class="share-menu" style="display: none;">
                                    <a href="#" onclick="shareOnWhatsApp(${post.id})">Share on WhatsApp</a>
                                    <a href="#" onclick="shareOnFacebook(${post.id})">Share on Facebook</a>
                                    <a href="#" onclick="shareOnTwitter(${post.id})">Share on Twitter</a>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            });

            mainContentHTML += `
                </div>
                <div class="sidebar" style="width: 30%; padding-left: 20px;">
                    <h3 class="sidebar-title">Most viewed</h3>
                    <ul class="sidebar-list">`;

            data.posts.forEach(post => {
                mainContentHTML += `

                    <li class="sidebar-item"><a href="${post.url}" class="sidebar-link">${post.title}</a></li>
                `;
            });

            mainContentHTML += `
                    </ul>
                </div>
            </div>
            `;

            postsContainer.innerHTML = mainContentHTML;

            // Add event listeners for like buttons after rendering
            data.posts.forEach(post => {
                const button = document.getElementById(`like-btn-${post.id}`);
                const likeCountSpan = document.getElementById(`like-count-${post.id}`);
                elementsMap.set(post.id, { button, likeCountSpan });
                button.addEventListener('click', function() {
                    toggleLike(post.id);
                });
            });
        })
        .catch(error => {
            console.error('Error fetching posts:', error);
        });
    }

    // Function to handle like/unlike post
    function toggleLike(postId) {
        const { button, likeCountSpan } = elementsMap.get(postId);
        const alreadyLiked = button.textContent.startsWith('Liked');
    
        fetch('/like/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify({
                post_id: postId,
                like_action: alreadyLiked ? 'remove' : 'add',
            }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                likeCountSpan.textContent = data.likes_count;
                button.textContent = data.liked ? `Liked (${data.likes_count})` : `Like (${data.likes_count})`;
            } else {
                console.error("Error in response:", data.message);
            }
        })
        .catch(error => {
            console.error("Request failed:", error);
        });
    }
    // Helper function to get CSRF token from the cookie
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Re-fetch sorted posts when the page becomes visible again
    document.addEventListener('visibilitychange', function() {
        if (!document.hidden && !visibilityFlag) {
            visibilityFlag = true;
            fetchSortedPosts();
        } else if (document.hidden) {
            visibilityFlag = false;
        }
    });

    fetchSortedPosts();  // Fetch posts when the DOM is fully loaded
});

// LIKE BTN JS END 12/12/2024




// COMMENT JS START 17/12/2024
document.addEventListener('DOMContentLoaded', function () {
    const submitButton = document.getElementById('submit-comment');
    const loadMoreButton = document.getElementById('load-more-comments');

    // Comment submission logic
    if (submitButton) {  // Ensure the button exists before attaching event listener
        console.log('Adding comment event listener');  // Debugging line

        // Prevent attaching the event listener multiple times
        if (submitButton.hasAttribute('data-listener-attached')) {
            console.log('Listener already attached');
            return;
        }

        // Mark the listener as attached
        submitButton.setAttribute('data-listener-attached', 'true');

        submitButton.addEventListener('click', function (e) {
            // Ignore if the button is already disabled
            if (submitButton.disabled) return;

            e.preventDefault();  // Prevent form submission

            const postId = this.getAttribute('data-post-id');
            const content = document.getElementById('comment-content').value;

            // Check if the content field is filled
            if (!content) {
                alert("Please fill in the comment!");
                return;  // Prevent sending an empty comment
            }

            // Get CSRF token from the hidden input field
            const csrfToken = document.querySelector('[name="csrfmiddlewaretoken"]').value;

            // Disable the submit button immediately to prevent multiple submissions
            submitButton.disabled = true;
            submitButton.innerHTML = "Posting...";  // Indicate it's processing

            console.log('Button disabled, sending request...');

            // Send the POST request to the /add_comment/ endpoint
            fetch('/add_comment/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,  // CSRF token for security
                },
                body: JSON.stringify({ 
                    post_id: postId, 
                    content: content,
                    user_id: '{{ user.id }}'  // Send the user ID as 'user_id', not 'author_id'
                })
            })
            .then(response => response.json())  // Parse the JSON response
            .then(data => {
                console.log('Response received', data);  // Log the response data

                if (data.status === 'success') {
                    // Add the new comment to the comment list
                    const commentList = document.getElementById('comment-list');

                    // Insert the HTML directly from the response
                    commentList.innerHTML += data.comment_html;

                    // Update the comment count (if the element exists)
                    const commentCount = document.getElementById('comment-count-' + postId);
                    if (commentCount) {
                        commentCount.textContent = data.comments_count;  // Update the count
                    }

                    // Now dynamically insert the like button and like count for the new comment
                    const newComment = commentList.lastElementChild;
                    const likeButtonContainer = newComment.querySelector('.like-link');
                    const likeCountSpan = likeButtonContainer.querySelector('.like-count');
                    likeCountSpan.textContent = data.new_comment_like_count;  // Update with the actual like count

                    // Clear the text area after posting
                    document.getElementById('comment-content').value = '';
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert("There was an error posting your comment. Please try again.");
            })
            .finally(() => {
                // Re-enable the button and reset the text after the request is completed
                setTimeout(() => {
                    submitButton.disabled = false;
                    submitButton.innerHTML = "Submit Comment";  // Reset button text
                    console.log('Button re-enabled');
                }, 1000);  // Delay to ensure that the request is fully processed before re-enabling
            });
        });
    }

    // Read More / Read Less functionality
    document.body.addEventListener('click', function (e) {
        if (e.target && e.target.classList.contains('read-more')) {
            const commentParagraph = e.target.closest('p');
            const fullContent = commentParagraph.getAttribute('data-full-content');
            commentParagraph.innerHTML = `${fullContent} <a href="#" class="read-less">Read Less</a>`;
        }
        if (e.target && e.target.classList.contains('read-less')) {
            const commentParagraph = e.target.closest('p');
            const truncatedContent = commentParagraph.getAttribute('data-truncated-content');
            commentParagraph.innerHTML = `${truncatedContent} <a href="#" class="read-more">Read More</a>`;
        }
    });

    // COMMENT-LIKE JS START 3/1/2025
    document.body.addEventListener('click', function (e) {
        // Only handle clicks on elements with the "like-link" class
        if (e.target && e.target.classList.contains('like-link')) {
            e.preventDefault();  // Prevent default anchor link behavior

            const likeLink = e.target;
            const commentId = likeLink.getAttribute('data-comment-id');

            // Send AJAX request to register the like
            const csrfToken = document.querySelector('[name="csrfmiddlewaretoken"]').value;

            // Send a request to add the like
            fetch('/like_comment/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,  // CSRF token for security
                },
                body: JSON.stringify({ comment_id: commentId })
            })
            .then(response => response.json())  // Parse the JSON response
            .then(data => {
                if (data.status === 'success') {
                    // Update the like count
                    const likeCountSpan = likeLink.querySelector('.like-count');
                    likeCountSpan.textContent = data.like_count;
                } else {
                    alert('Error liking the comment. Please try again.');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('There was an error liking the comment. Please try again.');
            });
        }
    });
    // COMMENT-LIKE JS END 3/1/2025

    // LOAD MORE COMMENTS FUNCTIONALITY
    if (loadMoreButton) {
        loadMoreButton.addEventListener('click', function () {
            const postId = this.getAttribute('data-post-id');
            const currentPage = this.getAttribute('data-current-page') || 1;
            loadComments(postId, parseInt(currentPage) + 1);
        });
    }

    // Function to load comments
    function loadComments(postId, page) {
        fetch(`/post/${postId}/?page=${page}`, {
            method: 'GET', 
            headers: {
                'Accept': 'application/json',  // Ensure Accept header is set to application/json
                'Content-Type': 'application/json',  // If sending JSON data
            }
        })
        .then(response => response.json())
        .then(data => {
            console.log('Response data:', data);  // Log the response data for debugging
            
            if (data.status === 'success') {
                const commentList = document.getElementById('comment-list');
                const loadMoreButton = document.getElementById('load-more-comments');
                
                // Append new comments
                data.comments.forEach(comment => {
                    
                    const newComment = document.createElement('div');
                    newComment.classList.add('comment');
            
                    // Ensure that comment.user.id exists and is valid
                    if (comment.user && comment.user.id) {
                        // Replace the placeholder 0 with the actual user ID dynamically
                        const userProfileUrl = profileUrlTemplate.replace('0', comment.user.id);
            
                        // Check if the comment content length is greater than 50 characters
                        let contentHtml;
                        if (comment.content.length > 50) {
                            contentHtml = `
                                <p>
                                    <strong>
                                        <a href="${userProfileUrl}" class="comments-user-names">
                                            ${comment.user.first_name} ${comment.user.last_name}
                                        </a>
                                    </strong>
                                    ${comment.published_at}: ${comment.content.slice(0, 50)}... 
                                    <a href="#" class="read-more" data-comment-id="${comment.id}">Read More</a>
                                </p>
                            `;
                        } else {
                            // If content is 50 characters or less, just show it
                            contentHtml = `
                                <p>
                                    <strong>
                                        <a href="${userProfileUrl}" class="comments-user-names">
                                            ${comment.user.first_name} ${comment.user.last_name}
                                        </a>
                                    </strong>
                                    ${comment.published_at}: ${comment.content}
                                </p>
                            `;
                        }
            
                        // Append the comment with the appropriate content
                        newComment.innerHTML = `
                            ${contentHtml}
                            <a href="#" class="like-link" data-comment-id="${comment.id}">
                                Like <span class="like-count">${comment.commentlike_set_count}</span>
                            </a>
                        `;
                    }
            
                    commentList.appendChild(newComment);
                });
            
            
        
                // Handle "Load More Comments" visibility
                if (data.has_next) {
                    loadMoreButton.setAttribute('data-current-page', data.current_page);
                    loadMoreButton.style.display = 'block';  // Show the button
                } else {
                    loadMoreButton.style.display = 'none';  // Hide the button
                }
            } else {
                alert('Error loading comments');
            }
        })
        .catch(error => {
            console.error('Error loading comments:', error);
            alert('There was an error loading the comments. Please try again.');
        });
    }

    const initialPostId = loadMoreButton ? loadMoreButton.getAttribute('data-post-id') : null;
    if (initialPostId) {
        loadComments(initialPostId, 1);  // Load the first page of comments
    }
});
// COMMENT JS END 17/12/2024







// SEE MORE QUOTES JS START 09/12/2024
document.addEventListener('DOMContentLoaded', function() {
    let currentPage = 1; // Track the current page number
    const quotesContainer = document.getElementById('quote-container');
    const seeMoreButton = document.getElementById('see-more-btn'); // Corrected button ID selection

    // Check if the "SEE MORE QUOTES" button exists
    if (seeMoreButton) {
        // Event listener for the "SEE MORE QUOTES" button
        seeMoreButton.addEventListener('click', function() {
            currentPage++;  // Increment page number for the next request

            // Make an AJAX request to get the next set of quotes
            fetch(`/quotes/?page=${currentPage}`, {  // Fixed fetch URL
                method: 'GET',
                headers: {

                    'Accept': 'application/json', // Ensure the server returns JSON
                },
            })
            .then(response => response.json())  // Get JSON response
            .then(data => {

                if (data.quotes) {
                    quotesContainer.innerHTML += data.quotes; // Append new quotes
                    if (!data.has_next) {
                        seeMoreButton.style.display = 'none';
                    }
                }
            })
            .catch(error => console.error('Error loading more quotes:', error));
        });
    } else {
        console.log('NO MORE QUOTES');
    }
});
// SEE MORE QUOTES JS END 09/12/2024





// SHARE BUTTONS JS START 17-12-2024
    function toggleMenu(postId) {
        const menu = document.getElementById('share-menu-' + postId);
        menu.style.display = (menu.style.display === 'block') ? 'none' : 'block';
    }
    
    // Share on WhatsApp
    function shareOnWhatsApp(postId) {
        const postTitle = encodeURIComponent(document.getElementById('post-title-' + postId).innerText); // Fetching title dynamically
        const postUrl = encodeURIComponent(document.getElementById('post-url-' + postId).href); // Fetching URL dynamically
        window.open(`https://wa.me/?text=${postTitle}%20${postUrl}`, '_blank');
    }
    
    // Share on Facebook
    function shareOnFacebook(postId) {
        const postUrl = encodeURIComponent(document.getElementById('post-url-' + postId).href); // Fetching URL dynamically
        window.open(`https://www.facebook.com/sharer/sharer.php?u=${postUrl}`, '_blank');
    }
    
    // Share on Twitter
    function shareOnTwitter(postId) {
        const postTitle = encodeURIComponent(document.getElementById('post-title-' + postId).innerText); // Fetching title dynamically
        const postUrl = encodeURIComponent(document.getElementById('post-url-' + postId).href); // Fetching URL dynamically
        window.open(`https://twitter.com/intent/tweet?text=${postTitle}&url=${postUrl}`, '_blank');
    }
    
    // Close the menu if clicked outside
    window.onclick = function(event) {
        const menuItems = document.querySelectorAll('.share-menu');
        menuItems.forEach(menu => {
            const button = menu.previousElementSibling; // the share button
            if (!button.contains(event.target) && !menu.contains(event.target)) {
                menu.style.display = 'none';
            }
        });
    }
// SHARE BUTTONS JS START 17-12-2024




