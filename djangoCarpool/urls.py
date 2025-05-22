"""djangoCarpool URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from apps.carpool.views import (
    RegisterView, LoginView,
    PassengerCreateView, PassengerInfoView,
    DriverCreateView, DriverInfoView,
    AdvertiserCreateView, AdvertiserInfoView,
    IdentityVerificationView, VehicleView,
    SubmitTripRequestAPIView, TripRequestStatusAPIView, CancelTripRequestAPIView,
    PassengerOrderHistoryAPIView, SubmitDriverReviewAPIView, PassengerCouponsAPIView, ReceiveCouponAPIView,
    CreateTripView, MyTripsView, AcceptTripRequestView, TripPassengersView, DriverProfileView, RatePassengerView
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # 注册和登录相关接口
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/login/', LoginView.as_view(), name='login'),

    # JWT Token 相关接口
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # 乘客相关接口
    path('api/passenger/create/', PassengerCreateView.as_view(), name='passenger-create'),
    path('api/passenger/info/', PassengerInfoView.as_view(), name='passenger-info'),

    # 司机相关接口
    path('api/driver/create/', DriverCreateView.as_view(), name='driver-create'),
    path('api/driver/info/', DriverInfoView.as_view(), name='driver-info'),
    path('api/identity/', IdentityVerificationView.as_view(), name='identity-verification'),
    path('api/vehicle/', VehicleView.as_view(), name='vehicle'),

    # 广告商相关接口
    path('api/advertiser/create/', AdvertiserCreateView.as_view(), name='advertiser-create'),
    path('api/advertiser/info/', AdvertiserInfoView.as_view(), name='advertiser-info'),

    # 乘客功能接口
    path('api/passenger/trip/request/', SubmitTripRequestAPIView.as_view(), name='submit-trip-request'),
    path('api/passenger/trip/status/', TripRequestStatusAPIView.as_view(), name='trip-request-status'),
    path('api/passenger/trip/cancel/<int:pk>/', CancelTripRequestAPIView.as_view(), name='cancel-trip-request'),
    path('api/passenger/orders/', PassengerOrderHistoryAPIView.as_view(), name='passenger-orders'),
    path('api/passenger/review/', SubmitDriverReviewAPIView.as_view(), name='submit-driver-review'),
    path('api/passenger/coupons/', PassengerCouponsAPIView.as_view(), name='passenger-coupons'),
    path('api/passenger/coupons/receive/<int:coupon_id>/', ReceiveCouponAPIView.as_view(), name='receive-coupon'),

    # 司机功能接口
    path('api/driver/trips/create/', CreateTripView.as_view(), name='driver-create-trip'),
    path('api/driver/trips/', MyTripsView.as_view(), name='driver-my-trips'),
    path('api/driver/trips/accept/', AcceptTripRequestView.as_view(), name='driver-accept-trip-request'),
    path('api/driver/trips/<int:trip_id>/passengers/', TripPassengersView.as_view(), name='trip-passenger-list'),
    path('api/driver/profile/', DriverProfileView.as_view(), name='driver-profile'),
    path('api/driver/reviews/', RatePassengerView.as_view(), name='rate-passenger'),
]
