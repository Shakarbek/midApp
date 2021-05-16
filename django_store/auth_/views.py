import logging

from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics, status, viewsets
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from auth_.role_permissions import SellerPermission
from auth_.serializers import UserRegistrationSerializer, UserSerializer, SellerRegistrationSerializer, SellerSerializer, ProfileSerializer

logger = logging.getLogger('authorization')


# Create your views here.

@csrf_exempt
def auth(request):
    jwt_authentication = JSONWebTokenAuthentication()
    authenticated = jwt_authentication.authenticate(request)
    user = authenticated[0]
    ser = ProfileSerializer(user.profile)
    print(user.pk)
    return JsonResponse(ser.data)

class UserRegisterView(generics.GenericAPIView):
    serializer_class = UserRegistrationSerializer

    def post(self, request, *args, **kwargs):
        try:
            serializer = UserRegistrationSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                user = serializer.save()
                logger.info(f"{user.username} registered")
                user_serializer = UserSerializer(instance=user)
                return JsonResponse(user_serializer.data, status=status.HTTP_200_OK)
            else:
                logger.error(serializer.errors)
                return JsonResponse({'errors': str(serializer.errors)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"{e} error")
            return JsonResponse({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)

class SellerRegisterView(generics.GenericAPIView):
    serializer_class = SellerRegistrationSerializer

    # permission_classes = (IsAuthenticated,)

    @permission_classes(IsAuthenticated)
    def post(self, request, *args, **kwargs):
        if request.user.is_seller:
            try:
                seller = request.user.seller
            except ObjectDoesNotExist as e1:
                return JsonResponse({'message': "Can not get a Seller!"},
                                    status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            if seller:
                if not seller.is_active:
                    seller.make_active()
                    logger.info(f"{request.user} re-open the shop {request.user.seller}")
                    ser = SellerSerializer(seller)
                    return JsonResponse(ser.data, status=status.HTTP_200_OK)
            return JsonResponse({'message': "Your store is active"}, status=status.HTTP_200_OK)
        try:
            serializer = SellerRegistrationSerializer(data=request.data, context={'request': request})
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                logger.info(f"{request.user} is now seller")
                return JsonResponse(serializer.data, status=status.HTTP_200_OK)
            else:
                logger.info(f"{serializer.errors}")
                return JsonResponse({'message': str(serializer.errors)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(e)
            return JsonResponse({'message': str(e)}, status=status.HTTP_404_NOT_FOUND)

    @permission_classes(SellerPermission, )
    def put(self, request, *args, **kwargs):
        user = request.user
        if user.seller.is_active:
            user.seller.status_inactive()
            logger.info(f"{user} is not selling now")
            return JsonResponse({'message': 'Status of your shop is inactive!'}, status=status.HTTP_200_OK)
        else:
            user.seller.status_active()
            logger.info(f"{user} is selling now")
            return JsonResponse({'message': 'Status of your shop is active!'}, status=status.HTTP_200_OK)

    @permission_classes(SellerPermission, )
    def delete(self, request, *args, **kwargs):
        request.user.fire_seller()
        logger.info(f"{request.user} closed shop!")
        return JsonResponse({'message': 'Your Shop is de-activated'}, status=status.HTTP_200_OK)


