from django.core.validators import validate_email
from rest_framework import serializers

from auth_.models import User, Seller, Profile
from main.models import Product


class CategorySerializer(serializers.Serializer):
    name= serializers.CharField(max_length=200)


class ProductSerializer(serializers.ModelSerializer):
    category=CategorySerializer()

    class Meta:
        model=Product
        fields=['id', 'name', 'price', 'category']


class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password', 'email', 'age', 'phone_number', 'location')

    def validate(self, attrs):
        password = attrs['password']
        if not attrs.__contains__('email'):
            raise serializers.ValidationError('email is required!!!')
        email = attrs['email']
        if not attrs.__contains__('location'):
            raise serializers.ValidationError('Location is required!!!')
        # if not attrs.__contains__('age'):
        #     raise serializers.ValidationError('Age is required!!!')
        # if not attrs.__contains__('phone_number'):
        #     raise serializers.ValidationError('Phone number is required!!!')
        if len(password) < 8:
            raise serializers.ValidationError('Password is too short, minimum length is 8')
        try:
            validate_email(email)
        except serializers.ValidationError as e:
            raise serializers.ValidationError(f"bad email, details: {e}")
        return attrs

    def create(self, validated_data):
        user = User.users.create_user(username=validated_data['username'],
                                      password=validated_data['password'],
                                      email=validated_data['email'],
                                      age=validated_data['age'],
                                      location=validated_data['location'],
                                      is_seller=False)
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=['username']

class UserInfoSerializer(UserSerializer):
    class Meta:
        model=User
        fields=UserSerializer.Meta.fields+['age', 'is_seller']

class UserTotalInfoSerializer(UserInfoSerializer):
    class Meta:
        model=User
        fields=UserInfoSerializer.Meta.fields+['phone_number', 'location']

class SellerSerializer(serializers.ModelSerializer):
    class Meta:
        model=Seller
        fields=['is_active']

class SellerInfoSerializer(SellerSerializer):
    class Meta:
        model=Seller
        fields=SellerSerializer.Meta.fields+['user', 'location']


class SellerRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seller
        fields = ('location')

    def validate(self, attrs):
        if not attrs.__contains__('location'):
            raise serializers.ValidationError('Location is required!!!')
        return attrs

    def create(self, validated_data):
        user_obj = self.context['request'].user
        seller = Seller.objects.create(user=user_obj, location=validated_data['location'])
        user_obj.is_seller = True
        user_obj.save()
        return seller


class ProfileSerializer(serializers.ModelSerializer):
    products = ProductSerializer(read_only=True, many=True)

    class Meta:
        model = Profile
        fields = ['products']
