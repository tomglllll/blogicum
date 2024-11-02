from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.http import Http404
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Count

from .forms import PostForm, ProfileForm, CommentForm
from .models import Category, Post, Comment

POSTS_PER_PAGE = 10


def paginate_queryset(request, queryset, per_page=POSTS_PER_PAGE):
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def get_base_post_queryset():
    return Post.objects.filter(
        is_published=True,
        pub_date__lte=timezone.now(),
        category__is_published=True
    ).annotate(
        comment_count=Count('comments')
    ).select_related(
        'author', 'category', 'location'
    ).order_by('-pub_date')


def index(request):
    template_name = 'blog/index.html'
    posts = get_base_post_queryset()
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
    posts = get_base_post_queryset().filter(category=category)
    page_obj = paginate_queryset(request, posts)
    context = {'category': category, 'page_obj': page_obj}
    return render(request, template_name, context)


def post_detail(request, post_id):
    template_name = 'blog/detail.html'
    post = get_object_or_404(Post, id=post_id)
    if (
        not post.is_published or not post.category.is_published
        or post.pub_date > timezone.now()
    ) and post.author != request.user:
        raise Http404("Страница не найдена")
    comments = post.comments.order_by('created_at')
    form = CommentForm() if request.user.is_authenticated else None
    context = {'post': post, 'comments': comments, 'form': form}
    return render(request, template_name, context)


def profile(request, username):
    profile = get_object_or_404(User, username=username)
    if request.user == profile:
        posts = Post.objects.filter(author=profile)
    else:
        posts = Post.objects.filter(
            author=profile,
            is_published=True,
            pub_date__lte=timezone.now()
        )
    posts = (posts
             .annotate(comment_count=Count('comments'))
             .order_by('-pub_date'))
    page_obj = paginate_queryset(request, posts)
    context = {'profile': profile, 'page_obj': page_obj}
    return render(request, 'blog/profile.html', context)


def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, files=request.FILES or None)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect(('blog:profile'), username=request.user.username)
    else:
        form = PostForm()
    return render(request, 'blog/create.html', {'form': form})


def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        return redirect('blog:post_detail', post_id=post.id)
    if request.method == 'POST':
        form = PostForm(request.POST,
                        files=request.FILES or None,
                        instance=post)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', post_id=post.id)
    else:
        form = PostForm(instance=post)
    context = {'form': form}
    return render(request, 'blog/create.html', context)


def edit_profile(request):
    user = request.user
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('blog:profile', username=request.user.username)
    else:
        form = ProfileForm(instance=user)
    return render(request, 'blog/user.html', {'form': form})


def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect('blog:post_detail', post_id=post.id)
    else:
        form = CommentForm()
    context = {'form': form, 'post': post}
    return render(request, 'blog/comment.html', context)


def edit_comment(request, post_id, comment_id):
    post = get_object_or_404(Post, id=post_id)
    comment = get_object_or_404(Comment, id=comment_id, author=request.user)
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', post_id=post.id)
    else:
        form = CommentForm(instance=comment)
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
