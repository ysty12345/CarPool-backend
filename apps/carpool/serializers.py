from rest_framework import serializers
from django.core.validators import RegexValidator, EmailValidator
from .models import (
    Account, Passenger, Driver, Advertiser, IdentityVerification, Vehicle
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


# 身份验证序列化器
class IdentityVerificationSerializer(serializers.ModelSerializer):
    status = serializers.CharField(read_only=True)
    class Meta:
        model = IdentityVerification
        fields = '__all__'

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
        fields = ['id', 'rating', 'created_at', 'services', 'identity_verification', 'vehicle']

    def get_services(self, obj):
        return [service.name for service in obj.services.all()]
