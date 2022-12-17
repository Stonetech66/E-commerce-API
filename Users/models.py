from django.db import models
# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Permission
import uuid
from django.contrib import auth
from django.core.exceptions import PermissionDenied

# Create your models here.
class UserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, password):

        if not email:
            raise TypeError("Users must have an email")
        
        if not first_name:
            raise TypeError("Users must have a Firstname")
        
        if not last_name:
            raise TypeError("Users must have a lastname")
        
        user= self.model(email=self.normalize_email(email), first_name= first_name, last_name=last_name)
        user.set_password(password)
        user.save(using=self.db)
        return user


    def create_superuser(self, email, first_name, last_name, password):

        user=self.create_user(email=email, password=password, first_name=first_name, last_name=last_name)
        user.is_superuser=True
        user.is_admin= True
        user.save(using=self.db)
        
        return user

def _user_get_permissions(user, obj, from_name):
    permissions = set()
    name = 'get_%s_permissions' % from_name
    for backend in auth.get_backends():
        if hasattr(backend, name):
            permissions.update(getattr(backend, name)(user, obj))
    return permissions


def _user_has_perm(user, perm, obj):
    """
    A backend can raise `PermissionDenied` to short-circuit permission checking.
    """
    for backend in auth.get_backends():
        if not hasattr(backend, 'has_perm'):
            continue
        try:
            if backend.has_perm(user, perm, obj):
                return True
        except PermissionDenied:
            return False
    return False


def _user_has_module_perms(user, app_label):
    """
    A backend can raise `PermissionDenied` to short-circuit permission checking.
    """
    for backend in auth.get_backends():
        if not hasattr(backend, 'has_module_perms'):
            continue
        try:
            if backend.has_module_perms(user, app_label):
                return True
        except PermissionDenied:
            return False
    return False




class MyUser(AbstractBaseUser, PermissionsMixin):
    email=models.EmailField(unique=True, max_length=255)
    first_name= models.CharField(max_length=100)
    last_name=models.CharField(max_length=100)
    id= models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    is_active= models.BooleanField(default=True)
    is_admin= models.BooleanField(default=False)
    objects= UserManager()
    USERNAME_FIELD="email"
    REQUIRED_FIELDS=["last_name", "first_name"]

    @property
    def Fullname(self):
        return f"{self.first_name} {self.last_name}"
    
    def __str__(self):
        return self.email


    def get_user_permissions(self, obj=None):
        """
        Return a list of permission strings that this user has directly.
        Query all available auth backends. If an object is passed in,
        return only permissions matching this object.
        """
        return _user_get_permissions(self, obj, 'user')

    def get_group_permissions(self, obj=None):
        """
        Return a list of permission strings that this user has through their
        groups. Query all available auth backends. If an object is passed in,
        return only permissions matching this object.
        """
        return _user_get_permissions(self, obj, 'group')

    def get_all_permissions(self, obj=None):
        return _user_get_permissions(self, obj, 'all')

    def has_perm(self, perm, obj=None):
        """
        Return True if the user has the specified permission. Query all
        available auth backends, but return immediately if any backend returns
        True. Thus, a user who has permission from a single auth backend is
        assumed to have permission in general. If an object is provided, check
        permissions for that object.
        """
        # Active superusers have all permissions.
        if self.is_active and self.is_superuser:
            return True

        # Otherwise we need to check the backends.
        return _user_has_perm(self, perm, obj)

    def has_perms(self, perm_list, obj=None):
        """
        Return True if the user has each of the specified permissions. If
        object is passed, check if the user has all required perms for it.
        """
        return all(self.has_perm(perm, obj) for perm in perm_list)

    def has_module_perms(self, app_label):
        """
        Return True if the user has any permissions in the given app label.
        Use similar logic as has_perm(), above.
        """
        # Active superusers have all permissions.
        if self.is_active and self.is_superuser:
            return True

        return _user_has_module_perms(self, app_label)
    @property
    def  is_staff(self):
        return self.is_admin


class UserProfile(models.Model):
    user=models.OneToOneField(MyUser, related_name="user_profile", on_delete=models.CASCADE)
    profile_pic=models.ImageField(null=True, blank=True)

    def __str__(self):
        return self.user.email

