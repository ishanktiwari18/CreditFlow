from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from datetime import datetime, timedelta
from decimal import Decimal

from .models import Customer, Loan
from .serializers import (
    CustomerRegistrationSerializer,
    LoanEligibilitySerializer,
    LoanEligibilityResponseSerializer,
    LoanCreateSerializer,
    LoanCreateResponseSerializer,
    LoanDetailSerializer,
    CustomerLoanSerializer,
)
from .utils import check_loan_eligibility, calculate_monthly_installment


@api_view(['POST'])
def register_customer(request):
    serializer = CustomerRegistrationSerializer(data=request.data)
    
    if serializer.is_valid():
        customer = serializer.save()
        
        response_data = {
            'customer_id': customer.customer_id,
            'name': f"{customer.first_name} {customer.last_name}",
            'age': customer.age,
            'monthly_income': customer.monthly_salary,
            'approved_limit': customer.approved_limit,
            'phone_number': customer.phone_number,
        }
        
        return Response(response_data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def check_eligibility(request):
    serializer = LoanEligibilitySerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    customer_id = serializer.validated_data['customer_id']
    loan_amount = serializer.validated_data['loan_amount']
    interest_rate = serializer.validated_data['interest_rate']
    tenure = serializer.validated_data['tenure']
    
    eligibility_result = check_loan_eligibility(customer_id, loan_amount, interest_rate, tenure)
    
    response_data = {
        'customer_id': customer_id,
        'approval': eligibility_result['approval'],
        'interest_rate': interest_rate,
        'corrected_interest_rate': eligibility_result['corrected_interest_rate'],
        'tenure': tenure,
        'monthly_installment': eligibility_result['monthly_installment'],
    }
    
    response_serializer = LoanEligibilityResponseSerializer(response_data)
    return Response(response_serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
def create_loan(request):
    serializer = LoanCreateSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    customer_id = serializer.validated_data['customer_id']
    loan_amount = serializer.validated_data['loan_amount']
    interest_rate = serializer.validated_data['interest_rate']
    tenure = serializer.validated_data['tenure']
    
    try:
        customer = Customer.objects.get(customer_id=customer_id)
    except Customer.DoesNotExist:
        return Response(
            {
                'loan_id': None,
                'customer_id': customer_id,
                'loan_approved': False,
                'message': 'Customer not found',
                'monthly_installment': 0,
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
    eligibility_result = check_loan_eligibility(customer_id, loan_amount, interest_rate, tenure)
    
    if not eligibility_result['approval']:
        response_data = {
            'loan_id': None,
            'customer_id': customer_id,
            'loan_approved': False,
            'message': eligibility_result['message'],
            'monthly_installment': 0,
        }
        return Response(response_data, status=status.HTTP_200_OK)
    
    corrected_interest_rate = eligibility_result['corrected_interest_rate']
    monthly_installment = eligibility_result['monthly_installment']
    
    start_date = datetime.now().date()
    end_date = start_date + timedelta(days=tenure * 30)  
    
    loan = Loan.objects.create(
        customer=customer,
        loan_amount=loan_amount,
        tenure=tenure,
        interest_rate=corrected_interest_rate,
        monthly_repayment=monthly_installment,
        emis_paid_on_time=0,
        start_date=start_date,
        end_date=end_date,
        is_active=True,
    )
    customer.current_debt += loan_amount
    customer.save()
    
    response_data = {
        'loan_id': loan.loan_id,
        'customer_id': customer_id,
        'loan_approved': True,
        'message': 'Loan approved successfully',
        'monthly_installment': monthly_installment,
    }
    
    return Response(response_data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def view_loan(request, loan_id):
    try:
        loan = Loan.objects.select_related('customer').get(loan_id=loan_id)
    except Loan.DoesNotExist:
        return Response(
            {'error': 'Loan not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = LoanDetailSerializer(loan)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def view_customer_loans(request, customer_id):
    try:
        customer = Customer.objects.get(customer_id=customer_id)
    except Customer.DoesNotExist:
        return Response(
            {'error': 'Customer not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    loans = Loan.objects.filter(customer=customer, is_active=True)
    serializer = CustomerLoanSerializer(loans, many=True)
    
    return Response(serializer.data, status=status.HTTP_200_OK)
