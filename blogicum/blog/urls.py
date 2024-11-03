from django.urls import include, path
from django.contrib.auth.decorators import login_required

from . import views

app_name = 'blog'

post_urls = [
    path('<int:post_id>/',
         views.post_detail,
         name='post_detail'),
    path('create/',
         login_required(views.create_post),
         name='create_post'),
    path('<int:post_id>/edit/',
         login_required(views.edit_post),
         name='edit_post'),
    path('<int:post_id>/comment/',
         login_required(views.add_comment),
         name='add_comment'),
    path('<int:post_id>/edit_comment/<int:comment_id>/',
         login_required(views.edit_comment),
         name='edit_comment'),
    path('<int:post_id>/delete_comment/<int:comment_id>/',
         login_required(views.delete_comment),
         name='delete_comment'),
    path('<int:post_id>/delete/',
         login_required(views.delete_post),
         name='delete_post'),
]

urlpatterns = [
    path('', views.index, name='index'),
    path('category/<slug:category_slug>/',
         views.category_posts,
         name='category_posts'),
    path('profile/edit/',
         login_required(views.edit_profile),
         name='edit_profile'),
    path('profile/<str:username>/',
         views.profile,
         name='profile'),
    path('posts/', include(post_urls)),
]
