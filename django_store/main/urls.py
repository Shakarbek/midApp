from django.urls import path
from rest_framework import routers

from .views import ProductViewSet, Orders, CategoryView

router = routers.SimpleRouter()
router.register('products', ProductViewSet)
router.register('orders', Orders)
urlpatterns = [
    path('category/', CategoryView.as_view()),
]
urlpatterns += router.urls