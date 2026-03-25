from django.db import models
from django.utils import timezone
from classes.models import Enrollment
from simple_history.models import HistoricalRecords


class Tuition(models.Model):
    TUITION_TYPE_CHOICES = [
        ("monthly", "Theo tháng"),
        ("course", "Theo khóa học"),
    ]

    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name="tuitions")
    tuition_type = models.CharField(max_length=20, choices=TUITION_TYPE_CHOICES, default="monthly")
    month = models.CharField(max_length=7, blank=True, help_text="YYYY-MM format")
    course_name = models.CharField(max_length=200, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    paid = models.BooleanField(default=False)
    paid_at = models.DateTimeField(null=True, blank=True)

    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    history = HistoricalRecords()

    class Meta:
        db_table = "tuition"
        unique_together = [["enrollment", "month"]]
        ordering = ["-created_at"]

    def __str__(self):
        try:
            if self.tuition_type == "monthly":
                return f"{self.enrollment.student.full_name} - {self.enrollment.class_enrolled.class_name} - {self.month}"
            return f"{self.enrollment.student.full_name} - {self.enrollment.class_enrolled.class_name} - {self.course_name}"
        except Exception:
            return f"Tuition #{self.pk}"

    def mark_as_paid(self):
        self.paid = True
        self.paid_at = timezone.now()
        self.save()

        PaymentHistory.objects.create(
            tuition=self,
            amount=self.amount,
            paid_at=self.paid_at,
        )


class PaymentHistory(models.Model):
    tuition = models.ForeignKey(Tuition, on_delete=models.CASCADE, related_name="payment_histories")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_at = models.DateTimeField()
    notes = models.TextField(blank=True)

    history = HistoricalRecords()

    class Meta:
        db_table = "payment_histories"
        ordering = ["-paid_at"]

    def __str__(self):
        try:
            return f"{self.tuition} - {self.amount}"
        except Exception:
            return f"PaymentHistory #{self.pk}"
