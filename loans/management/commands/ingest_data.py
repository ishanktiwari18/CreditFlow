from django.core.management.base import BaseCommand
from loans.tasks import ingest_customer_data, ingest_loan_data
import os


class Command(BaseCommand):
    help = 'Ingest customer and loan data from Excel files'

    def add_arguments(self, parser):
        parser.add_argument(
            '--customer-file',
            type=str,
            help='Path to customer data Excel file',
            default='/app/data/customer_data.xlsx'
        )
        parser.add_argument(
            '--loan-file',
            type=str,
            help='Path to loan data Excel file',
            default='/app/data/loan_data.xlsx'
        )

    def handle(self, *args, **options):
        customer_file = options['customer_file']
        loan_file = options['loan_file']

        if not os.path.exists(customer_file):
            self.stdout.write(self.style.ERROR(f'Customer file not found: {customer_file}'))
            return

        if not os.path.exists(loan_file):
            self.stdout.write(self.style.ERROR(f'Loan file not found: {loan_file}'))
            return

        self.stdout.write(self.style.SUCCESS('Starting data ingestion...'))

        self.stdout.write('Ingesting customer data...')
        customer_result = ingest_customer_data(customer_file)
        self.stdout.write(self.style.SUCCESS(customer_result))

        self.stdout.write('Ingesting loan data...')
        loan_result = ingest_loan_data(loan_file)
        self.stdout.write(self.style.SUCCESS(loan_result))

        self.stdout.write(self.style.SUCCESS('Data ingestion completed!'))
