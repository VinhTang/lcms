import re
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    ROLE_CHOICES = [
        ("admin", "Quản trị viên"),
        ("teacher", "Giáo viên"),
        ("assistant", "Trợ giảng"),
        ("parent", "Phụ huynh"),
    ]
    GENDER_CHOICES = [
        ("male", "Nam"),
        ("female", "Nữ"),
        ("other", "Khác"),
    ]

    domain = models.CharField(max_length=100, unique=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="teacher")

    class Meta:
        db_table = "users"
        ordering = ["-date_joined"]

    def __str__(self):
        return f"{self.get_full_name()} ({self.domain})"

    def save(self, *args, **kwargs):
        if not self.domain:
            self.domain = self.generate_domain()
        if not self.username:
            self.username = self.domain
        super().save(*args, **kwargs)

    @staticmethod
    def clean_first_name(first_name):
        if not first_name:
            return ""
        first_name = first_name.strip()
        first_name = re.sub(r'[0-9]', '', first_name)
        first_name = re.sub(r'[^aăâbcdđeêghiklmnoôơpqrstuưvxyząâbcdefghijklmnopqrstuvxyz\s]', '', first_name, flags=re.IGNORECASE)
        return first_name

    @staticmethod
    def clean_last_name(last_name):
        if not last_name:
            return ""
        last_name = last_name.strip()
        last_name = re.sub(r'\s+', '', last_name)
        return last_name

    def generate_domain(self):
        last_name = self.clean_last_name(self.last_name or "")
        first_name = self.clean_first_name(self.first_name or "")

        first_name_normalized = first_name.replace(" ", "")

        base_domain = f"{last_name}{first_name_normalized}".lower()

        if not base_domain:
            base_domain = "user"

        domain = base_domain
        counter = 2
        max_attempts = 100

        while User.objects.filter(domain=domain).exclude(id=self.id).exists() and counter <= max_attempts:
            domain = f"{base_domain}{counter}"
            counter += 1

        return domain
