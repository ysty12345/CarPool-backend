from rest_framework.permissions import BasePermission


class IsPassenger(BasePermission):
    """
    仅允许乘客身份访问
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_passenger


class IsDriver(BasePermission):
    """
    仅允许司机身份访问
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_driver


class IsAdvertiser(BasePermission):
    """
    仅允许广告商身份访问
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_advertiser
