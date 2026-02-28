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
        }
        result = []
        for char in text:
            result.append(diacritics_map.get(char, char))
        return ''.join(result)

    def generate_domain(self):
        """
        Vietnamese naming: Họ (family) + Tên đệm (middle) + Tên (given).
        Domain = tên (last word) + initials of họ đệm.
        Example: last_name="Nguyễn", first_name="Văn Nam"
                 -> full = "Nguyễn Văn Nam"
                 -> tên = "Nam", họ đệm = "Nguyễn Văn"
                 -> domain = "nam" + "nv" = "namnv"
        If duplicate: namnv2, namnv3, ...
        """
        full_name = f"{self.last_name or ''} {self.first_name or ''}".strip()
        full_name = self.clean_name(full_name)
        parts = full_name.split()

        if not parts:
            base_domain = "user"
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

        while User.objects.filter(domain=domain).exclude(id=self.id).exists() and counter <= max_attempts:
            domain = f"{base_domain}{counter}"
            counter += 1

        return domain
