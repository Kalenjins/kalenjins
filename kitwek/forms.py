from django import forms
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from .models import CustomUser




class LoginForm(forms.Form):
    email = forms.EmailField(label='Email', max_length=254)
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        if email and password:
            user = authenticate(email=email, password=password)
            if user is None:
                raise forms.ValidationError("Invalid email or password")
            cleaned_data['user'] = user
        return cleaned_data





class SignUpForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput, label="Password")
    password2 = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")
    
    class Meta:
        model = CustomUser
        fields = [
            'first_name',
            'last_name', 
            'email', 
            'phone_number', 
            'date_of_birth', 
            ]

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        
        if password1 != password2:
            raise ValidationError("Passwords do not match")
        
        # Password validation (optional)
        validate_password(password1)
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user
    


    #EDIT PROFILE FORM
from .models import CustomUser

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
                'first_name',
                'last_name',
                'phone_number', 
                'gender', 
                'current_county',
                'home_county',
                'date_of_birth',
                'profile_picture'
                ]    