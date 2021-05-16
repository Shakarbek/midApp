from rest_framework.permissions import BasePermission

class CustomerPermission(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_customer)


class SellerPermission(BasePermission):
    message = "You are not Seller!!!"

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_seller)
