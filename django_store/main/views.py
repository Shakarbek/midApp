from django.http import JsonResponse, HttpResponse
from django.shortcuts import render

# Create your views here.
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, viewsets, status
from rest_framework.decorators import action, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from main.product_filter import ProductFilter
from auth_.role_permissions import SellerPermission
from .models import Product, Order, Category
from .serializers import ProductSerializer, ProductCreateSerializer, ProductUpdateSerializer, CategorySerializer, \
    OrderSerializer, OrderCreateSerializer
import logging
logger = logging.getLogger('main')



class ProductViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    permission_classes = (AllowAny,)

    filter_backends = (DjangoFilterBackend,)
    filterset_class = ProductFilter
    pagination_class = PageNumberPagination

    @action(methods=["GET", ], url_path='all', detail=False)
    def all(self, request, *args, **kwargs):
        serializer = ProductSerializer(Product.objects.all(), many=True)
        data = serializer.data
        return JsonResponse(data, safe=False)

    def list(self, request, *args, **kwargs):
        serializer = ProductSerializer(Product.objects.produce(), many=True)
        data = serializer.data
        return JsonResponse(data, safe=False)

    def retrieve(self, request, *args, **kwargs):
        try:
            serializer = ProductSerializer(self.get_object())
            data = serializer.data
            return JsonResponse(data, safe=False)
        except Product.DoesNotExist as e:
            return JsonResponse({'error': 'Product does not exist'})
        except Exception as e:
            return JsonResponse({'error': str(e)})

    @action(methods=['POST'], detail=False, url_path='add', url_name='create')
            # permission_classes=(SellerPermission,))
    def post_product(self, request):
        try:
            data = self.request.data
            serializer = ProductCreateSerializer(data=data, context={'request': request})
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                logger.info(f"{request.user} created {serializer.data['name']}")
                return JsonResponse(serializer.data, status=status.HTTP_200_OK)
            else:
                logger.error(f"{request.user} try to post product with bad request!!!")
                return HttpResponse('Invalid Product', status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"{e}")
            return HttpResponse(e, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(methods=['PUT', 'DELETE'], detail=True, url_path='edit', url_name='update',
            permission_classes=(IsAuthenticated, SellerPermission))
    def update_product(self, request, pk):
        if request.method == "PUT":
            product = Product.objects.get(id=pk)
            serializer = ProductUpdateSerializer(instance=product, data=self.request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                logger.info(f"{request.user} updated {product}")
                return JsonResponse(serializer.data)
            return JsonResponse(serializer.data)
        elif request.method == "DELETE":
            product = self.queryset.get(id=pk)
            if product.seller == request.user.seller:
                logger.info(f"{request.user} deleted {product}")
                product.delete()
                return HttpResponse('deleted')
            else:
                return HttpResponse('You can delete only your products!')


class CategoryView(APIView):

    @permission_classes(SellerPermission,)
    def post(self, request, *args, **kwargs):
        data = self.request.data
        serializer = CategorySerializer(data=data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            logger.info(f"{request.user} posted new category")
            return JsonResponse(serializer.data)
        return JsonResponse({'error': "Category name is not valid!"})

    @permission_classes(AllowAny)
    def get(self, request, *args, **kwargs):
        serializer = CategorySerializer(Category.objects.all(), many=True)
        return JsonResponse(serializer.data, safe=False)


class Orders(viewsets.GenericViewSet, mixins.ListModelMixin,):

    queryset = Order.orders.prefetch_related('customer')
    permission_classes = (IsAuthenticated,)
    serializer_class = OrderSerializer

    def get_queryset(self, pk=0):
        if pk > 0:
            return self.request.user.customer_order.all()[int(pk)-1]
        return self.request.user.customer_order.all()

    def list(self, request, *args, **kwargs):
        serializer = OrderSerializer(self.get_queryset(), many=True)
        return JsonResponse(serializer.data, safe=False)

    def retrieve(self, request, pk, *args, **kwargs):
        try:
            serializer = OrderSerializer(self.get_queryset(pk=int(pk)))
            data = serializer.data
            return JsonResponse(data, safe=False)
        except Order.DoesNotExist as e:
            return JsonResponse({'error': 'Order does not exist'})
        except IndexError as e:
            return JsonResponse({'error': 'Order does not exist'})
        except Exception as e:
            print(e)
            return JsonResponse({'error': str(e)})

    @action(methods=['POST'], detail=False, url_path='make', permission_classes=(IsAuthenticated,))
    def make_order(self, request):
        try:
            prods = self.request.user.profile.products.all()
            if len(prods) < 1:
                return JsonResponse({'error': 'Add products to your basket'})
            # address = request.data['address']
            total = 0
            for prod in prods:
                total = prod.price + total

            order_data = {
                'customer': self.request.user,
                'products': prods,
                'total': total
            }

            serializer_order = OrderCreateSerializer(data=order_data)
            serializer_order.create(validated_data=order_data)
            if serializer_order.is_valid(raise_exception=True):
                profile = request.user.profile
                profile.products.set([])
                profile.save()
                logger.info(f"{request.user} created order")
                return JsonResponse({'message': 'Order create success!'}, safe=False)
            return JsonResponse({'error': str(serializer_order.errors)})
        except Exception as e:
            logger.error(str(e))
        return JsonResponse({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


