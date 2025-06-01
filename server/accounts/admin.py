from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User, Child


class ChildInline(admin.StackedInline):
    model = Child
    extra = 0
    can_delete = True


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'role', 'is_active', 'date_joined')
    list_filter = ('role', 'is_active', 'is_staff', 'is_superuser')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'role', 'phone_number', 'address', 'profile_picture')}),
        (_('Parent info'), {'fields': ('children_info', 'emergency_contact')}),
        (_('Staff info'), {'fields': ('position', 'bio')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'role'),
        }),
    )
    inlines = [ChildInline]


@admin.register(Child)
class ChildAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'parent', 'date_of_birth', 'group')
    list_filter = ('group',)
    search_fields = ('first_name', 'last_name', 'parent__email')
    raw_id_fields = ('parent',)
    fieldsets = (
        (None, {'fields': ('parent', 'first_name', 'last_name', 'date_of_birth', 'group', 'photo')}),
        (_('Medical Information'), {'fields': ('allergies', 'medical_notes')}),
    )
