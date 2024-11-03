from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.models import User

from .forms import PostForm, ProfileForm, CommentForm
from .models import Category, Post, Comment
from .utils import paginate_queryset, get_post_queryset


def index(request):
    template_name = 'blog/index.html'
    posts = get_post_queryset()
    page_obj = paginate_queryset(request, posts)
    context = {'page_obj': page_obj}
    return render(request, template_name, context)


def category_posts(request, category_slug):
    template_name = 'blog/category.html'
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )
    posts = get_post_queryset().filter(category=category)
    page_obj = paginate_queryset(request, posts)
    context = {'category': category, 'page_obj': page_obj}
    return render(request, template_name, context)


def post_detail(request, post_id):
    template_name = 'blog/detail.html'
    if (request.user.is_authenticated
       and Post.objects.filter(id=post_id, author=request.user).exists()):
        post = get_object_or_404(get_post_queryset(apply_filters=False),
                                 id=post_id)
    else:
        post = get_object_or_404(get_post_queryset(), id=post_id)

    comments = post.comments.select_related('author').order_by('created_at')
    context = {'post': post, 'comments': comments, 'form': CommentForm()}
    return render(request, template_name, context)


def profile(request, username):
    profile = get_object_or_404(User, username=username)
    if request.user == profile:
        posts = get_post_queryset(manager=profile.posts.all(),
                                  apply_filters=False)
    else:
        posts = get_post_queryset(manager=profile.posts.all(),
                                  apply_filters=True)
    page_obj = paginate_queryset(request, posts)
    context = {'profile': profile, 'page_obj': page_obj}
    return render(request, 'blog/profile.html', context)


def create_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect(('blog:profile'), username=request.user.username)
    return render(request, 'blog/create.html', {'form': form})


def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        return redirect('blog:post_detail', post_id=post.id)
    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=post)
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id=post.id)

    context = {'form': form}
    return render(request, 'blog/create.html', context)


def edit_profile(request):
    user = request.user
    form = ProfileForm(request.POST or None, instance=user)
    if form.is_valid():
        form.save()
        return redirect('blog:profile', username=request.user.username)
    return render(request, 'blog/user.html', {'form': form})


def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()
        return redirect('blog:post_detail', post_id=post.id)


def edit_comment(request, post_id, comment_id):
    post = get_object_or_404(Post, id=post_id)
    comment = get_object_or_404(Comment, id=comment_id, author=request.user)
    form = CommentForm(request.POST or None, instance=comment)
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id=post.id)
    context = {'form': form, 'post': post, 'comment': comment}
    return render(request, 'blog/comment.html', context)


def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, author=request.user)
    form = PostForm(instance=post)
    context = {'post': post, 'form': form}
    if request.method == 'POST':
        post.delete()
        return redirect('blog:index')
    return render(request, 'blog/detail.html', context)


def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, author=request.user)
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', post_id=post.id)
    context = {'post': post, 'comment': comment}
    return render(request, 'blog/comment.html', context)
