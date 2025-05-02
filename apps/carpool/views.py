from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

from .models import Passenger, Driver, Advertiser
from .serializers import RegisterSerializer, PassengerSerializer, DriverSerializer, AdvertiserSerializer, \
    IdentityVerificationSerializer, VehicleSerializer


# Create your views here.


# 注册视图
class RegisterView(APIView):
    authentication_classes = []  # 不需要登录就能访问注册接口

    def post(self, request):
        ser = RegisterSerializer(data=request.data)
        if ser.is_valid():
            user = ser.save()
            # 为用户生成 JWT
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            return Response({"message": "注册成功", "access_token": access_token}, status=status.HTTP_201_CREATED)
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)


# 登录视图
class LoginView(APIView):
    authentication_classes = []  # 不需要登录就能访问登录接口

    def post(self, request):
        username = request.data.get("phone")
        password = request.data.get("password")

        # 验证用户名和密码
        user = authenticate(username=username, password=password)
        if user is not None:
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)
            return Response({
                "message": "登录成功",
                "access_token": access_token,
                "refresh_token": refresh_token
            }, status=status.HTTP_200_OK)
        else:
            return Response({"error": "用户名或密码错误"}, status=status.HTTP_401_UNAUTHORIZED)


# 乘客视图
class PassengerCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        account = request.user
        if account.is_passenger:
            return Response({"detail": "已是乘客"}, status=400)

        nickname = request.data.get("nickname")
        rating = request.data.get("rating", 5.0)  # 默认评分

        Passenger.objects.create(account=account, nickname=nickname, rating=rating)
        account.is_passenger = True
        account.save()

        return Response({"detail": "乘客信息创建成功"}, status=201)


class PassengerInfoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            passenger = Passenger.objects.get(account=request.user)
            serializer = PassengerSerializer(passenger)
            return Response(serializer.data)
        except Passenger.DoesNotExist:
            return Response({"detail": "乘客信息不存在"}, status=404)


# 司机视图
class DriverCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        account = request.user
        if account.is_driver:
            return Response({"detail": "已是司机"}, status=400)
        if not account.identity_verification or not account.vehicle:
            return Response({"detail": "请先完成实名认证和车辆信息录入"}, status=400)

        serializer = DriverSerializer(data=request.data)
        if serializer.is_valid():
            Driver.objects.create(account=account, **serializer.validated_data)
            account.is_driver = True
            account.save()
            return Response({"detail": "司机身份创建成功"}, status=201)
        return Response(serializer.errors, status=400)


class DriverInfoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            driver = Driver.objects.get(account=request.user)
            serializer = DriverSerializer(driver)
            return Response(serializer.data)
        except Driver.DoesNotExist:
            return Response({"detail": "司机信息不存在"}, status=404)


# 广告商视图
class AdvertiserCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        account = request.user
        if account.is_advertiser:
            return Response({"detail": "已是广告商"}, status=400)

        company_name = request.data.get("company_name")
        contact_name = request.data.get("contact_name")
        email = request.data.get("email")
        website_url = request.data.get("website_url")

        Advertiser.objects.create(
            account=account,
            company_name=company_name,
            contact_name=contact_name,
            email=email,
            website_url=website_url
        )
        account.is_advertiser = True
        account.save()

        return Response({"detail": "广告商身份创建成功"}, status=201)


class AdvertiserInfoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            advertiser = Advertiser.objects.get(account=request.user)
            serializer = AdvertiserSerializer(advertiser)
            return Response(serializer.data)
        except Advertiser.DoesNotExist:
            return Response({"detail": "广告商信息不存在"}, status=404)


# 身份验证视图
class IdentityVerificationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = IdentityVerificationSerializer(data=request.data)
        if serializer.is_valid():
            identity = serializer.save()
            request.user.identity_verification = identity
            request.user.save()
            return Response({"detail": "实名认证成功"}, status=201)
        return Response(serializer.errors, status=400)

    def get(self, request):
        identity = request.user.identity_verification
        if not identity:
            return Response({"detail": "未提交实名认证"}, status=404)
        serializer = IdentityVerificationSerializer(identity)
        return Response(serializer.data)

    def patch(self, request):
        identity = request.user.identity_verification
        if not identity:
            return Response({"detail": "未提交实名认证"}, status=404)
        serializer = IdentityVerificationSerializer(identity, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "实名认证更新成功"})
        return Response(serializer.errors, status=400)


# 车辆信息视图
class VehicleView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = VehicleSerializer(data=request.data)
        if serializer.is_valid():
            vehicle = serializer.save()
            request.user.vehicle = vehicle
            request.user.save()
            return Response({"detail": "车辆信息录入成功"}, status=201)
        return Response(serializer.errors, status=400)

    def get(self, request):
        vehicle = request.user.vehicle
        if not vehicle:
            return Response({"detail": "未提交车辆信息"}, status=404)
        serializer = VehicleSerializer(vehicle)
        return Response(serializer.data)

    def patch(self, request):
        vehicle = request.user.vehicle
        if not vehicle:
            return Response({"detail": "未提交车辆信息"}, status=404)
        serializer = VehicleSerializer(vehicle, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "车辆信息更新成功"})
        return Response(serializer.errors, status=400)
