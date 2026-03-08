from django.contrib import admin
from .models import Customer, Loan


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['customer_id', 'first_name', 'last_name', 'phone_number', 'monthly_salary', 'approved_limit', 'current_debt']
    search_fields = ['first_name', 'last_name', 'phone_number']
    list_filter = ['age']


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ['loan_id', 'customer', 'loan_amount', 'tenure', 'interest_rate', 'monthly_repayment', 'is_active', 'start_date', 'end_date']
    search_fields = ['loan_id', 'customer__first_name', 'customer__last_name']
    list_filter = ['is_active', 'start_date']
    date_hierarchy = 'start_date'
