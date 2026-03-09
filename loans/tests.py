from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from decimal import Decimal
from datetime import datetime, timedelta

from .models import Customer, Loan
from .utils import calculate_credit_score, calculate_monthly_installment, check_loan_eligibility


class CustomerModelTest(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(
            first_name="John",
            last_name="Doe",
            age=30,
            phone_number=1234567890,
            monthly_salary=Decimal('50000.00'),
            approved_limit=Decimal('1800000.00'),
            current_debt=Decimal('0.00')
        )

    def test_customer_creation(self):
        self.assertEqual(self.customer.first_name, "John")
        self.assertEqual(self.customer.last_name, "Doe")
        self.assertEqual(self.customer.age, 30)


class LoanModelTest(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(
            first_name="Jane",
            last_name="Smith",
            age=28,
            phone_number=9876543210,
            monthly_salary=Decimal('60000.00'),
            approved_limit=Decimal('2160000.00'),
            current_debt=Decimal('0.00')
        )
        
        self.loan = Loan.objects.create(
            customer=self.customer,
            loan_amount=Decimal('100000.00'),
            tenure=12,
            interest_rate=Decimal('10.5'),
            monthly_repayment=Decimal('8792.00'),
            emis_paid_on_time=6,
            start_date=datetime.now().date(),
            end_date=datetime.now().date() + timedelta(days=365),
            is_active=True
        )

    def test_loan_creation(self):
        self.assertEqual(self.loan.loan_amount, Decimal('100000.00'))
        self.assertEqual(self.loan.tenure, 12)
        self.assertEqual(self.loan.repayments_left, 6)


class UtilsTest(TestCase):
    def test_calculate_monthly_installment(self):
        loan_amount = Decimal('100000.00')
        interest_rate = Decimal('10.0')
        tenure = 12
        
        emi = calculate_monthly_installment(loan_amount, interest_rate, tenure)
        self.assertGreater(emi, 0)
        self.assertIsInstance(emi, Decimal)

    def test_calculate_credit_score_new_customer(self):
        customer = Customer.objects.create(
            first_name="Test",
            last_name="User",
            age=25,
            phone_number=1111111111,
            monthly_salary=Decimal('40000.00'),
            approved_limit=Decimal('1440000.00'),
            current_debt=Decimal('0.00')
        )
        
        score = calculate_credit_score(customer.customer_id)
        self.assertEqual(score, 100) 


class APITest(APITestCase):
    def test_register_customer(self):
        data = {
            'first_name': 'Alice',
            'last_name': 'Johnson',
            'age': 32,
            'monthly_income': 75000,
            'phone_number': 5555555555
        }
        
        response = self.client.post('/register', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('customer_id', response.data)
        self.assertIn('approved_limit', response.data)

    def test_check_eligibility(self):
     
        customer = Customer.objects.create(
            first_name="Bob",
            last_name="Brown",
            age=35,
            phone_number=6666666666,
            monthly_salary=Decimal('80000.00'),
            approved_limit=Decimal('2880000.00'),
            current_debt=Decimal('0.00')
        )
        
        data = {
            'customer_id': customer.customer_id,
            'loan_amount': 200000,
            'interest_rate': 8.5,
            'tenure': 24
        }
        
        response = self.client.post('/check-eligibility', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('approval', response.data)
        self.assertIn('monthly_installment', response.data)
