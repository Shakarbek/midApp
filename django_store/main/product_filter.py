from django_filters import rest_framework as filters

from main.models import Product


class ProductFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='contains')
    price = filters.NumberFilter(field_name='price', lookup_expr='lte')
    category = filters.CharFilter(lookup_expr='exact')

    class Meta:
        model = Product
        fields = ('name', 'price', 'category',)