from django.contrib import admin
from .models import (
    Account, Passenger, Driver, Advertiser,
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
    list_display = ('id', 'phone', 'is_passenger', 'is_driver', 'is_advertiser',
                    'is_staff', 'is_superuser', 'created_at')
    search_fields = ('phone',)
    list_filter = ('is_passenger', 'is_driver', 'is_advertiser', 'is_staff', 'is_superuser')

    fieldsets = (
        (None, {'fields': ('phone', 'password')}),
        ('权限设置', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('个人信息', {'fields': ('is_driver', 'is_passenger', 'is_advertiser', 'identity_verification', 'vehicle')}),
    )
    readonly_fields = ('password',)  # 将密码字段设为只读
    add_fieldsets = (
        (None, {'fields': ('phone', 'password')}),
        ('权限设置', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('个人信息', {'fields': ('is_driver', 'is_passenger', 'is_advertiser', 'identity_verification', 'vehicle')}),
    )


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


@admin.register(IdentityVerification)
class IdentityVerificationAdmin(admin.ModelAdmin):
    # 1. 在列表页直接显示审核状态
    list_display = ('id', 'realname', 'idnumber', 'driverlicense', 'status', 'created_at')

    # 2. 允许在右侧栏按状态进行筛选 (方便你快速找到所有 "待审核" 的记录)
    list_filter = ('status',)

    # 3. 【关键】允许在列表页直接编辑 status 字段
    list_editable = ('status',)

    # 4. 保留搜索功能
    search_fields = ('realname', 'idnumber', 'driverlicense')


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    # 1. 在列表页直接显示审核状态
    list_display = ('id', 'plate_number', 'brand', 'model', 'status', 'created_at')

    # 2. 允许在右侧栏按状态进行筛选
    list_filter = ('status', 'brand')

    # 3. 【关键】允许在列表页直接编辑 status 字段
    list_editable = ('status',)

    # 4. 保留搜索功能
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
    # --- 【核心修正部分】 ---
    # 将 list_display 中的 'trip_request' 和 'driver' 替换为我们自定义的方法名
    list_display = ('id', 'trip_request_info', 'driver_info', 'actual_price', 'payment_status', 'start_time', 'end_time')
    # ---

    list_filter = ('payment_status',)
    search_fields = ('trip_request__account__phone', 'driver__account__phone')
    
    # 编辑页面的字段保持不变
    fields = ('trip_request', 'driver', 'actual_price', 'user_coupon', 'discount_amount', 'payment_status', 'start_time', 'end_time', 'route')
    
    # 自定义方法保持不变
    def trip_request_info(self, obj):
        # 增加一个try-except以防止关联对象被删除后报错
        try:
            return f"请求ID: {obj.trip_request.id} (乘客: {obj.trip_request.account.phone})"
        except (AttributeError, TypeError):
            return "N/A"
    trip_request_info.short_description = '打车请求' # 这是列表页显示的列名

    def driver_info(self, obj):
        try:
            return f"司机ID: {obj.driver.id} ({obj.driver.account.phone})"
        except (AttributeError, TypeError):
            return "N/A"
    driver_info.short_description = '接单司机' # 这是列表页显示的列名

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
