import re
from django.db import models
from django.utils import timezone


class Student(models.Model):
    GENDER_CHOICES = [
        ("male", "Nam"),
        ("female", "Nữ"),
        ("other", "Khác"),
    ]
    STATUS_CHOICES = [
        ("active", "Hoạt động"),
        ("inactive", "Không hoạt động"),
        ("deleted", "Đã xóa"),
    ]

    domain = models.CharField(max_length=100, unique=True, blank=True)
    full_name = models.CharField(max_length=200)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)
    birth_year = models.PositiveIntegerField(null=True, blank=True, help_text="Năm sinh")
    school = models.CharField(max_length=200, blank=True, help_text="Trường học")
    emergency_call = models.CharField(max_length=20, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    deleted_at = models.DateTimeField(null=True, blank=True)
    restored_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "students"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.full_name} ({self.domain})"

    def save(self, *args, **kwargs):
        if not self.domain:
            self.domain = self.generate_domain()
        super().save(*args, **kwargs)

    @staticmethod
    def clean_name(name):
        if not name:
            return ""
        name = name.strip()
        name = re.sub(r'[0-9]', '', name)
        name = re.sub(r'[^aăâbcdđeêghiklmnoôơpqrstuưvxyząâbcdefghijklmnopqrstuvxyz\s]', '', name, flags=re.IGNORECASE)
        return name

    def generate_domain(self):
        full_name = self.full_name or ""
        parts = full_name.split()

        if len(parts) < 2:
            last_name = self.clean_name(parts[0] if parts else "")
            first_name = ""
        else:
            last_name = self.clean_name(parts[0])
            first_name = ' '.join([self.clean_name(p) for p in parts[1:]])

        first_initials = ""
        if first_name:
            first_parts = first_name.split()
            first_initials = ''.join([p[0].upper() for p in first_parts if p])

        base_domain = f"{last_name}{first_initials}".lower()

        if not base_domain:
            base_domain = "student"

        domain = base_domain
        counter = 2
        max_attempts = 100

        while Student.objects.filter(domain=domain).exclude(id=self.id).exists() and counter <= max_attempts:
            domain = f"{base_domain}{counter}"
            counter += 1

        return domain

    def soft_delete(self):
        self.status = "deleted"
        self.deleted_at = timezone.now()
        self.save()

    def restore(self):
        self.status = "active"
        self.deleted_at = None
        self.restored_at = timezone.now()
        self.save()
