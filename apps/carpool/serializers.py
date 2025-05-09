from rest_framework import serializers
from django.core.validators import RegexValidator, EmailValidator
from .models import (
    Account, Passenger, Driver, Advertiser, IdentityVerification, Vehicle, TripRequest, TripOrder, Review, Coupon,
    UserCoupon
)


# 注册序列化器
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    RegexValidator(r"^1[3-9]\d{9}$", message="手机号格式不正确")

    class Meta:
        model = Account
        fields = ['phone', 'password', 'is_passenger', 'is_driver', 'is_advertiser']
        extra_kwargs = {
            'phone': {'required': True, 'max_length': 11, 'min_length': 1, 'validators': []},
            'is_passenger': {'read_only': True},
            'is_driver': {'read_only': True},
            'is_advertiser': {'read_only': True},
        }

    def validate(self, attrs):
        phone = attrs.get('phone')
        if Account.objects.filter(phone=phone).exists():
            raise serializers.ValidationError({"detail": "手机号已注册"})
        return attrs

    def create(self, validated_data):
        return Account.objects.create_user(**validated_data)


# 乘客序列化器
class PassengerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Passenger
        fields = ['nickname', 'rating', 'created_at']


# 广告商序列化器
class AdvertiserSerializer(serializers.ModelSerializer):
    status = serializers.CharField(read_only=True)

    class Meta:
        model = Advertiser
        fields = "__all__"
        readonly_fields = ['account', 'status', 'created_at']


# 身份验证序列化器
class IdentityVerificationSerializer(serializers.ModelSerializer):
    status = serializers.CharField(read_only=True)

    class Meta:
        model = IdentityVerification
        fields = '__all__'
        read_only_fields = ['status', 'created_at', 'last_modified']

    def validate_idnumber(self, value):
        import re
        if not re.match(r'^\d{17}[\dXx]$', value):
            raise serializers.ValidationError("身份证号格式不正确")
        return value

    def validate_driverlicense(self, value):
        if len(value) < 6:
            raise serializers.ValidationError("驾驶证号格式不正确")
        return value


# 车辆序列化器
class VehicleSerializer(serializers.ModelSerializer):
    status = serializers.CharField(read_only=True)

    class Meta:
        model = Vehicle
        fields = '__all__'
        read_only_fields = ['status', 'created_at']

    def validate_plate_number(self, value):
        import re
        if not re.match(r'^[京沪粤苏浙鲁晋冀津渝川鄂湘皖赣闽陕甘宁蒙新青藏桂云贵黑吉辽]{1}[A-Z]{1}[A-Z0-9]{5}$', value):
            raise serializers.ValidationError("车牌号格式不正确")
        return value


# 司机序列化器
class DriverSerializer(serializers.ModelSerializer):
    identity_verification = IdentityVerificationSerializer(source='account.identity_verification', read_only=True)
    vehicle = VehicleSerializer(source='account.vehicle', read_only=True)
    services = serializers.SerializerMethodField()

    class Meta:
        model = Driver
        fields = ['rating', 'created_at', 'services', 'identity_verification', 'vehicle']

    def get_services(self, obj):
        return [service.name for service in obj.services.all()]


# 乘客功能相关序列化器
class TripRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = TripRequest
        fields = '__all__'
        read_only_fields = ['account', 'status', 'request_time', 'estimated_price']

    def create(self, validated_data):
        validated_data['status'] = 'pending'
        from django.utils import timezone
        validated_data['request_time'] = timezone.now()
        return super().create(validated_data)

    def validate_trip_type(self, value):
        if value not in dict(TripRequest.TRIP_TYPE_CHOICES):
            raise serializers.ValidationError("无效的出行类型")
        return value

    def validate(self, data):
        if data.get('seats_needed', 1) <= 0:
            raise serializers.ValidationError({'seats_needed': '乘客数量必须大于0'})
        return data


class TripOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = TripOrder
        fields = '__all__'
        readonly_fields = ['trip_request', 'driver', 'payment_status', 'created_at']


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = "__all__"
        read_only_fields = ['created_at', 'reviewer']

    def validate(self, data):
        user = self.context['request'].user
        order = data['order']

        if order.passenger != user and order.driver != user:
            raise serializers.ValidationError("你无权评价这个订单。")

        if Review.objects.filter(order=order, reviewer=user).exists():
            raise serializers.ValidationError("你已经评价过这个订单了。")

        if user == data['reviewee']:
            raise serializers.ValidationError("不能评价自己。")

        return data


class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = '__all__'


class UserCouponSerializer(serializers.ModelSerializer):
    coupon = CouponSerializer(read_only=True)

    class Meta:
        model = UserCoupon
        fields = ['coupon', 'acquired_at', 'used_at', 'status']
