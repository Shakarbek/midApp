from django.urls import path
from rest_framework_jwt.views import obtain_jwt_token, verify_jwt_token
from .views import auth, UserRegisterView, SellerRegisterView
urlpatterns = [
    path('', obtain_jwt_token),
    path('token', auth),    # register simple user
    path('signup/', UserRegisterView.as_view())
]