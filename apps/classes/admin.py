from django.contrib import admin
from .models import Subject, Class, Enrollment, ParentStudent


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ["subject_name", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["subject_name"]


@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ["class_code", "class_name", "subject", "teacher", "get_student_count", "room", "is_active"]
    list_filter = ["subject", "is_active"]
    search_fields = ["class_code", "class_name", "teacher__first_name", "teacher__last_name"]
    filter_horizontal = ["assistants"]


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ["student", "class_enrolled", "status", "enrolled_at"]
    list_filter = ["status", "class_enrolled"]
    search_fields = ["student__full_name", "class_enrolled__class_name"]


@admin.register(ParentStudent)
class ParentStudentAdmin(admin.ModelAdmin):
    list_display = ["parent", "student", "relationship"]
    list_filter = ["relationship"]
    search_fields = ["parent__first_name", "parent__last_name", "student__full_name"]
