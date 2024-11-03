from django.core.paginator import Paginator
from django.utils import timezone
from django.db.models import Count
from django.conf import settings

from .models import Post


def paginate_queryset(request, queryset, per_page=settings.POSTS_PER_PAGE):
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def get_post_queryset(manager=Post.objects,
                      apply_filters=True,
                      annotate_comments=True):
    queryset = manager.select_related('author', 'category', 'location')
    if apply_filters:
        queryset = queryset.filter(
            is_published=True,
            pub_date__lte=timezone.now(),
            category__is_published=True
        )
    if annotate_comments:
        queryset = (queryset.annotate(comment_count=Count('comments'))
                    .order_by('-pub_date'))
    return queryset
