import re
from django.db import models
from django.utils import timezone
from simple_history.models import HistoricalRecords


class Student(models.Model):
    GENDER_CHOICES = [
        ("male", "Nam"),
        ("female", "Nữ"),
        ("other", "Khác"),
    ]
    STATUS_CHOICES = [
        ("active", "Đang học"),
        ("inactive", "Nghỉ"),
    ]

    domain = models.CharField(max_length=100, unique=True, blank=True)
    full_name = models.CharField(max_length=200)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)
    birth_year = models.PositiveIntegerField(null=True, blank=True, help_text="Năm sinh")
    school = models.CharField(max_length=200, blank=True, help_text="Trường học")
    emergency_call = models.CharField(max_length=20, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    history = HistoricalRecords()

    class Meta:
        db_table = "students"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.full_name} ({self.domain})"

    def save(self, *args, **kwargs):
        if not self.domain:
            self.domain = self.generate_domain()
            
        is_becoming_inactive = False
        if self.pk:
            old_status = Student.objects.get(pk=self.pk).status
            if old_status == 'active' and self.status in ['inactive', 'deleted']:
                is_becoming_inactive = True
                
        super().save(*args, **kwargs)
        
        if is_becoming_inactive:
            from classes.models import Enrollment
            Enrollment.objects.filter(student=self, status='active').update(
                status='dropped',
                dropped_at=timezone.now()
            )

    @staticmethod
    def clean_name(name):
        """Remove numbers and special characters, keep Vietnamese letters."""
        if not name:
            return ""
        name = name.strip()
        name = re.sub(r'[0-9]', '', name)
        name = re.sub(
            r'[^a-zA-ZàáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđÀÁẢÃẠĂẮẰẲẴẶÂẤẦẨẪẬÈÉẺẼẸÊẾỀỂỄỆÌÍỈĨỊÒÓỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÙÚỦŨỤƯỨỪỬỮỰỲÝỶỸỴĐ\s]',
            '', name
        )
        return name

    @staticmethod
    def remove_diacritics(text):
        """Convert Vietnamese characters to ASCII equivalents."""
        diacritics_map = {
            'à': 'a', 'á': 'a', 'ả': 'a', 'ã': 'a', 'ạ': 'a',
            'ă': 'a', 'ắ': 'a', 'ằ': 'a', 'ẳ': 'a', 'ẵ': 'a', 'ặ': 'a',
            'â': 'a', 'ấ': 'a', 'ầ': 'a', 'ẩ': 'a', 'ẫ': 'a', 'ậ': 'a',
            'è': 'e', 'é': 'e', 'ẻ': 'e', 'ẽ': 'e', 'ẹ': 'e',
            'ê': 'e', 'ế': 'e', 'ề': 'e', 'ể': 'e', 'ễ': 'e', 'ệ': 'e',
            'ì': 'i', 'í': 'i', 'ỉ': 'i', 'ĩ': 'i', 'ị': 'i',
            'ò': 'o', 'ó': 'o', 'ỏ': 'o', 'õ': 'o', 'ọ': 'o',
            'ô': 'o', 'ố': 'o', 'ồ': 'o', 'ổ': 'o', 'ỗ': 'o', 'ộ': 'o',
            'ơ': 'o', 'ớ': 'o', 'ờ': 'o', 'ở': 'o', 'ỡ': 'o', 'ợ': 'o',
            'ù': 'u', 'ú': 'u', 'ủ': 'u', 'ũ': 'u', 'ụ': 'u',
            'ư': 'u', 'ứ': 'u', 'ừ': 'u', 'ử': 'u', 'ữ': 'u', 'ự': 'u',
            'ỳ': 'y', 'ý': 'y', 'ỷ': 'y', 'ỹ': 'y', 'ỵ': 'y',
            'đ': 'd',
            'À': 'a', 'Á': 'a', 'Ả': 'a', 'Ã': 'a', 'Ạ': 'a',
            'Ă': 'a', 'Ắ': 'a', 'Ằ': 'a', 'Ẳ': 'a', 'Ẵ': 'a', 'Ặ': 'a',
            'Â': 'a', 'Ấ': 'a', 'Ầ': 'a', 'Ẩ': 'a', 'Ẫ': 'a', 'Ậ': 'a',
            'È': 'e', 'É': 'e', 'Ẻ': 'e', 'Ẽ': 'e', 'Ẹ': 'e',
            'Ê': 'e', 'Ế': 'e', 'Ề': 'e', 'Ể': 'e', 'Ễ': 'e', 'Ệ': 'e',
            'Ì': 'i', 'Í': 'i', 'Ỉ': 'i', 'Ĩ': 'i', 'Ị': 'i',
            'Ò': 'o', 'Ó': 'o', 'Ỏ': 'o', 'Õ': 'o', 'Ọ': 'o',
            'Ô': 'o', 'Ố': 'o', 'Ồ': 'o', 'Ổ': 'o', 'Ỗ': 'o', 'Ộ': 'o',
            'Ơ': 'o', 'Ớ': 'o', 'Ờ': 'o', 'Ở': 'o', 'Ỡ': 'o', 'Ợ': 'o',
            'Ù': 'u', 'Ú': 'u', 'Ủ': 'u', 'Ũ': 'u', 'Ụ': 'u',
            'Ư': 'u', 'Ứ': 'u', 'Ừ': 'u', 'Ử': 'u', 'Ữ': 'u', 'Ự': 'u',
            'Ý': 'y', 'Ý': 'y', 'Ỷ': 'y', 'Ỹ': 'y', 'Ỵ': 'y',
            'Đ': 'd', 'Ð': 'd',
        }
        result = []
        for char in text:
            result.append(diacritics_map.get(char, char))
        return ''.join(result)

    def generate_domain(self):
        """
        Vietnamese naming: Họ (family) + Tên đệm (middle) + Tên (given).
        Domain = tên (last word) + initials of họ đệm.
        Example: "Nguyễn Văn Nam"
                 -> tên = "Nam", họ đệm = "Nguyễn Văn"
                 -> domain = "nam" + "nv" = "namnv"
        If duplicate: namnv2, namnv3, ...
        """
        full_name = self.clean_name(self.full_name or "")
        parts = full_name.split()

        if not parts:
            base_domain = "student"
        elif len(parts) == 1:
            base_domain = self.remove_diacritics(parts[0]).lower()
        else:
            ten = self.remove_diacritics(parts[-1]).lower()
            initials = ''.join(
                [self.remove_diacritics(p[0]).lower() for p in parts[:-1] if p]
            )
            base_domain = f"{ten}{initials}"

        domain = base_domain
        counter = 2
        max_attempts = 100

        while Student.objects.filter(domain=domain).exclude(id=self.id).exists() and counter <= max_attempts:
            domain = f"{base_domain}{counter}"
            counter += 1

        return domain

    def soft_delete(self):
        self.status = "inactive"
        self.save()
