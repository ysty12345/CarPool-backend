from django.contrib import admin
from .models import (
    Account, Passenger, Driver, Advertiser, Admin as PlatformAdmin,
    IdentityVerification, Vehicle,
    RideService, DriverService,
    Ride, TripRequest, TripOrder,
    Message, Review,
    Coupon, UserCoupon,
    Ad
)


# Register your models here.

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('id', 'phone', 'is_passenger', 'is_driver', 'is_advertiser', 'is_admin', 'created_at')
    search_fields = ('phone',)
    list_filter = ('is_passenger', 'is_driver', 'is_advertiser', 'is_admin')


@admin.register(Passenger)
class PassengerAdmin(admin.ModelAdmin):
    list_display = ('id', 'account', 'nickname', 'rating', 'created_at')
    search_fields = ('account__phone', 'nickname')


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ('id', 'account', 'rating', 'created_at')
    search_fields = ('account__phone',)


@admin.register(Advertiser)
class AdvertiserAdmin(admin.ModelAdmin):
    list_display = ('id', 'account', 'company_name', 'contact_name', 'email', 'created_at')
    search_fields = ('company_name', 'contact_name', 'email')


@admin.register(PlatformAdmin)
class PlatformAdminAdmin(admin.ModelAdmin):
    list_display = ('id', 'account', 'created_at')


@admin.register(IdentityVerification)
class IdentityVerificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'realname', 'idnumber', 'driverlicense', 'created_at')
    search_fields = ('realname', 'idnumber', 'driverlicense')


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('id', 'brand', 'model', 'plate_number', 'seats', 'color', 'created_at')
    search_fields = ('plate_number', 'brand', 'model')


@admin.register(RideService)
class RideServiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'base_fare', 'per_km_rate', 'per_minute_rate')


@admin.register(DriverService)
class DriverServiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'driver', 'service')
    list_filter = ('service',)


@admin.register(Ride)
class RideAdmin(admin.ModelAdmin):
    list_display = ('id', 'account', 'start_location', 'end_location', 'departure_time', 'available_seats', 'status')
    list_filter = ('status', 'departure_time')
    search_fields = ('start_location', 'end_location', 'account__phone')


@admin.register(TripRequest)
class TripRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'account', 'trip_type', 'status', 'pickup_address', 'dropoff_address', 'request_time')
    list_filter = ('trip_type', 'status')
    search_fields = ('pickup_address', 'dropoff_address', 'account__phone')


@admin.register(TripOrder)
class TripOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'trip_request', 'driver', 'actual_price', 'payment_status', 'start_time', 'end_time')
    list_filter = ('payment_status',)
    search_fields = ('trip_request__account__phone', 'driver__account__phone')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'receiver', 'timestamp')
    search_fields = ('sender__phone', 'receiver__phone', 'content')
    list_filter = ('timestamp',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'reviewer', 'reviewee', 'rating', 'created_at')
    list_filter = ('rating',)
    search_fields = ('reviewer__phone', 'reviewee__phone', 'comment')


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'discount_type', 'discount_value', 'min_spend', 'valid_from', 'valid_until', 'created_by')
    list_filter = ('discount_type', 'valid_from', 'valid_until')
    search_fields = ('name', 'description')


@admin.register(UserCoupon)
class UserCouponAdmin(admin.ModelAdmin):
    list_display = ('id', 'account', 'coupon', 'status', 'acquired_at', 'used_at')
    list_filter = ('status', 'acquired_at')
    search_fields = ('account__phone', 'coupon__name')


@admin.register(Ad)
class AdAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'advertiser', 'ad_type', 'price', 'status', 'start_date', 'end_date')
    list_filter = ('ad_type', 'status')
    search_fields = ('title', 'description')
