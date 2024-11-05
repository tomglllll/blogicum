from django.core.paginator import Paginator
from django.conf import settings


def paginate_queryset(request, queryset, per_page=settings.POSTS_PER_PAGE):
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
