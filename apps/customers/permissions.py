from rest_framework import permissions

class IsCustomerOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of a customer profile to view or edit it.
    """
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user

class IsAdminUser(permissions.BasePermission):
    """
    Custom permission to only allow admin users to access the view.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_staff