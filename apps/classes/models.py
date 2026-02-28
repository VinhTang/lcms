from django.db import models
from accounts.models import User
from students.models import Student


class Subject(models.Model):
    subject_name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

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
    room = models.CharField(max_length=100, blank=True)
    max_students = models.IntegerField(default=30)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "classes"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.class_code} - {self.class_name}"

    def get_student_count(self):
        return self.enrollments.filter(status="active").count()


class Enrollment(models.Model):
    STATUS_CHOICES = [
        ("active", "Hoạt động"),
        ("dropped", "Đã rời lớp"),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="enrollments")
    class_enrolled = models.ForeignKey(Class, on_delete=models.CASCADE, related_name="enrollments")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    enrolled_at = models.DateTimeField(auto_now_add=True)
    dropped_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "enrollments"
        unique_together = ["student", "class_enrolled"]
        ordering = ["-enrolled_at"]

    def __str__(self):
        return f"{self.student.full_name} - {self.class_enrolled.class_name}"


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
        return f"{self.parent.get_full_name()} - {self.student.full_name}"
