from django.db import models
from django.utils import timezone
from accounts.models import User
from classes.models import Class, Enrollment


class ClassSession(models.Model):
    STATUS_CHOICES = [
        ("not_started", "Chưa bắt đầu"),
        ("in_progress", "Đang diễn ra"),
        ("ended", "Đã kết thúc"),
    ]

    class_enrolled = models.ForeignKey(Class, on_delete=models.CASCADE, related_name="sessions")
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name="class_sessions")
    scheduled_date = models.DateField()
    scheduled_start = models.TimeField()
    scheduled_end = models.TimeField()
    actual_start = models.DateTimeField(null=True, blank=True)
    actual_end = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="not_started")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "class_sessions"
        ordering = ["-scheduled_date", "-scheduled_start"]

    def __str__(self):
        return f"{self.class_enrolled.class_code} - {self.scheduled_date}"

    def open_class(self):
        self.status = "in_progress"
        self.actual_start = timezone.now()
        self.save()

    def end_class(self):
        self.status = "ended"
        self.actual_end = timezone.now()
        self.save()
        self.mark_unmarked_as_not_marked()

    def mark_unmarked_as_not_marked(self):
        enrollments = Enrollment.objects.filter(
            class_enrolled=self.class_enrolled,
            status="active"
        )
        for enrollment in enrollments:
            Attendance.objects.get_or_create(
                class_session=self,
                enrollment=enrollment,
                defaults={"status": "not_marked"}
            )


class Attendance(models.Model):
    STATUS_CHOICES = [
        ("present", "Có mặt"),
        ("absent_with_permission", "Vắng có phép"),
        ("absent_without_permission", "Vắng không phép"),
        ("not_marked", "Chưa điểm danh"),
    ]

    class_session = models.ForeignKey(ClassSession, on_delete=models.CASCADE, related_name="attendances")
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name="attendances")
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="not_marked")
    marked_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="marked_attendances")
    marked_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = "attendance"
        unique_together = ["class_session", "enrollment"]
        ordering = ["class_session", "enrollment__student__full_name"]

    def __str__(self):
        return f"{self.enrollment.student.full_name} - {self.class_session.class_enrolled.class_code} - {self.get_status_display()}"

    def mark(self, status, marked_by):
        self.status = status
        self.marked_by = marked_by
        self.marked_at = timezone.now()
        self.save()


class AttendanceEditLog(models.Model):
    attendance = models.ForeignKey(Attendance, on_delete=models.CASCADE, related_name="edit_logs")
    old_status = models.CharField(max_length=30)
    new_status = models.CharField(max_length=30)
    edited_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    reason = models.TextField()
    edited_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "attendance_edit_logs"
        ordering = ["-edited_at"]

    def __str__(self):
        return f"Edit {self.attendance} - {self.old_status} -> {self.new_status}"
