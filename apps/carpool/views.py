from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import transaction
from django.contrib.auth import authenticate

from ext.permissions import IsPassenger, IsDriver, IsAdvertiser
from .models import Passenger, Driver, Advertiser, TripRequest, TripOrder, UserCoupon, Coupon, Ride
from .serializers import RegisterSerializer, PassengerSerializer, DriverSerializer, AdvertiserSerializer, \
    IdentityVerificationSerializer, VehicleSerializer, TripRequestSerializer, TripOrderSerializer, ReviewSerializer, \
    UserCouponSerializer, CouponSerializer, TripSerializer, RideListSerializer


# Create your views here.


# 注册视图
class RegisterView(APIView):
    # 不需要登录就能访问注册接口
    authentication_classes = []
    permission_classes = []

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
    # 不需要登录就能访问注册接口
    authentication_classes = []
    permission_classes = []

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


##########################################################
# 乘客基本视图
class PassengerCreateView(APIView):

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
    permission_classes = [IsPassenger]

    def get(self, request):
        try:
            passenger = Passenger.objects.get(account=request.user)
            serializer = PassengerSerializer(passenger)
            return Response(serializer.data)
        except Passenger.DoesNotExist:
            return Response({"detail": "乘客信息不存在"}, status=404)


# 司机基本视图
class DriverCreateView(APIView):

    def post(self, request):
        account = request.user

        if account.is_driver:
            return Response({"detail": "已是司机"}, status=400)

        # 检查实名认证是否存在并已审核通过
        identity = account.identity_verification
        if not identity:
            return Response({"detail": "请先完成实名认证"}, status=400)
        if identity.status != 'approved':
            return Response({"detail": "实名认证尚未通过审核"}, status=400)

        # 检查车辆信息是否存在并已审核通过
        vehicle = account.vehicle
        if not vehicle:
            return Response({"detail": "请先完成车辆信息录入"}, status=400)
        if vehicle.status != 'approved':
            return Response({"detail": "车辆信息尚未通过审核"}, status=400)

        # 检查是否已存在绑定的司机对象
        if Driver.objects.filter(account=account).exists():
            return Response({"detail": "司机身份已存在"}, status=400)

        # 校验其他字段
        serializer = DriverSerializer(data=request.data)
        if serializer.is_valid():
            Driver.objects.create(account=account, **serializer.validated_data)
            account.is_driver = True
            account.save()
            return Response({"detail": "司机身份创建成功"}, status=201)

        return Response(serializer.errors, status=400)


class DriverInfoView(APIView):
    permission_classes = [IsDriver]

    def get(self, request):
        try:
            driver = Driver.objects.get(account=request.user)
            serializer = DriverSerializer(driver)
            return Response(serializer.data)
        except Driver.DoesNotExist:
            return Response({"detail": "司机信息不存在"}, status=404)


##########################################################
# 广告商基本视图
class AdvertiserCreateView(APIView):

    def post(self, request):
        account = request.user
        if account.is_advertiser:
            return Response({"detail": "已是广告商"}, status=400)

        serializer = AdvertiserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(account=account)
            return Response({"detail": "广告商身份申请提交成功，等待审核"}, status=201)
        return Response(serializer.errors, status=400)


class AdvertiserInfoView(APIView):
    permission_classes = [IsAdvertiser]

    def get(self, request):
        try:
            advertiser = Advertiser.objects.get(account=request.user)
            serializer = AdvertiserSerializer(advertiser)
            return Response(serializer.data)
        except Advertiser.DoesNotExist:
            return Response({"detail": "广告商信息不存在"}, status=404)


# 身份验证视图
class IdentityVerificationView(APIView):

    def post(self, request):
        if request.user.identity_verification:
            return Response({"detail": "实名认证已提交，请勿重复操作"}, status=400)

        serializer = IdentityVerificationSerializer(data=request.data)
        if serializer.is_valid():
            identity = serializer.save()
            request.user.identity_verification = identity
            request.user.save()
            return Response({"detail": "实名认证提交成功，等待审核"}, status=201)
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
            instance = serializer.save()
            instance.status = 'pending'  # 修改后需要重新审核
            instance.save()
            return Response({"detail": "实名认证信息已更新，等待审核"})
        return Response(serializer.errors, status=400)


# 车辆信息视图
class VehicleView(APIView):

    def post(self, request):
        if request.user.vehicle:
            return Response({"detail": "车辆信息已提交，请勿重复操作"}, status=400)

        serializer = VehicleSerializer(data=request.data)
        if serializer.is_valid():
            vehicle = serializer.save()
            request.user.vehicle = vehicle
            request.user.save()
            return Response({"detail": "车辆信息录入成功，等待审核"}, status=201)
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
            instance = serializer.save()
            instance.status = 'pending'  # 修改后重置状态
            instance.save()
            return Response({"detail": "车辆信息更新成功，等待审核"})
        return Response(serializer.errors, status=400)


##########################################################
# 乘客功能视图

# 提交打车请求
class SubmitTripRequestView(APIView):
    permission_classes = [IsPassenger]

    def post(self, request):
        serializer = TripRequestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(account=request.user, request_time=timezone.now())
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 查看打车请求状态
class TripRequestStatusView(APIView):
    permission_classes = [IsPassenger]

    def get(self, request):
        requests = TripRequest.objects.filter(account=request.user)
        serializer = TripRequestSerializer(requests, many=True)
        return Response(serializer.data)


# 取消打车请求
class CancelTripRequestView(APIView):
    permission_classes = [IsPassenger]

    def post(self, request, pk):
        try:
            trip_request = TripRequest.objects.get(id=pk, account=request.user)
            if trip_request.status not in ['completed', 'cancelled']:
                trip_request.status = 'cancelled'
                trip_request.save()
                return Response({'detail': '请求已取消'})
            return Response({'detail': '当前状态不可取消'}, status=status.HTTP_400_BAD_REQUEST)
        except TripRequest.DoesNotExist:
            return Response({'detail': '未找到请求'}, status=status.HTTP_404_NOT_FOUND)


# 查看司机行程列表
class ListOpenRidesView(APIView):
    permission_classes = [IsPassenger]

    def get(self, request):
        open_rides = Ride.objects.filter(status='open').order_by('departure_time')
        serializer = RideListSerializer(open_rides, many=True)
        return Response(serializer.data)
  
# 加入行程  
class JoinRideView(APIView):
    """
    乘客加入一个开放的拼车行程。
    如果乘客已加入，则幂等地返回成功。
    """
    permission_classes = [IsPassenger]

    def post(self, request, ride_id):
        try:
            ride = Ride.objects.get(pk=ride_id)
        except Ride.DoesNotExist:
            return Response({"detail": "该行程不存在。"}, status=status.HTTP_404_NOT_FOUND)

        if TripOrder.objects.filter(
            trip_request__account=request.user,
            driver__account=ride.account,
            trip_request__pickup_location=ride.start_location,
            trip_request__dropoff_location=ride.end_location,
            start_time=ride.departure_time
        ).exists():
            return Response({"detail": "成功加入行程！"}, status=status.HTTP_200_OK)

        with transaction.atomic():
            ride = Ride.objects.select_for_update().get(pk=ride_id)

            if ride.status != 'open':
                return Response({"detail": "该行程当前不可加入。"}, status=status.HTTP_400_BAD_REQUEST)
            if ride.available_seats <= 0:
                return Response({"detail": "该行程已满员。"}, status=status.HTTP_400_BAD_REQUEST)
            if ride.account == request.user:
                return Response({"detail": "您不能加入自己的行程。"}, status=status.HTTP_400_BAD_REQUEST)

            ride.available_seats -= 1
            if ride.available_seats == 0:
                ride.status = 'full'
            ride.save()

            # --- 修正点 ---
            # 在创建 TripRequest 时，添加 request_time 字段
            trip_request = TripRequest.objects.create(
                account=request.user,
                trip_type='拼车',
                pickup_location=ride.start_location,
                dropoff_location=ride.end_location,
                scheduled_time=ride.departure_time,
                request_time=timezone.now(),  # <-- 新增此行，记录当前请求时间
                seats_needed=1,
                status='matched'
            )
            
            try:
                driver_profile = Driver.objects.get(account=ride.account)
            except Driver.DoesNotExist:
                return Response({"detail": "找不到该行程的司机信息。"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            TripOrder.objects.create(
                trip_request=trip_request,
                driver=driver_profile,
                payment_status='pending',
                start_time=ride.departure_time
            )

        return Response({"detail": "成功加入行程！"}, status=status.HTTP_200_OK)


# 查看历史订单
class PassengerOrderHistoryView(APIView):
    permission_classes = [IsPassenger]

    def get(self, request):
        orders = TripOrder.objects.filter(trip_request__account=request.user)
        serializer = TripOrderSerializer(orders, many=True)
        return Response(serializer.data)


# 评价司机
class SubmitDriverReviewView(APIView):
    permission_classes = [IsPassenger]

    def post(self, request):
        serializer = ReviewSerializer(data=request.data, context={'request': request}) # 正确的方式
        if serializer.is_valid():
            # 此处的 reviewer 也可以在序列化器内部自动设置，但现在这样写也没问题
            serializer.save(reviewer=request.user)
            return Response({'detail': '评价已提交'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 获取优惠券列表
class PassengerCouponsView(APIView):
    permission_classes = [IsPassenger]

    def get(self, request):
        user_coupons = UserCoupon.objects.filter(account=request.user)
        now = timezone.now()
        active_platform_coupons = Coupon.objects.filter(valid_from__lte=now,
                                                        valid_until__gte=now)
        user_serializer = UserCouponSerializer(user_coupons, many=True)
        coupon_serializer = CouponSerializer(active_platform_coupons, many=True)
        return Response({
            'my_coupons': user_serializer.data,
            'available': coupon_serializer.data
        })


# 领取优惠券
class ReceiveCouponView(APIView):
    permission_classes = [IsPassenger]

    def post(self, request, coupon_id):
        try:
            coupon = Coupon.objects.get(id=coupon_id)
            UserCoupon.objects.create(account=request.user, coupon=coupon, acquired_at=timezone.now(), status='active')
            return Response({'detail': '领取成功'})
        except Coupon.DoesNotExist:
            return Response({'detail': '优惠券不存在'}, status=status.HTTP_404_NOT_FOUND)


##########################################################
# 司机功能视图

# 发布行程
class CreateTripView(generics.CreateAPIView):
    serializer_class = TripSerializer
    permission_classes = [IsDriver]

    def perform_create(self, serializer):
        serializer.save(account=self.request.user)


# 查看行程
class MyTripsView(generics.ListAPIView):
    serializer_class = TripSerializer
    permission_classes = [IsDriver]

    def get_queryset(self):
        return Ride.objects.filter(account=self.request.user).order_by('-departure_time')


# 取消行程
class CancelRideView(APIView):
    permission_classes = [IsDriver]

    def post(self, request, pk):
        try:
            ride = Ride.objects.get(pk=pk, account=request.user)
            if ride.status == 'open' and ride.available_seats == ride.total_seats:
                # 只有在行程状态为 'open' 且可用座位数等于总座位数时(即没有乘客)才能取消
                ride.status = 'canceled'
                ride.save()
                return Response({"detail": "Ride canceled."}, status=status.HTTP_200_OK)
            return Response({"detail": "Ride cannot be canceled."}, status=status.HTTP_400_BAD_REQUEST)
        except Ride.DoesNotExist:
            return Response({"detail": "Ride not found."}, status=status.HTTP_404_NOT_FOUND)


# 查看待处理的打车请求
class ListPendingTripRequestsView(APIView):
    permission_classes = [IsDriver]

    def get(self, request):
        # 只返回状态为 pending 的请求
        requests = TripRequest.objects.filter(status='pending').order_by('-request_time')
        serializer = TripRequestSerializer(requests, many=True)
        return Response(serializer.data)


# 响应乘客请求 / 接单
class AcceptTripRequestView(APIView):
    permission_classes = [IsDriver]

    def post(self, request, request_id):
        try:
            trip_request = TripRequest.objects.get(id=request_id, status='pending')
        except TripRequest.DoesNotExist:
            return Response({"detail": "请求不存在或已处理"}, status=404)

        driver = Driver.objects.get(account=request.user)

        if trip_request.trip_type == '打车':
            # 直接创建订单
            TripOrder.objects.create(
                trip_request=trip_request,
                driver=driver,
                payment_status='pending',
                start_time=trip_request.scheduled_time or timezone.now()
            )
            trip_request.status = 'matched'
            trip_request.save()
            return Response({"detail": "已接打车订单"})

        elif trip_request.trip_type == '拼车':
            # 匹配 Ride
            matched_ride = Ride.objects.filter(
                account=request.user,
                start_location=trip_request.pickup_address,
                end_location=trip_request.dropoff_address,
                departure_time=trip_request.scheduled_time,
                status='open'
            ).first()

            if not matched_ride:
                return Response({"detail": "无匹配的行程计划"}, status=400)

            if trip_request.seats_needed is None:
                return Response({"detail": "缺少 seats_needed 信息"}, status=400)

            if trip_request.seats_needed > matched_ride.available_seats:
                return Response({"detail": "拼车请求剩余座位不足"}, status=400)

            # 成功接单
            TripOrder.objects.create(
                trip_request=trip_request,
                driver=driver,
                payment_status='pending',
                start_time=matched_ride.departure_time
            )
            trip_request.status = 'matched'
            trip_request.save()

            matched_ride.available_seats -= trip_request.seats_needed
            if matched_ride.available_seats == 0:
                matched_ride.status = 'full'
            matched_ride.save()

            return Response({"detail": "已接拼车订单"})

        return Response({"detail": "不支持的请求类型"}, status=400)


# 查看乘客
class TripPassengersView(APIView):
    permission_classes = [IsDriver]

    def get(self, request, trip_id):
        try:
            trip = TripOrder.objects.get(trip_request=trip_id, driver__account=request.user)
        except TripOrder.DoesNotExist:
            return Response({"detail": "行程不存在"}, status=404)

        passenger = Passenger.objects.get(account=trip.trip_request.account)
        passenger_data = {
            "nickname": passenger.nickname,
            "phone": trip.trip_request.account.phone,
            "pickup_time": trip.trip_request.request_time,
            "pickup_address": trip.trip_request.pickup_address,
            "dropoff_address": trip.trip_request.dropoff_address
        }
        return Response(passenger_data)


# 查看历史订单
class DriverOrderHistoryView(APIView):
    permission_classes = [IsDriver]

    def get(self, request):
        orders = TripOrder.objects.filter(driver__account=request.user)
        serializer = TripOrderSerializer(orders, many=True)
        return Response(serializer.data)


# 评价乘客
class RatePassengerView(generics.CreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [IsDriver]

    def perform_create(self, serializer):
        order = serializer.validated_data['order']
        serializer.save(
            reviewer=self.request.user,
            reviewee=order.passenger,
            created_at=timezone.now()
        )

