from django.core.exceptions import ValidationError
from django.contrib.auth.admin import UserAdmin
from django.contrib import admin
from kitwek.signals import compress_image
from .models import CustomUser, Post, Comment, CommentLike,Like, Clans, Origin, Quotes








class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_active', 'is_banned', 'date_joined')
    list_filter = ('is_staff', 'is_active', 'is_banned')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'phone_number', 'tsc_number', 'date_of_birth')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_banned', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name', 'last_name', 'is_active', 'is_staff', 'is_banned')
        }),
    )

admin.site.register(CustomUser, CustomUserAdmin)



# Register your models here.

# Post Model
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    ordering = ('-published_at',)
    list_display = ('title', 'author', 'published_at', 'image')
    search_fields = ('title', 'content', 'author')
    list_filter = ('published_at', 'author')

    def save_model(self, request, obj, form, change):
        """
        Override save_model to handle image resizing and compression before saving the object
        """
        if obj.image:
            try:
                # Compress the image if it exceeds the size limit
                obj.image = compress_image(obj.image, max_size_kb=500)
            except ValidationError as e:
                # Handle the error here, it will be displayed in the admin form
                form.add_error('image', e)
                return  # Return without saving the object if the image size is too large
        
        # Save the model after compression is done
        super().save_model(request, obj, form, change)

# Comment Model
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'published_at')
    search_fields = ('user', 'content')
    list_filter = ('published_at', 'user')

# Like Model
@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('post', 'user_ip')
    search_fields = ('user_ip',)

# Like Model
@admin.register(Clans)
class ClansAdmin(admin.ModelAdmin):
    list_display = ('clan_name', 'clan_details')
    search_fields = ('user_ip',)

# Like Model
@admin.register(Origin)
class OriginAdmin(admin.ModelAdmin):
    list_display = ('origin_title', 'origin_details')
    search_fields = ('origin_title',)

# Like Model
@admin.register(Quotes)
class QuotesAdmin(admin.ModelAdmin):
    list_display = ('quote_title', 'quote_details')
    search_fields = ('quote_title',)    


# Like Model
@admin.register(CommentLike)
class CommentLikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_ip' , 'comment_id')
    list_filter = ('user_ip', 'id')