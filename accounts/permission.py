from rest_framework.permissions import BasePermission


class IsManager(BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user , "userprofile") and request.user.userprofile.role == "manager"
    
class IsAdmin(BasePermission):
     def has_permission(self, request, view):
        return hasattr(request.user , "userprofile") and request.user.userprofile.role == "admin"

class IsStaff(BasePermission):
     def has_permission(self, request, view):
        return hasattr(request.user , "userprofile") and request.user.userprofile.role == "staff"

class IsStaffOrManagerOrAdmin(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        return hasattr(request.user, "userprofile") and request.user.userprofile.role in ["staff", "manager", "admin"]

class IsManagerOrAdmin(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        return hasattr(request.user, "userprofile") and request.user.userprofile.role in ["manager", "admin"]
