from datetime import datetime
from decimal import Decimal
from .models import Loan, Customer


def calculate_credit_score(customer_id):
    try:
        customer = Customer.objects.get(customer_id=customer_id)
    except Customer.DoesNotExist:
        return 0

    loans = Loan.objects.filter(customer=customer)
    
    if not loans.exists():
        return 100  
    current_loans = loans.filter(is_active=True)
    total_current_debt = sum(loan.loan_amount for loan in current_loans)
    
    if total_current_debt > customer.approved_limit:
        return 0
    
    score = 0
    
 
    total_emis = sum(loan.tenure for loan in loans)
    emis_paid_on_time = sum(loan.emis_paid_on_time for loan in loans)
    
    if total_emis > 0:
        payment_ratio = emis_paid_on_time / total_emis
        score += payment_ratio * 40
    
    num_loans = loans.count()
    if num_loans == 0:
        score += 20
    elif num_loans <= 3:
        score += 20 - (num_loans * 5)
    else:
        score += 5  
    
    
    current_year = datetime.now().year
    current_year_loans = loans.filter(start_date__year=current_year)
    
    if current_year_loans.count() == 0:
        score += 20
    elif current_year_loans.count() <= 2:
        score += 15
    else:
        score += 5
    
    
    if customer.approved_limit > 0:
        utilization = float(total_current_debt / customer.approved_limit)
        if utilization < 0.3:
            score += 20
        elif utilization < 0.5:
            score += 15
        elif utilization < 0.7:
            score += 10
        else:
            score += 5
    
    return min(100, max(0, int(score)))


def calculate_monthly_installment(loan_amount, interest_rate, tenure):
    P = float(loan_amount)
    annual_rate = float(interest_rate)
    R = annual_rate / (12 * 100) 
    N = tenure
    
    if R == 0:
        return Decimal(str(P / N))
    
    emi = P * R * ((1 + R) ** N) / (((1 + R) ** N) - 1)
    return Decimal(str(round(emi, 2)))


def check_loan_eligibility(customer_id, loan_amount, interest_rate, tenure):
    try:
        customer = Customer.objects.get(customer_id=customer_id)
    except Customer.DoesNotExist:
        return {
            'approval': False,
            'message': 'Customer not found',
            'corrected_interest_rate': interest_rate,
            'monthly_installment': 0
        }
    

    credit_score = calculate_credit_score(customer_id)
    
    approval = False
    corrected_interest_rate = interest_rate
    message = ""
    
    if credit_score > 50:
        approval = True
        corrected_interest_rate = interest_rate
    elif 30 < credit_score <= 50:
        if interest_rate >= 12:
            approval = True
            corrected_interest_rate = interest_rate
        else:
            approval = True
            corrected_interest_rate = Decimal('12.0')
    elif 10 < credit_score <= 30:
        if interest_rate >= 16:
            approval = True
            corrected_interest_rate = interest_rate
        else:
            approval = True
            corrected_interest_rate = Decimal('16.0')
    else:  # credit_score <= 10
        approval = False
        message = "Credit score too low. Loan cannot be approved."
    
    if approval:
        current_loans = Loan.objects.filter(customer=customer, is_active=True)
        total_current_emis = sum(loan.monthly_repayment for loan in current_loans)
        
        new_emi = calculate_monthly_installment(loan_amount, corrected_interest_rate, tenure)
        
        if (total_current_emis + new_emi) > (customer.monthly_salary * Decimal('0.5')):
            approval = False
            message = "Sum of all EMIs exceeds 50% of monthly salary. Loan cannot be approved."
    
    monthly_installment = calculate_monthly_installment(loan_amount, corrected_interest_rate, tenure) if approval else 0
    
    return {
        'approval': approval,
        'message': message if not approval else "Loan can be approved",
        'corrected_interest_rate': corrected_interest_rate,
        'monthly_installment': monthly_installment,
        'credit_score': credit_score
    }
