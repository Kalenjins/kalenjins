from django.db.models import Count, Case, When, Value, IntegerField,Exists, OuterRef,F
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import  ObjectDoesNotExist
from django.contrib.auth.models import  AnonymousUser
from django.views.decorators.csrf import csrf_exempt
from django.template.defaultfilters import timesince
from django.template.loader import render_to_string
from django.contrib.auth import authenticate,login
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.contrib import messages 
from django.urls import reverse
import json
from .forms import LoginForm,SignUpForm,ProfileEditForm
from .models import CustomUser, Post, Comment, CommentLike, Like, Clans, Origin, Quotes, PostView




#log in func start
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            # Get the cleaned data from the form
            email = form.cleaned_data['email']  # Assuming the form has 'username' field
            password = form.cleaned_data['password']  # Assuming the form has 'password' field
            
            # Authenticate the user using Django's built-in authenticate function
            user = authenticate(request, email=email, password=password)
            
            if user is not None:
                # If user is authenticated, log them in
                login(request, user)
                
                # Redirect to the 'next' URL or home page after successful login
                next_url = request.GET.get('next', 'home')
                return redirect(next_url)
            else:
                # If authentication fails, add an error message
                messages.error(request, "Invalid email or password.")
        else:
            # If form is not valid, we can handle any other validation errors
            messages.error(request, "Invalid email or password.")

    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})
#log in func end




#sign up func start
def sign_up(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)  # Save the user but don't commit to the database yet
            user.set_password(form.cleaned_data["password1"])  # Set the password before saving
            user.save()  # Save the user to the database
            
            # Authenticate and log in the user
            user = authenticate(email=user.email, password=form.cleaned_data['password1'])
            if user is not None:
                login(request, user)
                return redirect('login')  # Redirect to the login page or any other page
            
        else:
            print(form.errors)  # This will show form validation errors in the console
    else:
        form = SignUpForm()

    return render(request, 'sign_up.html', {'form': form})
#sign up func end






@login_required
def index(request):
    # Create a subquery to check if the logged-in user has viewed the post
    post_views = PostView.objects.filter(post=OuterRef('pk'), user=request.user)

    posts = Post.objects.annotate(
        annotated_published_at=F('published_at'),  # Use alias to avoid conflict
        likes_count=Count('like'),  # Count likes on each post
        comment_count=Count('comment'),  # Count comments on each post
        viewed_rank=Case(
            When(Exists(post_views), then=Value(1)),  # Check if the user has viewed the post
            default=Value(0),
            output_field=IntegerField()
        )
    ).order_by('viewed_rank', '-likes_count')  # Viewed posts at the bottom, then ordered by likes count
    
    return render(request, 'index.html', {'posts': posts})



def post_detail(request, post_id):
    # Fetch the post based on the provided ID
    post = get_object_or_404(Post, id=post_id)

       # Increment the read count each time the post is viewed
    post.increment_view_count()  # This will increase the read_count by 1

    # Track the post view for the user (only if the user is authenticated)
    if not isinstance(request.user, AnonymousUser):  # Check if the user is logged in
        if not PostView.objects.filter(post=post, user=request.user).exists():
            PostView.objects.create(post=post, user=request.user)

    # Fetch comments associated with this post and paginate them
    comments_list = Comment.objects.filter(post=post).select_related('user') \
        .prefetch_related('commentlike_set').order_by('published_at')

    paginator = Paginator(comments_list, 10)  # Show 10 comments per page
    page_number = request.GET.get('page', 1)
    comments = paginator.get_page(page_number)

    # Fetch recent posts for the sidebar (you can adjust the number of posts as needed)
    recent_posts = Post.objects.order_by('-read_count')[:5]  # Fetch top 5 posts with the highest read_count

    # Fetch sponsored content (this is just an example, you can adjust it to your model)
    sponsored_content = {
        'title': 'Sponsored Ad',
        'description': 'Check out this amazing product!',
        'link': 'http://example.com/product'  # Replace with actual sponsored link
    }

    # Handle comment submission if it's a POST request
    if request.method == 'POST':
        if request.user.is_authenticated:
            content = request.POST.get('content')
            if content:
                # Create and save the comment
                comment = Comment(post=post, user=request.user, content=content)
                comment.save()

                # Prepare the response data
                return JsonResponse({
                    'status': 'success',
                    'user': comment.user.first_name,
                    'content': comment.content,
                    'comments_count': post.comment_set.count(),
                })
            else:
                return JsonResponse({'status': 'error', 'message': 'Content cannot be empty'})
        else:
            return JsonResponse({'status': 'error', 'message': 'You must be logged in to comment.'}, status=403)

    # Check if the request is an AJAX request (for loading more comments)
    if request.headers.get('Accept') == 'application/json':
        # Prepare comments data for the JSON response
        comments_data = [
            {
                'id': comment.id,
                'user': {
                    'id': comment.user.id,
                    'first_name': comment.user.first_name,
                    'last_name': comment.user.last_name
                },
                'content': comment.content,
                'published_at': comment.published_at.isoformat(),
                'commentlike_set_count': comment.commentlike_set.count()
            }
            for comment in comments
        ]
        
        # Return the comments data as a JSON response
        return JsonResponse({
            'status': 'success',
            'comments': comments_data,  # Include the formatted comments data
            'has_next': comments.has_next(),  # Indicates if there are more comments to load
            'current_page': page_number,
            'comments_count': post.comment_set.count(),
        })

    # For non-AJAX requests, render the post details page
    return render(request, 'post_detail.html', {
        'post': post, 
        'comments': comments,
        'has_next': comments.has_next(),  # Pass has_next to template
        'current_page': page_number,  # Pass current page to template
        'recent_posts': recent_posts,  # Pass recent posts to the template
        'sponsored_content': sponsored_content,  # Pass sponsored content to the template
    })

def comment_to_dict(comment):
    """ Helper function to convert a comment to a dictionary for JSON response """
    return {
        'id': comment.id,
        'user': {
            'first_name': comment.user.first_name,
            'last_name': comment.user.last_name,
        },
        'content': comment.content,
        'published_at': comment.published_at.isoformat(),  # Return ISO formatted datetime
        'commentlike_set_count': comment.commentlike_set.count(),
    }



@login_required
def get_sorted_posts(request):
    # Create a subquery to check if the logged-in user has viewed the post
    post_views = PostView.objects.filter(post=OuterRef('pk'), user=request.user)
 
    # Fetch posts, annotate them with like counts, comment counts, and viewed rank
    posts = Post.objects.annotate(
        likes_count=Count('like'),  # Count likes on each post
        comments_count=Count('comment'),  # Count comments on each post
        viewed_rank=Case(
            When(Exists(post_views), then=Value(1)),  # If the user has viewed the post, set viewed_rank = 1
            default=Value(0),  # If the user hasn't viewed the post, set viewed_rank = 0
            output_field=IntegerField()
        )
    ).order_by('viewed_rank', '-likes_count')  # Order by 'viewed_rank' first, then by likes_count in descending order

    # Prepare the posts data to send as JSON
    posts_data = []
    for post in posts:
        posts_data.append({
            'id': post.id,
            'title': post.title,
            'content': post.content,  # Full content, no truncation
            'likes_count': post.likes_count,
            'comments_count': post.comments_count,
            'image_url': post.image.url if post.image else None,  
           
            'url': post.get_absolute_url(),  # Assuming you have a `get_absolute_url()` method for the Post model
        })

    # Return the data as a JSON response
    return JsonResponse({'posts': posts_data})







 # Profile func START

def profile_view(request, id=None):
    # If no id is provided, use the logged-in user's id
    if id is None:
        user = request.user  # Use the logged-in user's data
    else:
        # If an id is provided, get the user with that id
        user = get_object_or_404(CustomUser, id=id)

    return render(request, 'profile.html', {'user': user})
   

@login_required
def edit_profile_view(request):
    user = request.user
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile')  # Redirect back to the profile page after saving
    else:
        form = ProfileEditForm(instance=user)

    return render(request, 'edit_profile.html', {'form': form})
 # Profile func END





@csrf_exempt  # Avoid CSRF validation for this example (be careful with this in production)
def like_post(request):
    if request.method == "POST":
        try:
            # Parse the request body
            data = json.loads(request.body)
            post_id = data.get('post_id')
            
            if not post_id:
                return JsonResponse({"status": "error", "message": "Post ID is required"}, status=400)

            post = get_object_or_404(Post, id=post_id)
            user_ip = request.META.get('REMOTE_ADDR')

            # Check if a like from this IP already exists for this post
            existing_like = Like.objects.filter(post=post, user_ip=user_ip).first()

            if existing_like:
                # If the user has already liked the post, delete the like (unlike)
                existing_like.delete()
                liked = False
            else:
                # If the user hasn't liked the post yet, create a new like
                Like.objects.create(post=post, user_ip=user_ip)
                liked = True

            # Get the updated like count for the post
            likes_count = post.like_set.count()

            return JsonResponse({
                "status": "success",
                "liked": liked,
                "post_id": post_id,
                "likes_count": likes_count
            }, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "Invalid JSON data"}, status=400)

        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

    return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)





def truncate_comment(content, word_limit=50):
    words = content.split()
    if len(words) > word_limit:
        truncated_content = ' '.join(words[:word_limit]) + '...'
        return truncated_content, True  # Indicate it's truncated
    return content, False  # No truncation




@login_required
def add_comment(request):
    if request.method == 'POST' and request.headers.get('Content-Type') == 'application/json':
        try:
            data = json.loads(request.body)
            post_id = data.get('post_id')
            content = data.get('content')
            user = request.user  # Get the logged-in user

            # Truncate the comment content
            truncated_content, is_truncated = truncate_comment(content)
            
            if post_id and content:
                # Create the comment
                comment = Comment.objects.create(
                    post_id=post_id,
                    user=user,
                    content=content
                )
                
                # Generate the time since the comment was posted
                published_time = timesince(comment.published_at)
                
                # Generate the URL for the user's profile
                profile_url = reverse('profile_user_by_id', kwargs={'id': comment.user.id})

                # Get the like count for the new comment
                new_comment_like_count = comment.commentlike_set.count()

                # Generate the HTML for the like button and count
                like_button_html = f'''
                    <a href="#" class="like-link" data-comment-id="{comment.id}">
                        Like <span class="like-count">{new_comment_like_count}</span>
                    </a>
                '''

                # Construct the HTML for the new comment
                comment_html = f'''
                    <div class="comment">
                        <p>
                            <strong>
                                <a href="{profile_url}">
                                    {comment.user.first_name} {comment.user.last_name}
                                </a>
                            </strong>  
                            {published_time} : {truncated_content}
                            {'<a href="#" class="read-more">Read More</a>' if is_truncated else ''}
                        </p>
                        {like_button_html}  <!-- Insert the like button HTML -->
                    </div>
                '''

                # Return the comment HTML and other data
                return JsonResponse({
                    'status': 'success',
                    'comment_html': comment_html,
                    'comments_count': comment.post.comment_set.count(),  # Update the comment count
                    'new_comment_like_count': new_comment_like_count,  # Include the like count
                })
            else:
                return JsonResponse({'status': 'error', 'message': 'Invalid data'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON format'}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)



def like_comment(request):
    if request.method == 'POST' and request.headers.get('Content-Type') == 'application/json':
        try:
            # Parse the JSON request body
            data = json.loads(request.body)
            comment_id = data.get('comment_id')

            # Check if the comment_id exists in the request
            if not comment_id:
                return JsonResponse({'status': 'error', 'message': 'No comment ID provided'}, status=400)

            # Try to retrieve the comment, handle the case where it's not found
            try:
                comment = Comment.objects.get(id=comment_id)
            except ObjectDoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Comment not found'}, status=404)

            # Check if the user is logged in
            if request.user.is_authenticated:
                user = request.user
                # Check if the logged-in user has already liked the comment
                existing_like = CommentLike.objects.filter(comment=comment, user=user)
            else:
                # For non-logged-in users, use their IP address to track likes
                user_ip = request.META.get('REMOTE_ADDR')
                # Check if the IP address has already liked the comment
                existing_like = CommentLike.objects.filter(comment=comment, user_ip=user_ip)

            # Prevent duplicate likes
            if existing_like.exists():
                return JsonResponse({'status': 'error', 'message': 'You have already liked this comment.'}, status=400)

            # Add the like depending on whether the user is logged in or not
            if request.user.is_authenticated:
                CommentLike.objects.create(comment=comment, user=user)
            else:
                CommentLike.objects.create(comment=comment, user_ip=user_ip)

            # Get the updated like count
            like_count = CommentLike.objects.filter(comment=comment).count()

            return JsonResponse({
                'status': 'success',
                'like_count': like_count,
            })

        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON format'}, status=400)

    # Return a bad request response if the request method or content type is incorrect
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)












@login_required
def clans(request):
    clans = Clans.objects.all()  
    return render(request, 'clans.html', {'clans': clans})


def clan_detail(request, pk):
    clan = get_object_or_404(Clans, pk=pk)
    return render(request, 'clan_detail.html', {'clan': clan})

@login_required
def origin(request):
    origin = Origin.objects.all() 
    return render(request, 'origin.html', {'origin': origin})

@login_required
def quote(request):
    # Get all quotes from the database
    quote_list = Quotes.objects.all()

    # Set up pagination (10 quotes per page)
    paginator = Paginator(quote_list, 20)  # 10 quotes per page
    page_number = request.GET.get('page')  # Get page number from the query parameters
    page_obj = paginator.get_page(page_number)  # Get the quotes for the current page

    # Check for AJAX request by looking at the 'X-Requested-With' header
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Render only the quotes section (partial template) for the current page
        quotes_html = render_to_string('partials/quotes_list.html', {'page_obj': page_obj})
        return JsonResponse({'quotes': quotes_html, 'has_next': page_obj.has_next()})

    # Return normal page with paginated quotes if not an AJAX request
    return render(request, 'quotes.html', {'page_obj': page_obj})






#FUNCTION TEST


