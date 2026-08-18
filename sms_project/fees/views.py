from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404

from accounts.decorators import admin_required, student_required
from accounts.view_helpers import confirm_and_delete
from .models import FeeRecord, Payment
from .forms import FeeRecordForm, PaymentForm


@admin_required
def fee_list(request):
    records = FeeRecord.objects.select_related('student', 'student__user').all()
    return render(request, 'fees/fee_list.html', {'records': records})


@admin_required
def fee_form(request, pk=None):
    record = get_object_or_404(FeeRecord, pk=pk) if pk else None
    if request.method == 'POST':
        form = FeeRecordForm(request.POST, instance=record)
        if form.is_valid():
            form.save()
            messages.success(request, 'Fee record saved successfully.')
            return redirect('fees:list')
    else:
        form = FeeRecordForm(instance=record)
    return render(request, 'generic_form.html', {
        'form': form, 'heading': 'Edit Fee Record' if record else 'Add Fee Record', 'cancel_url': '/fees/',
    })


@admin_required
def fee_delete(request, pk):
    record = FeeRecord.objects.filter(pk=pk).first()
    return confirm_and_delete(
        request, record, 'fees:list', '/fees/',
        message='All payment history for this fee record will also be deleted.',
        success_message='Fee record deleted.',
    )


@admin_required
def fee_detail(request, pk):
    record = get_object_or_404(FeeRecord, pk=pk)
    if request.method == 'POST':
        # Bind fee_record onto the instance BEFORE validation, since
        # PaymentForm doesn't expose that field and Payment.clean() needs it.
        form = PaymentForm(request.POST, instance=Payment(fee_record=record))
        if form.is_valid():
            form.save()  # Payment.save() recalculates fee_record.paid_amount itself
            messages.success(request, 'Payment recorded.')
            return redirect('fees:detail', pk=record.pk)
    else:
        form = PaymentForm()
    record.refresh_from_db()
    return render(request, 'fees/fee_detail.html', {'record': record, 'form': form, 'payments': record.payments.all()})


@admin_required
def payment_delete(request, pk):
    """Priority 1, issue #4: deleting a payment must recalculate the fee
    record's paid_amount — Payment.delete() now handles that automatically."""
    payment = get_object_or_404(Payment, pk=pk)
    fee_record_pk = payment.fee_record_id
    if request.method == 'POST':
        payment.delete()
        messages.success(request, 'Payment deleted and fee balance updated.')
        return redirect('fees:detail', pk=fee_record_pk)
    return render(request, 'generic_confirm_delete.html', {
        'object_label': str(payment),
        'cancel_url': f'/fees/{fee_record_pk}/',
        'message': "This will reduce the fee record's paid amount accordingly.",
    })


@student_required
def my_fees(request):
    student = getattr(request.user, 'student_profile', None)
    records = student.fee_records.all() if student else []
    return render(request, 'fees/my_fees.html', {'records': records})
