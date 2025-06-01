from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """Custom user manager for User model with email as the unique identifier."""
    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular user with the given email and password."""
        if not email:
            raise ValueError(_('The Email field must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a superuser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', User.Role.ADMIN)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Custom User model with additional fields for daycare roles."""
    
    class Role(models.TextChoices):
        PARENT = 'PARENT', _('Parent')
        STAFF = 'STAFF', _('Staff')
        ADMIN = 'ADMIN', _('Admin')
    
    username = None  # Remove username field
    email = models.EmailField(_('email address'), unique=True)
    role = models.CharField(_('role'), max_length=10, choices=Role.choices, default=Role.PARENT)
    phone_number = models.CharField(_('phone number'), max_length=15, blank=True)
    address = models.TextField(_('address'), blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True)
    
    # For parents
    children_info = models.TextField(_('children information'), blank=True, help_text=_('Information about children'))
    emergency_contact = models.CharField(_('emergency contact'), max_length=100, blank=True)
    
    # For staff
    position = models.CharField(_('position'), max_length=100, blank=True, help_text=_('Staff position/title'))
    bio = models.TextField(_('bio'), blank=True, help_text=_('Staff biography'))
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    objects = UserManager()
    
    def __str__(self):
        return self.email
    
    @property
    def is_parent(self):
        return self.role == self.Role.PARENT
    
    @property
    def is_staff_member(self):
        return self.role == self.Role.STAFF
    
    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN


class Child(models.Model):
    """Model to store information about children of parents."""
    parent = models.ForeignKey(User, on_delete=models.CASCADE, related_name='children')
    first_name = models.CharField(_('first name'), max_length=100)
    last_name = models.CharField(_('last name'), max_length=100)
    date_of_birth = models.DateField(_('date of birth'))
    allergies = models.TextField(_('allergies'), blank=True)
    medical_notes = models.TextField(_('medical notes'), blank=True)
    photo = models.ImageField(upload_to='children_photos/', blank=True, null=True)
    group = models.CharField(_('group'), max_length=50, blank=True, help_text=_('Class/Group assignment'))
    
    class Meta:
        verbose_name = _('child')
        verbose_name_plural = _('children')
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def age(self):
        from datetime import date
        today = date.today()
        return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
