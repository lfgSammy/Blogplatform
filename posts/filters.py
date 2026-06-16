import django_filters
from .models import Post


class PostFilter(django_filters.FilterSet):
    # filter by category slug
    category = django_filters.CharFilter(
        field_name='category__slug', lookup_expr='iexact'
    )
    # filter by tag slug
    tag = django_filters.CharFilter(
        field_name='tags__slug', lookup_expr='iexact'
    )
    # filter by author username
    author = django_filters.CharFilter(
        field_name='author__username', lookup_expr='iexact'
    )
    # filter by status
    status = django_filters.CharFilter(
        field_name='status', lookup_expr='iexact'
    )
    # filter by date range
    created_after = django_filters.DateFilter(
        field_name='created_at', lookup_expr='gte'
    )
    created_before = django_filters.DateFilter(
        field_name='created_at', lookup_expr='lte'
    )
    # search in title and body
    search = django_filters.CharFilter(method='filter_search')

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            title__icontains=value
        ) | queryset.filter(
            body__icontains=value
        )

    class Meta:
        model = Post
        fields = ['category', 'tag', 'author', 'status',
                  'created_after', 'created_before', 'search']