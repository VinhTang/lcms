from django.db import models
from django.utils import timezone
from classes.models import Enrollment
from simple_history.models import HistoricalRecords


class Tuition(models.Model):
    TUITION_TYPE_CHOICES = [
        ("monthly", "Theo tháng"),
        ("course", "Theo khóa học"),
    ]
    PAYMENT_METHOD_CHOICES = [
        ("cash", "Tiền mặt"),
        ("transfer", "Chuyển khoản"),
        ("card", "Thẻ"),
    ]

    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name="tuitions")
    tuition_type = models.CharField(max_length=20, choices=TUITION_TYPE_CHOICES, default="monthly")
    month = models.CharField(max_length=7, blank=True, help_text="YYYY-MM format")
    course_name = models.CharField(max_length=200, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    paid = models.BooleanField(default=False)
    paid_at = models.DateTimeField(null=True, blank=True)
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    history = HistoricalRecords()

    class Meta:
        db_table = "tuition"
        unique_together = [["enrollment", "month"], ["enrollment", "course_name"]]
        ordering = ["-created_at"]

    def __str__(self):
        if self.tuition_type == "monthly":
            return f"{self.enrollment.student.full_name} - {self.enrollment.class_enrolled.class_name} - {self.month}"
        return f"{self.enrollment.student.full_name} - {self.enrollment.class_enrolled.class_name} - {self.course_name}"

    def mark_as_paid(self, payment_method=None):
        self.paid = True
        self.paid_at = timezone.now()
        if payment_method:
            self.payment_method = payment_method
        self.save()

        PaymentHistory.objects.create(
            tuition=self,
            amount=self.amount,
            paid_at=self.paid_at,
            payment_method=self.payment_method
        )


class PaymentHistory(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ("cash", "Tiền mặt"),
        ("transfer", "Chuyển khoản"),
        ("card", "Thẻ"),
    ]

    tuition = models.ForeignKey(Tuition, on_delete=models.CASCADE, related_name="payment_histories")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_at = models.DateTimeField()
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES, blank=True)
    notes = models.TextField(blank=True)

    history = HistoricalRecords()

    class Meta:
        db_table = "payment_histories"
        ordering = ["-paid_at"]

    def __str__(self):
        return f"{self.tuition} - {self.amount}"
