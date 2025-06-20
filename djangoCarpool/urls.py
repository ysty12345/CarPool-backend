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
    SubmitTripRequestView, TripRequestStatusView, CancelTripRequestView,
    PassengerOrderHistoryView, SubmitDriverReviewView, PassengerCouponsView, ReceiveCouponView,
    CreateTripView, MyTripsView, AcceptTripRequestView, TripPassengersView, RatePassengerView,
    CancelRideView, ListPendingTripRequestsView, DriverOrderHistoryView, ListOpenRidesView, JoinRideView
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
    path('api/passenger/trip/request/', SubmitTripRequestView.as_view(), name='submit-trip-request'),
    path('api/passenger/trip/status/', TripRequestStatusView.as_view(), name='trip-request-status'),
    path('api/passenger/trip/cancel/<int:pk>/', CancelTripRequestView.as_view(), name='cancel-trip-request'),
    path('api/passenger/rides/open/', ListOpenRidesView.as_view(), name='open-ride-list'),
    path('api/passenger/rides/<int:ride_id>/join/', JoinRideView.as_view(), name='join-ride'),
    path('api/passenger/orders/', PassengerOrderHistoryView.as_view(), name='passenger-orders'),
    path('api/passenger/review/', SubmitDriverReviewView.as_view(), name='submit-driver-review'),
    path('api/passenger/coupons/', PassengerCouponsView.as_view(), name='passenger-coupons'),
    path('api/passenger/coupons/receive/<int:coupon_id>/', ReceiveCouponView.as_view(), name='receive-coupon'),

    # 司机功能接口
    path('api/driver/ride/create/', CreateTripView.as_view(), name='driver-create-trip'),
    path('api/driver/ride/', MyTripsView.as_view(), name='driver-my-trips'),
    path('api/driver/ride/<int:pk>/cancel/', CancelRideView.as_view(), name='driver-ride-cancel'),
    path('api/driver/trip/requests/', ListPendingTripRequestsView.as_view(), name='list-pending-trip-requests'),
    path('api/driver/trip/<int:request_id>/accept/', AcceptTripRequestView.as_view(), name='driver-accept-trip-request'),
    path('api/driver/trip/<int:trip_id>/passengers/', TripPassengersView.as_view(), name='trip-passenger-list'),
    path('api/driver/orders/', DriverOrderHistoryView.as_view(), name='driver-orders'),
    path('api/driver/review/', RatePassengerView.as_view(), name='rate-passenger'),
]
