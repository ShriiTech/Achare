from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser, PermissionsMixin,
)
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from rest_framework_simplejwt.tokens import RefreshToken

from apps.account.models.managers.custom_user_manager import CustomUserManager


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    مدل کاربر سفارشی بر پایه AbstractBaseUser.
    - از ایمیل به‌عنوان شناسه استفاده می‌شود (USERNAME_FIELD = 'email')
    - شامل فیلدهای مفید: first_name, last_name, phone_number, is_staff, is_active, date_joined
    - متد generate_tokens می‌تواند توکن refresh/access را با Simple JWT بسازد.
    """

    email = models.EmailField(_('email address'), unique=True, db_index=True)
    first_name = models.CharField(_('first name'), max_length=150, blank=True)
    last_name = models.CharField(_('last name'), max_length=150, blank=True)
    phone_number = models.CharField(_('phone number'), max_length=20, blank=True, null=True, unique=True)

    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_('Designates whether this user should be treated as active. '
                    'Unselect this instead of deleting accounts.'),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    # اگر بخواهی می‌توانی فیلدهای پروفایل بیشتر اضافه کنی (avatar, bio, language, ...)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # در زمان createsuperuser اگر فیلدی اجباری است اینجا اضافه کن

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ['-date_joined']

    def __str__(self) -> str:
        return self.email

    def get_full_name(self) -> str:
        full = f"{self.first_name} {self.last_name}".strip()
        return full or self.email

    def get_short_name(self) -> str:
        return self.first_name or self.email.split("@")[0]

    def email_user(self, subject: str, message: str, from_email=None, **kwargs):
        """
        متد کمکی برای ارسال ایمیل (در صورت نیاز).
        """
        from django.core.mail import send_mail
        send_mail(subject, message, from_email, [self.email], **kwargs)

    # ----- JWT helpers (Simple JWT) -----
    def generate_jwt_tokens(self) -> dict:
        """
        ساخت توکن access و refresh با استفاده از djangorestframework-simplejwt.
        خروجی نمونه:
        {
            "refresh": "<refresh_token>",
            "access": "<access_token>"
        }
        """
        refresh = RefreshToken.for_user(self)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

    @property
    def tokens(self) -> dict:
        """
        property معادل generate_jwt_tokens برای راحتی دسترسی.
        """
        return self.generate_jwt_tokens()
