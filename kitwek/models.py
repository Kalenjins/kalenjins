from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.urls import reverse
from django.db import models


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        return self.create_user(email, password, **extra_fields)



class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    date_of_birth = models.DateField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], blank=True)
    current_county = models.CharField(max_length=100, blank=True)
    home_county = models.CharField(max_length=100, blank=True)

    # User status fields
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_banned = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.email





class Post(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=100, default= 'Paul Kimetto')
    published_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='post_images/', null=True, blank=True)
    content = models.TextField()
    read_count = models.PositiveIntegerField(default=0)  # New field to store read count
     

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        # Assuming you have a URL pattern named 'post_detail' for the post detail page
        return reverse('post_detail', kwargs={'post_id': self.id})
                       
    def increment_view_count(self):
        self.read_count += 1
        self.save()
                   
   
                        

class PostView(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"View by {self.user} on {self.post}"
    
    
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE) 
    content = models.TextField()
    published_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user} on {self.post}"

class CommentLike(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, null=True, blank=True, on_delete=models.CASCADE)  # Allow for None if not logged in
    user_ip = models.CharField(max_length=15, null=True, blank=True)

    def __str__(self):
        return f"Like for {self.comment}"    
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['comment', 'user'], name='unique_comment_like')
        ]
    

    

class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user_ip = models.CharField(max_length=15)
      
        # Add unique constraint on the combination of post and user_ip
    class Meta:
        unique_together = ('post', 'user_ip')  # Old-style constraint (still works)
        # OR alternatively, you can use the new approach with UniqueConstraint:
        # constraints = [
        #     models.UniqueConstraint(fields=['post', 'user_ip'], name='unique_like')
        # ]

    def __str__(self):
        return f"Like for {self.post}"
    




    
class Clans(models.Model):
    clan_name = models.CharField(max_length=50)
    clan_details = models.TextField(max_length=5000)

    def __str__(self):
        return  self.clan_name

class Origin(models.Model):
    origin_title = models.CharField(max_length=50, blank=True)
    origin_details = models.TextField(max_length=5000, blank= True)

    def __str__(self):
        return  self.origin_title
    

class Quotes (models.Model):
    quote_title = models.CharField(max_length=100)
    quote_details = models.TextField(max_length=500)

    def __str__(self):
        return  self.quote_title