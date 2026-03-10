from django.db import models
from accounts.models import User
from students.models import Student
from simple_history.models import HistoricalRecords


class Subject(models.Model):
    subject_name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    history = HistoricalRecords()

    class Meta:
        db_table = "subjects"
        ordering = ["subject_name"]

    def __str__(self):
        return self.subject_name


class Class(models.Model):
    class_code = models.CharField(max_length=50, unique=True)
    class_name = models.CharField(max_length=200)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="classes")
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name="teaching_classes", limit_choices_to={"role": "teacher"})
    assistants = models.ManyToManyField(User, related_name="assistant_classes", blank=True, limit_choices_to={"role": "assistant"})
    schedule_days = models.CharField(max_length=50, blank=True, help_text="e.g., '2,4,6' for Mon=1, Sun=7")
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    room = models.CharField(max_length=100, blank=True)
    max_students = models.IntegerField(default=30)
    tuition_fee = models.IntegerField(null=True, blank=True, help_text="Học phí của lớp (VND)")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    history = HistoricalRecords()

    class Meta:
        db_table = "classes"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.class_code} - {self.class_name}"

    @property
    def active_students_count(self):
        return self.enrollments.filter(status='active', student__status='active').count()

    STATUS_CHOICES = [
        ('pending', 'Chưa bắt đầu'),
        ('active', 'Khai giảng'),
        ('completed', 'Kết thúc'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def save(self, *args, **kwargs):
        from django.utils import timezone
        from django.core.exceptions import ValidationError
        
        # Strict rule: Cannot activate class before start_date
        if self.status == 'active' and self.start_date:
            if self.start_date > timezone.now().date():
                raise ValidationError(f'Lớp {self.class_name} chưa đến ngày khai giảng ({self.start_date}).')
        
        if self.status == 'active' and not self.start_date:
            # If no start date, we shouldn't really be 'active' unless it's a legacy case, 
            # but user specifically said "Lớp chưa khai giảng... không được mở"
            # So we might want a start date to be required for active status.
            pass

        super().save(*args, **kwargs)

    @property
    def get_schedule_display(self):
        if not self.schedule_days:
            return ""
        
        days_map = {
            '0': 'Chủ nhật',
            '1': 'Thứ 2',
            '2': 'Thứ 3',
            '3': 'Thứ 4',
            '4': 'Thứ 5',
            '5': 'Thứ 6',
            '6': 'Thứ 7'
        }
        
        days = self.schedule_days.split(',')
        formatted_days = [days_map.get(day.strip(), day.strip()) for day in days if day.strip()]
        
        if not formatted_days:
            return ""
            
        return ", ".join(formatted_days)

    def get_student_count(self):
        return self.enrollments.filter(status="active", student__status="active").count()

    def soft_delete(self):
        """Soft delete the class and drop all active enrollments."""
        self.is_active = False
        self.save()
        
        from django.utils import timezone
        for enrollment in self.enrollments.filter(status="active"):
            enrollment.status = "dropped"
            enrollment.dropped_at = timezone.now()
            enrollment.save()

    def sync_status(self):
        """Calculates and sets the status based on start_date and end_date."""
        from django.utils import timezone
        import datetime
        now_date = timezone.now().date()
        
        start_date = self.start_date
        end_date = self.end_date
        
        # Ensure we have date objects for comparison if they are passed as strings (e.g. from a form)
        if isinstance(start_date, str) and start_date:
            try:
                start_date = datetime.date.fromisoformat(start_date)
            except ValueError:
                pass
        
        if isinstance(end_date, str) and end_date:
            try:
                end_date = datetime.date.fromisoformat(end_date)
            except ValueError:
                pass

        if start_date and isinstance(start_date, datetime.date) and start_date > now_date:
            self.status = 'pending'
        elif end_date and isinstance(end_date, datetime.date) and end_date < now_date:
            self.status = 'completed'
        elif start_date and isinstance(start_date, datetime.date) and start_date <= now_date:
            # If end_date is missing or end_date >= today
            self.status = 'active'
        # If no dates are set, we might stick with current or default
        
    def save(self, *args, **kwargs):
        # Auto sync status before saving
        self.sync_status()
        
        # Check if status is transitioning to completed to handle enrollments
        is_new = self.pk is None
        old_status = None
        if not is_new:
            old_instance = Class.objects.filter(pk=self.pk).first()
            if old_instance:
                old_status = old_instance.status
        
        super().save(*args, **kwargs)
        
        # If transitioning to completed, mark enrollments
        if self.status == 'completed' and old_status != 'completed':
            from django.utils import timezone
            for enrollment in self.enrollments.filter(status='active'):
                enrollment.status = 'completed'
                enrollment.dropped_at = timezone.now()
                enrollment.save()


class Enrollment(models.Model):
    STATUS_CHOICES = [
        ("active", "Hoạt động"),
        ("completed", "Hoàn thành"),
        ("dropped", "Đã rời lớp"),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="enrollments")
    class_enrolled = models.ForeignKey(Class, on_delete=models.CASCADE, related_name="enrollments")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    enrolled_at = models.DateTimeField(auto_now_add=True)
    dropped_at = models.DateTimeField(null=True, blank=True)

    history = HistoricalRecords()

    class Meta:
        db_table = "enrollments"
        unique_together = ["student", "class_enrolled"]
        ordering = ["-enrolled_at"]

    def __str__(self):
        try:
            return f"{self.student.full_name} - {self.class_enrolled.class_name}"
        except Exception:
            return f"Enrollment #{self.pk}"


class ParentStudent(models.Model):
    RELATIONSHIP_CHOICES = [
        ("father", "Cha"),
        ("mother", "Mẹ"),
        ("guardian", "Người giám hộ"),
    ]

    parent = models.ForeignKey(User, on_delete=models.CASCADE, related_name="children", limit_choices_to={"role": "parent"})
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="parents")
    relationship = models.CharField(max_length=50, choices=RELATIONSHIP_CHOICES)

    class Meta:
        db_table = "parent_student"
        unique_together = ["parent", "student"]

    def __str__(self):
        try:
            return f"{self.parent.get_full_name()} - {self.student.full_name}"
        except Exception:
            return f"ParentStudent #{self.pk}"
