from django.db.models import Count
from django.core.paginator import Paginator
from django.utils import timezone
from .models import Post


def get_published_posts_with_comments(queryset=None, include_unpublished_for_author=None):
    if queryset is None:
        queryset = Post.objects.all()
    
    # Если указан автор, показываем ему все его посты
    if include_unpublished_for_author:
        queryset = queryset.filter(author=include_unpublished_for_author)
    else:
        queryset = queryset.filter(
            is_published=True,
            pub_date__lte=timezone.now(),
            category__is_published=True
        )
    
    queryset = queryset.annotate(
        comment_count=Count('comments')
    )
    
    ordering = Post._meta.ordering
    if ordering:
        queryset = queryset.order_by(*ordering)
    
    return queryset


def paginate_posts(request, posts_queryset, posts_per_page=10):
    paginator = Paginator(posts_queryset, posts_per_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)