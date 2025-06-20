# 文件路径: yourapp/tests.py
# 包含了针对 DriverAPITest.setUp 的修正

from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from django.utils import timezone
import json
from datetime import timedelta

from .models import (
    IdentityVerification, Passenger, TripRequest, Ride, Coupon, UserCoupon, Driver, Vehicle, TripOrder
)

Account = get_user_model()


class LoginAPITest(APITestCase):
    # ... 此处省略 ...
    pass

class IdentityVerificationAPITest(APITestCase):
    # ... 此处省略 ...
    pass

class PassengerAPITest(APITestCase):
    # ... 此处省略 ...
    pass

class RideAPITest(APITestCase):
    # ... 此处省略 ...
    pass


class DriverAPITest(APITestCase):
    """
    包含了司机身份及核心操作相关的测试用例 (11, 12, 13, 14, 15, 16)
    """
    def setUp(self):
        """
        创建一个用户，并将其设置为一个完整的“司机”身份，用于后续所有司机功能测试。
        """
        self.user = Account.objects.create_user(phone='13500005555', password='DriverPassword123')
        
        # --- 【核心修正部分】 ---
        # 1. 创建关联的司机对象
        Driver.objects.create(account=self.user, rating=5.0)
        # 2. 将用户的 is_driver 标志位设为 True
        self.user.is_driver = True
        self.user.save()
        # ---

        # 模拟登录
        self.client.force_authenticate(user=self.user)

    def test_create_driver_succeeds_with_approved_verifications(self):
        """
        测试用例ID：11 - 用户在所有认证都审核通过后，成功创建司机身份
        """
        normal_user = Account.objects.create_user(phone='13400004444', password='ValidPassword123')
        self.client.force_authenticate(user=normal_user)
        
        identity = IdentityVerification.objects.create(status='approved', realname='司机A', idnumber='111', driverlicense='111')
        vehicle = Vehicle.objects.create(status='approved', brand='A', model='B', color='C', plate_number='沪A111', seats=4)
        normal_user.identity_verification = identity
        normal_user.vehicle = vehicle
        normal_user.save()
        
        self.assertFalse(normal_user.is_driver)

        url = '/api/driver/create/'
        
        # --- 【核心修正部分】 ---
        # 创建司机时，需要提供 rating 字段
        data = {'rating': 5.0}
        # ---

        print("\n--- [Test Case 11: Create Driver - Success] ---")
        print(f"Input Data --> {json.dumps(data, ensure_ascii=False, indent=2)}")

        # --- 【核心修正部分】 ---
        # 将 data 添加到 post 请求中
        response = self.client.post(url, data, format='json')
        # ---

        print(f"Response Body <-- {json.dumps(response.data, ensure_ascii=False, indent=2)}")
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['detail'], '司机身份创建成功')
        normal_user.refresh_from_db()
        self.assertTrue(normal_user.is_driver)
        
    def test_create_driver_fails_without_identity_verification(self):
        """
        测试用例ID：12 - 用户在实名认证未通过审核时，创建司机身份失败
        """
        normal_user = Account.objects.create_user(phone='13400004445', password='ValidPassword123')
        self.client.force_authenticate(user=normal_user)
        self.assertIsNone(normal_user.identity_verification)

        url = '/api/driver/create/'
        print("\n--- [Test Case 12: Create Driver - No Identity Verification] ---")
        response = self.client.post(url)
        print(f"Response Body <-- {json.dumps(response.data, ensure_ascii=False, indent=2)}")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], '请先完成实名认证')

    def test_driver_create_ride_succeeds(self):
        """
        测试用例ID：13 - 已认证的司机成功发布一个新的拼车行程
        """
        # setUp 中已确保 self.user 是司机并已登录
        url = '/api/driver/ride/create/'
        data = {
            'start_location': '嘉定北地铁站',
            'end_location': '同济大学嘉定校区',
            'departure_time': (timezone.now() + timedelta(hours=2)).isoformat(),
            'total_seats': 3,
        }
        
        print("\n--- [Test Case 13: Driver Create Ride] ---")
        print(f"Input Data --> {json.dumps(data, ensure_ascii=False, indent=2)}")
        response = self.client.post(url, data, format='json')
        print(f"Response Body <-- {json.dumps(response.data, ensure_ascii=False, indent=2)}")
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Ride.objects.count(), 1)
        new_ride = Ride.objects.first()
        self.assertEqual(new_ride.account, self.user)

    def test_list_pending_trip_requests_succeeds(self):
        """
        测试用例ID：14 - 司机可以获取到当前所有状态为待处理的打车请求列表
        """
        passenger_user = Account.objects.create_user(phone='13600006666', password='PassengerPassword')
        now = timezone.now()
        TripRequest.objects.create(
            account=passenger_user, trip_type='打车', status='pending', seats_needed=1,
            pickup_address='A', pickup_location={'lat': 1, 'lng': 1},
            dropoff_address='B', dropoff_location={'lat': 2, 'lng': 2}, request_time=now
        )
        TripRequest.objects.create(
            account=passenger_user, trip_type='拼车', status='pending', seats_needed=2,
            pickup_address='C', pickup_location={'lat': 3, 'lng': 3},
            dropoff_address='D', dropoff_location={'lat': 4, 'lng': 4}, request_time=now
        )
        TripRequest.objects.create(
            account=passenger_user, trip_type='打车', status='matched', seats_needed=1,
            pickup_address='E', pickup_location={'lat': 5, 'lng': 5},
            dropoff_address='F', dropoff_location={'lat': 6, 'lng': 6}, request_time=now
        )

        url = '/api/driver/trip/requests/'
        print("\n--- [Test Case 14: List Pending Trip Requests] ---")
        response = self.client.get(url)
        print(f"Response Body (Count: {len(response.data)}) <--")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        
    def test_accept_taxi_request_succeeds(self):
        """
        测试用例ID：15 - 司机成功接受一个普通打车请求
        """
        passenger_user = Account.objects.create_user(phone='13700007777', password='PassengerPassword')
        trip_request = TripRequest.objects.create(
            account=passenger_user, trip_type='打车', status='pending', seats_needed=1,
            pickup_address='A', pickup_location={'lat': 1, 'lng': 1},
            dropoff_address='B', dropoff_location={'lat': 2, 'lng': 2}, request_time=timezone.now()
        )
        
        url = f'/api/driver/trip/{trip_request.id}/accept/'
        print(f"\n--- [Test Case 15: Accept Taxi Request (ID: {trip_request.id})] ---")
        response = self.client.post(url)
        print(f"Response Body <-- {json.dumps(response.data, ensure_ascii=False, indent=2)}")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], '已接打车订单')
        trip_request.refresh_from_db()
        self.assertEqual(trip_request.status, 'matched')
        self.assertTrue(TripOrder.objects.filter(trip_request=trip_request).exists())

    def test_accept_carpool_request_fails_not_enough_seats(self):
        """
        测试用例ID：16 - 司机尝试接受一个拼车请求，但其发布的对应行程剩余座位不足
        """
        passenger_user = Account.objects.create_user(phone='13800008888', password='PassengerPassword')
        now = timezone.now()
        scheduled_time = now + timedelta(hours=1)
        
        Ride.objects.create(
            account=self.user, start_location='A', end_location='B',
            departure_time=scheduled_time, total_seats=2, available_seats=2, status='open'
        )
        trip_request = TripRequest.objects.create(
            account=passenger_user, trip_type='拼车', status='pending', seats_needed=3,
            pickup_address='A', pickup_location={'lat': 1, 'lng': 1},
            dropoff_address='B', dropoff_location={'lat': 2, 'lng': 2}, 
            request_time=now, scheduled_time=scheduled_time
        )
        
        url = f'/api/driver/trip/{trip_request.id}/accept/'
        print(f"\n--- [Test Case 16: Accept Carpool - Not Enough Seats (Req ID: {trip_request.id})] ---")
        response = self.client.post(url)
        print(f"Response Body <-- {json.dumps(response.data, ensure_ascii=False, indent=2)}")
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], '拼车请求剩余座位不足')