from django import forms
from django.contrib.auth.models import User

from .models import Post, Comment


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ('title', 'text', 'category', 'location', 'pub_date', 'image')
        widgets = {
            'pub_date': forms.DateTimeInput(
                attrs={'type': 'datetime-local'},
                format='%d-%m-%Y %H:%M')
        }


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
