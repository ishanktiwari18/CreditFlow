from celery import shared_task
import pandas as pd
from datetime import datetime
from decimal import Decimal
from django.db import connection
from .models import Customer, Loan


@shared_task
def ingest_customer_data(file_path):
    try:
        df = pd.read_excel(file_path)
        
        customers_created = 0
        for _, row in df.iterrows():
            if Customer.objects.filter(customer_id=row['Customer ID']).exists():
                continue
            
            Customer.objects.create(
                customer_id=row['Customer ID'],
                first_name=row['First Name'],
                last_name=row['Last Name'],
                age=row['Age'],
                phone_number=row['Phone Number'],
                monthly_salary=Decimal(str(row['Monthly Salary'])),
                approved_limit=Decimal(str(row['Approved Limit'])),
                current_debt=0 
            )
            customers_created += 1
        
        if customers_created > 0:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT setval(pg_get_serial_sequence('customers', 'customer_id'), 
                                  COALESCE((SELECT MAX(customer_id) FROM customers), 1), 
                                  true);
                """)
        
        return f"Successfully ingested {customers_created} customers"
    
    except Exception as e:
        return f"Error ingesting customer data: {str(e)}"


@shared_task
def ingest_loan_data(file_path):
    try:
        df = pd.read_excel(file_path)
        
        loans_created = 0
        for _, row in df.iterrows():
            try:
                customer = Customer.objects.get(customer_id=row['Customer ID'])
            except Customer.DoesNotExist:
                continue
            
            if Loan.objects.filter(loan_id=row['Loan ID']).exists():
                continue
        
            start_date = pd.to_datetime(row['Date of Approval']).date()
            end_date = pd.to_datetime(row['End Date']).date()
            
            is_active = end_date > datetime.now().date()
            

            Loan.objects.create(
                loan_id=row['Loan ID'],
                customer=customer,
                loan_amount=Decimal(str(row['Loan Amount'])),
                tenure=int(row['Tenure']),
                interest_rate=Decimal(str(row['Interest Rate'])),
                monthly_repayment=Decimal(str(row['Monthly payment'])),
                emis_paid_on_time=int(row['EMIs paid on Time']),
                start_date=start_date,
                end_date=end_date,
                is_active=is_active,
            )
            loans_created += 1
        
        if loans_created > 0:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT setval(pg_get_serial_sequence('loans', 'loan_id'), 
                                  COALESCE((SELECT MAX(loan_id) FROM loans), 1), 
                                  true);
                """)
        

        update_customer_debt()
        
        return f"Successfully ingested {loans_created} loans"
    
    except Exception as e:
        return f"Error ingesting loan data: {str(e)}"


def update_customer_debt():
    customers = Customer.objects.all()
    
    for customer in customers:
        active_loans = Loan.objects.filter(customer=customer, is_active=True)
        total_debt = sum(loan.loan_amount for loan in active_loans)
        customer.current_debt = total_debt
        customer.save()


@shared_task
def ingest_all_data(customer_file_path, loan_file_path):
    customer_result = ingest_customer_data(customer_file_path)
    loan_result = ingest_loan_data(loan_file_path)
    
    return {
        'customer_ingestion': customer_result,
        'loan_ingestion': loan_result,
    }