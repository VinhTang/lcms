from django.contrib import admin
from .models import Tuition, PaymentHistory


@admin.register(Tuition)
class TuitionAdmin(admin.ModelAdmin):
    list_display = ["enrollment", "tuition_type", "month", "course_name", "amount", "due_date", "paid", "paid_at", "payment_method"]
    list_filter = ["paid", "tuition_type", "due_date"]
    search_fields = ["enrollment__student__full_name", "enrollment__class_enrolled__class_name", "month", "course_name"]
    readonly_fields = ["created_at", "paid_at"]
    actions = ["mark_as_paid"]

    def mark_as_paid(self, request, queryset):
        for obj in queryset:
            obj.mark_as_paid()
    mark_as_paid.short_description = "Đánh dấu đã thanh toán"


@admin.register(PaymentHistory)
class PaymentHistoryAdmin(admin.ModelAdmin):
    list_display = ["tuition", "amount", "paid_at", "payment_method"]
    list_filter = ["paid_at", "payment_method"]
    search_fields = ["tuition__enrollment__student__full_name"]
    readonly_fields = ["paid_at"]
