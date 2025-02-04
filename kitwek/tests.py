import json
from django.db import IntegrityError
from django.test import TestCase

# Create your tests here.

from django.test import TestCase
from django.contrib.auth import get_user_model
from kitwek.models import Post, Comment, Like, PostView, CommentLike, Clans, Origin, Quotes
from django.utils import timezone


class CustomUserTestCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='testuser@example.com',
            password='password123',
            first_name='John',
            last_name='Doe'
        )
    
    def test_user_creation(self):
        """Test that the user is created properly"""
        self.assertEqual(self.user.email, 'testuser@example.com')
        self.assertTrue(self.user.check_password('password123'))
        self.assertFalse(self.user.is_staff)
        self.assertFalse(self.user.is_superuser)

    def test_user_str(self):
        """Test the string representation of the user"""
        self.assertEqual(str(self.user), 'testuser@example.com')


class PostTestCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='testuser@example.com',
            password='password123',
            first_name='John',
            last_name='Doe'
        )
        self.post = Post.objects.create(
            title="Test Post",
            author=self.user.email,
            content="This is a test post."
        )

    def test_post_creation(self):
        """Test that a post is created correctly"""
        self.assertEqual(self.post.title, "Test Post")
        self.assertEqual(self.post.author, self.user.email)
        self.assertIn('test post', self.post.content.lower())

    def test_post_str(self):
        """Test the string representation of a post"""
        self.assertEqual(str(self.post), "Test Post")

    def test_get_absolute_url(self):
        """Test the get_absolute_url method"""
        url = self.post.get_absolute_url()
        # Adjust the expected URL to match the actual URL pattern
        self.assertEqual(url, f"/post/{self.post.id}/")  # Make sure this matches your URL pattern

class CommentLikeTestCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='testuser@example.com',
            password='password123',
            first_name='John',
            last_name='Doe'
        )
        self.post = Post.objects.create(
            title="Test Post",
            author=self.user.email,
            content="This is a test post."
        )
        self.comment = Comment.objects.create(
            post=self.post,
            user=self.user,
            content="This is a test comment."
        )

    def test_comment_like_creation(self):
        """Test that a comment like is created correctly"""
        like = CommentLike.objects.create(comment=self.comment, user=self.user)
        self.assertEqual(like.comment, self.comment)
        self.assertEqual(like.user, self.user)

    def test_comment_like_unique_constraint(self):
        """Test that the unique constraint works on comment and user"""
        CommentLike.objects.create(comment=self.comment, user=self.user)
        with self.assertRaises(IntegrityError):  # Expecting an IntegrityError here
            CommentLike.objects.create(comment=self.comment, user=self.user)
            
class LikeTestCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='testuser@example.com',
            password='password123',
            first_name='John',
            last_name='Doe'
        )
        self.post = Post.objects.create(
            title="Test Post",
            author=self.user.email,
            content="This is a test post."
        )

    def test_like_creation(self):
        """Test that a like is created correctly"""
        like = Like.objects.create(post=self.post, user_ip='192.168.1.1')
        self.assertEqual(like.post, self.post)
        self.assertEqual(like.user_ip, '192.168.1.1')

    def test_unique_like_constraint(self):
        """Test that the unique constraint works on post and user_ip"""
        Like.objects.create(post=self.post, user_ip='192.168.1.1')
        with self.assertRaises(Exception):
            Like.objects.create(post=self.post, user_ip='192.168.1.1')


class PostViewTestCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='testuser@example.com',
            password='password123',
            first_name='John',
            last_name='Doe'
        )
        self.post = Post.objects.create(
            title="Test Post",
            author=self.user.email,
            content="This is a test post."
        )

    def test_post_view_creation(self):
        """Test that a post view is created correctly"""
        post_view = PostView.objects.create(post=self.post, user=self.user)
        self.assertEqual(post_view.post, self.post)
        self.assertEqual(post_view.user, self.user)

    def test_post_view_str(self):
        """Test the string representation of post view"""
        post_view = PostView.objects.create(post=self.post, user=self.user)
        self.assertEqual(str(post_view), f"View by {self.user} on {self.post}")


class CommentLikeTestCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='testuser@example.com',
            password='password123',
            first_name='John',
            last_name='Doe'
        )
        self.post = Post.objects.create(
            title="Test Post",
            author=self.user.email,
            content="This is a test post."
        )
        self.comment = Comment.objects.create(
            post=self.post,
            user=self.user,
            content="This is a test comment."
        )

    def test_comment_like_creation(self):
        """Test that a comment like is created correctly"""
        like = CommentLike.objects.create(comment=self.comment, user=self.user)
        self.assertEqual(like.comment, self.comment)
        self.assertEqual(like.user, self.user)

    def test_comment_like_unique_constraint(self):
        """Test that the unique constraint works on comment and user"""
        # Create the first like
        CommentLike.objects.create(comment=self.comment, user=self.user)
        
        # Try creating a second like for the same comment and user
        with self.assertRaises(IntegrityError):  # Expecting an IntegrityError here
            CommentLike.objects.create(comment=self.comment, user=self.user)



class ClansTestCase(TestCase):
    def setUp(self):
        self.clan = Clans.objects.create(clan_name="Warriors", clan_details="A mighty clan of warriors.")

    def test_clan_creation(self):
        """Test that a clan is created correctly"""
        self.assertEqual(self.clan.clan_name, "Warriors")
        self.assertIn("mighty", self.clan.clan_details.lower())


class OriginTestCase(TestCase):
    def setUp(self):
        self.origin = Origin.objects.create(origin_title="Earth", origin_details="Origin of all humans.")

    def test_origin_creation(self):
        """Test that an origin is created correctly"""
        self.assertEqual(self.origin.origin_title, "Earth")
        self.assertIn("humans", self.origin.origin_details.lower())


class QuotesTestCase(TestCase):
    def setUp(self):
        self.quote = Quotes.objects.create(quote_title="Inspiration", quote_details="Believe in yourself!")

    def test_quote_creation(self):
        """Test that a quote is created correctly"""
        self.assertEqual(self.quote.quote_title, "Inspiration")
        self.assertIn("yourself", self.quote.quote_details.lower())






#FUNCTION TESTS

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Post, Comment, Clans, Quotes

User = get_user_model()

class TestUserAuthentication(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='testuser@example.com', password='password123'
        )

    def test_login_valid_user(self):
        # Test logging in with valid credentials
        response = self.client.post(reverse('login'), {
            'email': 'testuser@example.com',
            'password': 'password123',
        })
        self.assertEqual(response.status_code, 302)  # Redirects after login
        self.assertRedirects(response, reverse('home'))

    def test_login_invalid_user(self):
        # Test logging in with invalid credentials
        response = self.client.post(reverse('login'), {
            'email': 'wronguser@example.com',
            'password': 'wrongpassword',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid email or password.")

    def test_signup(self):
        # Test signing up a new user
        response = self.client.post(reverse('sign_up'), {
            'email': 'newuser@example.com',
            'password1': 'password123',
            'password2': 'password123',
            'first_name': 'New',
            'last_name': 'User',
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))


class TestPostViews(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='testuser@example.com', password='password123'
        )
        self.post = Post.objects.create(
            title="Test Post", content="This is a test post.", author=self.user
        )

    def test_post_detail_view(self):
        # Test viewing a post's details
        response = self.client.get(reverse('post_detail', args=[self.post.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.post.title)
        self.assertContains(response, self.post.content)

    def test_post_like(self):
        # Test liking a post
        self.client.login(email='testuser@example.com', password='password123')
        response = self.client.post(reverse('like_post'), data=json.dumps({'post_id': self.post.id}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertTrue(response_data['liked'])  # Post should be liked
        self.assertEqual(response_data['likes_count'], 1)

    def test_comment_creation(self):
        # Test comment creation for a post
        self.client.login(email='testuser@example.com', password='password123')
        response = self.client.post(reverse('add_comment'), data=json.dumps({
            'post_id': self.post.id, 'content': 'This is a test comment.'
        }), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(response_data['status'], 'success')
        self.assertContains(response_data['comment_html'], 'This is a test comment.')

    def test_comment_like(self):
        # Test liking a comment
        comment = Comment.objects.create(post=self.post, user=self.user, content="Test Comment")
        self.client.login(email='testuser@example.com', password='password123')
        response = self.client.post(reverse('like_comment'), data=json.dumps({'comment_id': comment.id}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(response_data['like_count'], 1)


class TestProfileViews(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='testuser@example.com', password='password123'
        )

    def test_profile_view(self):
        # Test viewing the profile page
        self.client.login(email='testuser@example.com', password='password123')
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user.first_name)

    def test_edit_profile_view(self):
        # Test editing profile
        self.client.login(email='testuser@example.com', password='password123')
        response = self.client.post(reverse('edit_profile'), {
            'first_name': 'Updated',
            'last_name': 'User',
            'email': 'updateduser@example.com',
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('profile'))


class TestClans(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='testuser@example.com', password='password123'
        )
        self.clan = Clans.objects.create(clan_name="Test Clan", clan_details="Details about Test Clan")

    def test_clan_list(self):
        # Test viewing the list of clans
        response = self.client.get(reverse('clans'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.clan.clan_name)

    def test_clan_detail(self):
        # Test viewing the detail page of a specific clan
        response = self.client.get(reverse('clan_detail', args=[self.clan.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.clan.clan_name)


class TestQuotes(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='testuser@example.com', password='password123'
        )
        self.quote = Quotes.objects.create(quote_title="Test Quote", quote_details="Details about Test Quote")

    def test_quote_list(self):
        # Test viewing the list of quotes
        response = self.client.get(reverse('quote'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.quote.quote_title)

    def test_quote_pagination(self):
        # Test that quotes are paginated
        for i in range(30):  # Create 30 quotes for pagination
            Quotes.objects.create(quote_title=f"Quote {i}", quote_details=f"Details about Quote {i}")
        response = self.client.get(reverse('quote') + '?page=2')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Quote 20')


