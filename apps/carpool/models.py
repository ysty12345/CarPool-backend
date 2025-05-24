from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


# Create your models here.


# 自定义用户管理器
class AccountManager(BaseUserManager):
    def create_user(self, phone, password=None, **extra_fields):
        print("create_user")
        if not phone:
            raise ValueError('手机号必须填写')
        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password=None, **extra_fields):
        print("create_superuser")
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(phone, password, **extra_fields)

    def create_staff(self, phone, password=None, **extra_fields):
        print("create_staff")
        extra_fields.setdefault('is_staff', True)
        return self.create_user(phone, password, **extra_fields)


# 账号表
class Account(AbstractBaseUser, PermissionsMixin):
    phone = models.CharField(max_length=20, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    identity_verification = models.OneToOneField('IdentityVerification', on_delete=models.SET_NULL, null=True,
                                                 blank=True)
    vehicle = models.OneToOneField('Vehicle', on_delete=models.SET_NULL, null=True, blank=True)

    is_passenger = models.BooleanField(default=False)
    is_driver = models.BooleanField(default=False)
    is_advertiser = models.BooleanField(default=False)

    # 关键字段：让 Django admin 知道权限
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'phone'
    objects = AccountManager()

    def __str__(self):
        return self.phone


# 乘客表
class Passenger(models.Model):
    account = models.OneToOneField(Account, on_delete=models.CASCADE)
    nickname = models.CharField(max_length=50)
    rating = models.DecimalField(max_digits=2, decimal_places=1)
    created_at = models.DateTimeField(auto_now_add=True)


# 司机表
class Driver(models.Model):
    account = models.OneToOneField(Account, on_delete=models.CASCADE)
    rating = models.DecimalField(max_digits=2, decimal_places=1)
    created_at = models.DateTimeField(auto_now_add=True)
    services = models.ManyToManyField('RideService', through='DriverService')


# 广告商表
class Advertiser(models.Model):
    account = models.OneToOneField(Account, on_delete=models.CASCADE)
    status = models.CharField(max_length=20,
                              choices=[('pending', '待审核'), ('approved', '已通过'), ('rejected', '已拒绝')],
                              default='pending')
    company_name = models.CharField(max_length=100)
    contact_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    website_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


# 身份认证表
class IdentityVerification(models.Model):
    realname = models.CharField(max_length=50)
    idnumber = models.CharField(max_length=50, unique=True)
    driverlicense = models.CharField(max_length=50, unique=True)
    license_issue_date = models.DateField(null=True, blank=True)
    license_expiry = models.DateField(null=True, blank=True)
    driverlicense_file_url = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=20,
                              choices=[('pending', '待审核'), ('approved', '已通过'), ('rejected', '已拒绝')],
                              default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified_at = models.DateTimeField(auto_now=True)


# 车辆信息表
class Vehicle(models.Model):
    brand = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    color = models.CharField(max_length=20)
    plate_number = models.CharField(max_length=20, unique=True)
    seats = models.IntegerField()
    registration_doc_url = models.CharField(max_length=255)
    status = models.CharField(max_length=20,
                              choices=[('pending', '待审核'), ('approved', '已通过'), ('rejected', '已拒绝')],
                              default='pending')
    created_at = models.DateTimeField(auto_now_add=True)


# 服务类型表
class RideService(models.Model):
    name = models.CharField(max_length=50, unique=True)
    base_fare = models.DecimalField(max_digits=10, decimal_places=2)
    per_km_rate = models.DecimalField(max_digits=10, decimal_places=2)
    per_minute_rate = models.DecimalField(max_digits=10, decimal_places=2)


# 司机与服务类型关系表
class DriverService(models.Model):
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE)
    service = models.ForeignKey(RideService, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('driver', 'service')


# 行程表
class Ride(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('full', 'Full'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled'),
    ]
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    start_location = models.CharField(max_length=255)
    end_location = models.CharField(max_length=255)
    departure_time = models.DateTimeField()
    available_seats = models.IntegerField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='open')


# 打车请求表
class TripRequest(models.Model):
    TRIP_TYPE_CHOICES = [('打车', '打车'), ('拼车', '拼车')]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('matched', 'Matched'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    trip_type = models.CharField(max_length=10, choices=TRIP_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    pickup_location = models.JSONField()
    pickup_address = models.CharField(max_length=255)
    dropoff_location = models.JSONField()
    dropoff_address = models.CharField(max_length=255)
    request_time = models.DateTimeField()
    scheduled_time = models.DateTimeField(null=True, blank=True)
    estimated_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    seats_needed = models.IntegerField(null=True, blank=True)
    pets_needed = models.BooleanField(default=False)


# 订单记录表
class TripOrder(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),  # 等待支付
        ('paid', 'Paid'),  # 已支付
        ('cancelled', 'Cancelled'),  # 已取消
        ('refunded', 'Refunded'),  # 已退款
    ]
    trip_request = models.ForeignKey(TripRequest, on_delete=models.CASCADE)  # 对应的打车请求
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE)  # 对应的司机
    actual_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)  # 实际支付金额
    user_coupon = models.ForeignKey('UserCoupon', on_delete=models.SET_NULL, null=True, blank=True)  # 使用的优惠券（可为空）
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # 折扣金额（可为空）
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES)  # 支付状态
    start_time = models.DateTimeField(null=True)  # 出发时间
    end_time = models.DateTimeField(null=True)  # 到达时间
    route = models.JSONField(null=True, blank=True)  # 行驶路线（GeoJSON 格式或坐标序列）

    # 用户与司机的评分、评价
    passenger_rating = models.DecimalField(max_digits=2, decimal_places=1, null=True, blank=True)  # 乘客对司机评分
    passenger_comment = models.TextField(null=True, blank=True)  # 乘客评论
    driver_rating = models.DecimalField(max_digits=2, decimal_places=1, null=True, blank=True)  # 司机对乘客评分
    driver_comment = models.TextField(null=True, blank=True)  # 司机评论

    created_at = models.DateTimeField(auto_now_add=True)
    last_modified_at = models.DateTimeField(auto_now=True)


# 聊天记录表
class Message(models.Model):
    sender = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='sent_messages')  # 发送方
    receiver = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='received_messages')  # 接收方
    content = models.TextField()  # 消息内容
    timestamp = models.DateTimeField(auto_now_add=True)  # 发送时间

    def __str__(self):
        return f"{self.sender} -> {self.receiver} at {self.timestamp}"


# 用户评价表
class Review(models.Model):
    rating = models.DecimalField(max_digits=2, decimal_places=1)  # 评分（1~5）
    comment = models.TextField()  # 评论内容
    created_at = models.DateTimeField(auto_now_add=True)  # 创建时间
    order = models.ForeignKey(TripOrder, on_delete=models.CASCADE, related_name='reviews')  # 所属订单
    reviewer = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='given_reviews')
    reviewee = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='received_reviews')

    def __str__(self):
        return f"Review for Order {self.order_id} - {self.rating} stars"

    class Meta:
        unique_together = ('order', 'reviewer')


# 优惠券表
class Coupon(models.Model):
    DISCOUNT_TYPE_CHOICES = [('fixed amount', 'Fixed Amount'), ('percentage', 'Percentage')]

    name = models.CharField(max_length=100)  # 名称
    description = models.TextField()  # 描述
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES)  # 折扣类型
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)  # 折扣数值
    min_spend = models.DecimalField(max_digits=10, decimal_places=2)  # 最低消费
    max_discount = models.DecimalField(max_digits=10, decimal_places=2)  # 最大折扣（仅限百分比）
    valid_from = models.DateTimeField()  # 有效期开始
    valid_until = models.DateTimeField()  # 有效期结束
    created_by = models.ForeignKey(Account, on_delete=models.CASCADE)  # 创建者（管理员）
    created_at = models.DateTimeField(auto_now_add=True)  # 创建时间

    def __str__(self):
        return self.name


# 用户优惠券表
class UserCoupon(models.Model):
    STATUS_CHOICES = [('active', 'Active'), ('used', 'Used'), ('expired', 'Expired')]

    account = models.ForeignKey(Account, on_delete=models.CASCADE)  # 用户
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)  # 所属优惠券
    acquired_at = models.DateTimeField(auto_now_add=True)  # 领取时间
    used_at = models.DateTimeField(null=True, blank=True)  # 使用时间（未使用则为空）
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)  # 状态

    def __str__(self):
        return f"{self.account.phone} - {self.coupon.name} ({self.status})"


# 广告表
class Ad(models.Model):
    AD_TYPE_CHOICES = [('banner', 'Banner'), ('popup', 'Popup'), ('video', 'Video')]
    STATUS_CHOICES = [('active', 'Active'), ('paused', 'Paused'), ('completed', 'Completed')]

    advertiser = models.ForeignKey(Advertiser, on_delete=models.CASCADE)  # 广告商
    title = models.CharField(max_length=255)  # 标题
    description = models.TextField()  # 描述
    image_url = models.CharField(max_length=255)  # 图片 URL
    target_url = models.CharField(max_length=255)  # 跳转链接
    ad_type = models.CharField(max_length=10, choices=AD_TYPE_CHOICES)  # 广告类型
    price = models.DecimalField(max_digits=10, decimal_places=2)  # 广告费用
    start_date = models.DateTimeField()  # 投放开始
    end_date = models.DateTimeField()  # 投放结束
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)  # 当前状态
    created_at = models.DateTimeField(auto_now_add=True)  # 创建时间

    def __str__(self):
        return f"{self.title} ({self.status})"
