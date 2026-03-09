from rest_framework import serializers
from .models import Customer, Loan


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['customer_id', 'first_name', 'last_name', 'age', 'phone_number', 'monthly_salary', 'approved_limit']


class CustomerRegistrationSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    age = serializers.IntegerField(min_value=18)
    monthly_income = serializers.DecimalField(max_digits=12, decimal_places=2)
    phone_number = serializers.IntegerField()

    def create(self, validated_data):
        monthly_income = validated_data['monthly_income']
        approved_limit = round((36 * float(monthly_income)) / 100000) * 100000

        customer = Customer.objects.create(
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            age=validated_data['age'],
            monthly_salary=monthly_income,
            phone_number=validated_data['phone_number'],
            approved_limit=approved_limit,
            current_debt=0
        )
        return customer


class LoanEligibilitySerializer(serializers.Serializer):
    customer_id = serializers.IntegerField()
    loan_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    interest_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    tenure = serializers.IntegerField()


class LoanEligibilityResponseSerializer(serializers.Serializer):
    customer_id = serializers.IntegerField()
    approval = serializers.BooleanField()
    interest_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    corrected_interest_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    tenure = serializers.IntegerField()
    monthly_installment = serializers.DecimalField(max_digits=12, decimal_places=2)


class LoanCreateSerializer(serializers.Serializer):
    customer_id = serializers.IntegerField()
    loan_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    interest_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    tenure = serializers.IntegerField()


class LoanCreateResponseSerializer(serializers.Serializer):
    loan_id = serializers.IntegerField(allow_null=True)
    customer_id = serializers.IntegerField()
    loan_approved = serializers.BooleanField()
    message = serializers.CharField()
    monthly_installment = serializers.DecimalField(max_digits=12, decimal_places=2)


class CustomerDetailSerializer(serializers.Serializer):
    id = serializers.IntegerField(source='customer_id')
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    phone_number = serializers.IntegerField()
    age = serializers.IntegerField()


class LoanDetailSerializer(serializers.Serializer):
    loan_id = serializers.IntegerField()
    customer = CustomerDetailSerializer()
    loan_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    interest_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    monthly_installment = serializers.DecimalField(max_digits=12, decimal_places=2, source='monthly_repayment')
    tenure = serializers.IntegerField()


class CustomerLoanSerializer(serializers.Serializer):
    loan_id = serializers.IntegerField()
    loan_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    interest_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    monthly_installment = serializers.DecimalField(max_digits=12, decimal_places=2, source='monthly_repayment')
    repayments_left = serializers.IntegerField()
