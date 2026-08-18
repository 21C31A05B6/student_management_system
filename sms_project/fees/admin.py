from django.contrib import admin
from .models import FeeRecord, Payment


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0


@admin.register(FeeRecord)
class FeeRecordAdmin(admin.ModelAdmin):
    list_display = ('student', 'academic_year', 'total_amount', 'paid_amount', 'due_amount', 'status')
    list_filter = ('academic_year',)
    search_fields = ('student__student_id',)
    inlines = [PaymentInline]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('receipt_number', 'fee_record', 'amount', 'payment_date', 'method')
