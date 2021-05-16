from datetime import datetime
from rest_framework import serializers
from auth_.models import Seller
from auth_.serializers import SellerSerializer, UserInfoSerializer, SellerSerializer, UserSerializer
from .models import Product, Category, Order


class CategorySerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    name = serializers.CharField(max_length=100)

    def validate(self, attrs):
        if not attrs.__contains__('name'):
            raise serializers.ValidationError('Name field is required')
        try:
            Category.objects.get(name=attrs['name'])
        except Category.DoesNotExist:
            return attrs
        raise serializers.ValidationError('Category with that name already exists')
        # return attrs

    def create(self, validated_data):
        return Category.objects.create(**validated_data)


class ProductSellerSerializer(serializers.ModelSerializer):
    user = UserInfoSerializer()

    class Meta:
        model = Seller
        fields = ['user', 'location', 'is_active']


class ProductSerializer(serializers.ModelSerializer):
    location = serializers.CharField(max_length=200, default="Almaty")
    seller = ProductSellerSerializer(read_only=True)
    produced = serializers.BooleanField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'category', 'description', 'price', 'quantity', 'location', 'seller', 'produced']


class OrderProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['name', 'category', 'price', 'produced']


class ProductSimpleSerializer(OrderProductSerializer):
    seller = SellerSerializer()

    class Meta:
        model = Product
        fields = OrderProductSerializer.Meta.fields + ['seller']


class ProductUpdateSerializer(serializers.ModelSerializer):
    description = serializers.CharField(required=False)
    location = serializers.CharField(required=False)
    produced = serializers.BooleanField(required=False)
    price = serializers.IntegerField(required=False)
    quantity = serializers.IntegerField(required=False)

    class Meta:
        model = Product
        fields = ['description', 'price', 'quantity', 'location', 'produced']

    def validate(self, attrs):
        if not attrs.__contains__('description') and not attrs.__contains__('price') and\
                not attrs.__contains__('quantity') and not attrs.__contains__('location') \
                and not attrs.__contains__('produced'):
            raise serializers.ValidationError('No data to update')

        return attrs

    def update(self, instance, validated_data):
        instance.description = validated_data.get('description', instance.description)
        instance.price = validated_data.get('price', instance.price)
        instance.quantity = validated_data.get('quantity', instance.quantity)
        instance.location = validated_data.get('location', instance.location)
        instance.produced = validated_data.get('produced', instance.produced)
        instance.save()
        return instance

    def delete(self, instance):
        print('delete', instance)
        return instance


class ProductCreateSerializer(serializers.ModelSerializer):
    location = serializers.CharField(max_length=200)
    seller = SellerSerializer(read_only=True)

    class Meta:
        model = Product
        fields = ['name', 'category', 'description', 'price', 'quantity', 'location', 'seller']

    def validate(self, attrs):
        if not attrs.__contains__('name'):
            raise serializers.ValidationError('Name is required!')
        if not attrs.__contains__('category'):
            raise serializers.ValidationError('Category is required!')
        if not attrs.__contains__('description'):
            raise serializers.ValidationError('Description is required!')
        if not attrs.__contains__('price'):
            raise serializers.ValidationError('Price is required!')
        if not attrs.__contains__('quantity'):
            raise serializers.ValidationError('Quantity is required!')
        if not attrs.__contains__('location'):
            raise serializers.ValidationError('Location is required!')
        return attrs

    def create(self, validated_data):
        return Product.objects.create(
            name=validated_data['name'],
            category=validated_data['category'],
            description=validated_data['description'],
            price=validated_data['price'],
            quantity=validated_data['quantity'],
            location=validated_data['location'],
            seller=self.context['request'].user.seller
        )


class OrderSerializer(serializers.ModelSerializer):
    products = OrderProductSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'products' ]


class OrderCreateSerializer(serializers.ModelSerializer):
    customer = UserSerializer(read_only=True)
    products = ProductSimpleSerializer(read_only=True, many=True)

    class Meta:
        model = Order
        fields = ['customer', 'products']

    def validate(self, attrs):
        return attrs

    def create(self, validated_data):
        customer = validated_data['customer']
        products = validated_data['products']
        order = Order.orders.create(
            customer=customer,
            products=products
        )
        order.products.set(products)
        return order