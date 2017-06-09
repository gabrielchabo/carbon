from django.test import TestCase
from django.core.exceptions import ValidationError
import datetime

from .models import CurrencyUtils, Transaction, Person, EventType, Event, Membership, Payment, USD, LBP, CREDIT, DEBIT

THRESHOLD = 5000000

class TestUtils(object):
    @staticmethod
    def get_person():
        person = Person()
        person.first_name = "mock"
        person.last_name = "momo"
        person.birth_date = datetime.datetime.today()
        person.email = "mock@momo.com"
        person.gender = 'M'
        person.marital_status = 'S'
        person.squad_member = True
        person.save()
        return person

    @staticmethod
    def get_event_type(name):
        event_type = EventType()
        event_type.name = name
        event_type.save()
        return event_type

    @staticmethod
    def get_payment(event, amount, currency, notes):
        payment = Payment()
        payment.event = event
        payment.event = event
        payment.amount = amount
        payment.currency = currency
        payment.payment_date = datetime.datetime.now()
        payment.notes = notes
        return payment

    @staticmethod
    def get_membership(month, year, amount, currency):
        TestUtils.get_person()
        membership = Membership.objects.create(person_id=1, month=month, year=year, collected_by_id=1, amount=amount, currency=currency, notes="NOTES")
        return membership

    @staticmethod
    def get_transaction(amount, currency, type):
        transaction = Transaction()
        transaction.amount = amount
        transaction.currency = currency
        transaction.transaction_type = type
        transaction.transaction_date = datetime.datetime.now()
        transaction.total = transaction.total_amount
        return transaction

class CurrencyUtilsTest(TestCase):
    # def test_usd_from_usd_conversion(self):
    #     for value in range(0, THRESHOLD):
    #         amount = CurrencyUtils.to_usd(value, USD)
    #         self.assertEqual(amount, amount/1)

    def test_usd_from_lbp_conversion(self):
        amount = CurrencyUtils.to_usd(1500, LBP)
        self.assertEqual(amount, 1)

        amount = CurrencyUtils.to_usd(5000, LBP)
        self.assertEqual(amount, 3.3333333333333335)

        amount = CurrencyUtils.to_usd(10000, LBP)
        self.assertEqual(amount, 6.666666666666667)

        amount = CurrencyUtils.to_usd(1500, LBP)
        self.assertEqual(amount, 1)

        amount = CurrencyUtils.to_usd(15000, LBP)
        self.assertEqual(amount, 10)

        amount = CurrencyUtils.to_usd(30000, LBP)
        self.assertEqual(amount, 20)

        amount = CurrencyUtils.to_usd(45000, LBP)
        self.assertEqual(amount, 30)

        amount = CurrencyUtils.to_usd(75000, LBP)
        self.assertEqual(amount, 50)

        amount = CurrencyUtils.to_usd(150000, LBP)
        self.assertEqual(amount, 100)

    def test_normalize_transaction_amount(self):
        amount = CurrencyUtils.normalize_transaction_amount(1, USD, CREDIT)
        self.assertEqual(amount, 1)

        amount = CurrencyUtils.normalize_transaction_amount(1, USD, DEBIT)
        self.assertEqual(amount, -1)

        amount = CurrencyUtils.normalize_transaction_amount(100, USD, CREDIT)
        self.assertEqual(amount, 100)

        amount = CurrencyUtils.normalize_transaction_amount(100, USD, DEBIT)
        self.assertEqual(amount, -100)

        amount = CurrencyUtils.normalize_transaction_amount(1500, LBP, CREDIT)
        self.assertEqual(amount, 1)

        amount = CurrencyUtils.normalize_transaction_amount(1500, LBP, DEBIT)
        self.assertEqual(amount, -1)

        amount = CurrencyUtils.normalize_transaction_amount(15000, LBP, CREDIT)
        self.assertEqual(amount, 10)

        amount = CurrencyUtils.normalize_transaction_amount(15000, LBP, DEBIT)
        self.assertEqual(amount, -10)

        amount = CurrencyUtils.normalize_transaction_amount(150000, LBP, CREDIT)
        self.assertEqual(amount, 100)

        amount = CurrencyUtils.normalize_transaction_amount(150000, LBP, DEBIT)
        self.assertEqual(amount, -100)

class TransactionModelTest(TestCase):
    def test_string_representation(self):
        transaction = TestUtils.get_transaction(1, USD, CREDIT)
        transaction.save()
        self.assertEqual(str(transaction), "Transaction-1")

    def test_cannot_edit_existing(self):
        transaction = TestUtils.get_transaction(1, USD, CREDIT)
        transaction.note = "TEST"
        transaction.save()
        retrieved_transaction = Transaction.objects.last()
        self.assertEqual(retrieved_transaction.amount, 1)
        self.assertEqual(retrieved_transaction.currency, USD)
        self.assertEqual(retrieved_transaction.transaction_type, CREDIT)
        self.assertEqual(retrieved_transaction.note, "TEST")
        with self.assertRaises(ValidationError):
            retrieved_transaction.save()

    def test_cannot_overdraw(self):
        transaction1 = TestUtils.get_transaction(1, USD, CREDIT)
        transaction1.save()
        self.assertEqual(transaction1.amount, 1.00)
        self.assertEqual(transaction1.total_amount, 1.00)

        transaction2 = TestUtils.get_transaction(2, USD, DEBIT)
        with self.assertRaises(ValidationError):
            transaction2.save()

    def test_currency_conversion_credit(self):
        transaction_usd = TestUtils.get_transaction(1, USD, CREDIT)
        transaction_usd.save()
        transaction_lbp = TestUtils.get_transaction(1500, LBP, CREDIT)
        self.assertEqual(transaction_lbp.amount, 1500)
        self.assertEqual(transaction_lbp.total, 1)
        transaction_lbp.save()
        self.assertEqual(transaction_lbp.amount, 1500)
        self.assertEqual(transaction_lbp.currency, LBP)
        self.assertEqual(transaction_lbp.total_amount, 2)

    def test_currency_conversion_debit(self):
        transaction_usd = TestUtils.get_transaction(1, USD, CREDIT)
        transaction_usd.save()
        self.assertEqual(transaction_usd.amount, 1)
        self.assertEqual(transaction_usd.total, 1)
        transaction_lbp = TestUtils.get_transaction(1500, LBP, DEBIT)
        self.assertEqual(transaction_lbp.amount, 1500)
        self.assertEqual(transaction_lbp.total, 1)
        transaction_lbp.save()
        self.assertEqual(transaction_lbp.amount, 1500)
        self.assertEqual(transaction_lbp.currency, LBP)
        self.assertEqual(transaction_lbp.total, 0)
        #Just to make sure that the record we're testing is the last one
        retrieved_transaction = Transaction.objects.last()
        self.assertEqual(retrieved_transaction.total, 0)

    def test_transaction_calculations(self):
        tr1_usd_credit = TestUtils.get_transaction(1, USD, CREDIT)
        tr1_usd_credit.save()
        self.assertEqual(tr1_usd_credit.amount, 1)
        self.assertEqual(tr1_usd_credit.total, 1)

        tr100_usd_credit = TestUtils.get_transaction(100, USD, CREDIT)
        tr100_usd_credit.save()
        self.assertEqual(tr100_usd_credit.total, 101)
        self.assertEqual(Transaction.objects.last().total, 101)

        tr1500_lbp_credit = TestUtils.get_transaction(1500, LBP, CREDIT)
        tr1500_lbp_credit.save()
        self.assertEqual(tr1500_lbp_credit.total, 102)
        self.assertEqual(Transaction.objects.last().total, 102)

        tr15000_lbp_credit = TestUtils.get_transaction(15000, LBP, CREDIT)
        tr15000_lbp_credit.save()
        self.assertEqual(tr15000_lbp_credit.total, 112)
        self.assertEqual(Transaction.objects.last().total, 112)

        tr1_usd_debit = TestUtils.get_transaction(1, USD, DEBIT)
        tr1_usd_debit.save()
        self.assertEqual(tr1_usd_debit.total, 111)
        self.assertEqual(Transaction.objects.last().total, 111)

        retrieved_transaction = Transaction.objects.last()
        self.assertEqual(retrieved_transaction.total, 111)#Making sure that the total is accurate
        tr150000_lbp_debit = TestUtils.get_transaction(150000, LBP, DEBIT)
        tr150000_lbp_debit.save()
        self.assertEqual(tr150000_lbp_debit.amount, 150000)
        self.assertEqual(tr150000_lbp_debit.currency, LBP)
        self.assertEqual(tr150000_lbp_debit.transaction_type, DEBIT)
        self.assertEqual(tr150000_lbp_debit.total, 11)

        tr10_usd_debit = TestUtils.get_transaction(10, USD, DEBIT)
        tr10_usd_debit.save()
        self.assertEqual(tr10_usd_debit.total, 1)

        tr3000_lbp_debit = TestUtils.get_transaction(3000, LBP, DEBIT)
        with self.assertRaises(ValidationError):
            tr3000_lbp_debit.save()

        tr2_usd_debit = TestUtils.get_transaction(2, USD, DEBIT)
        with self.assertRaises(ValidationError):
            tr2_usd_debit.save()

class MembershipModelTest(TestCase):
    def test_membership_adds_trans_usd(self):
        self.assertEqual(Transaction.objects.count(), 0)
        membership = TestUtils.get_membership('JAN', 2017, 10, USD)
        self.assertEqual(Transaction.objects.count(), 1)
        self.assertEqual(membership.amount, 10)
        self.assertEqual(Transaction.objects.count(), 1)
        last_transaction = Transaction.objects.last()
        self.assertEqual(last_transaction.amount, 10)
        self.assertEqual(last_transaction.currency, USD)
        self.assertEqual(last_transaction.total, 10)

    def test_membership_adds_trans_lbp(self):
        self.assertEqual(Transaction.objects.count(), 0)
        membership = TestUtils.get_membership('JAN', 2017, 1500, LBP)
        self.assertEqual(Transaction.objects.count(), 1)
        self.assertEqual(membership.amount, 1500)
        self.assertEqual(Transaction.objects.count(), 1)
        last_transaction = Transaction.objects.last()
        self.assertEqual(last_transaction.amount, 1500)
        self.assertEqual(last_transaction.currency, LBP)
        self.assertEqual(last_transaction.total, 1)

    def test_edit_membership_adds_no_trans(self):
        self.assertEqual(Transaction.objects.count(), 0)
        membership = TestUtils.get_membership('JAN', 2017, 10, USD)
        self.assertEqual(Membership.objects.count(), 1)
        self.assertEqual(Transaction.objects.count(), 1)
        self.assertEqual(membership.amount, 10)
        self.assertEqual(Transaction.objects.count(), 1)
        last_transaction = Transaction.objects.last()
        self.assertEqual(last_transaction.amount, 10)
        self.assertEqual(last_transaction.currency, USD)
        self.assertEqual(last_transaction.total, 10)
        """
        editing an existing membership should not affect insert a new transaction
        instead it should edit the existing transaction
        """
        membership.month = 'OCT'
        membership.save()
        self.assertEqual(Transaction.objects.count(), 1)
        last_membership = Membership.objects.last()
        self.assertEqual(last_membership.month, 'OCT')
        self.assertEqual(Membership.objects.all().count(), 1)


class EventModelTest(TestCase):
    def test_event_total_cost(self):
        #create a person
        organizer = TestUtils.get_person()

        #Add a transaction so that we can withdraw
        transaction = TestUtils.get_transaction(5000, USD, 2)
        transaction.save()

        #create the event
        event1 = Event()
        event_name = "EventTypeTest"
        event_type = TestUtils.get_event_type(event_name)
        self.assertEqual(event_type.name, event_name)
        event1.event_type = event_type
        event1.event_date = datetime.datetime.now()
        event1.organizer = organizer
        event1.save()
        self.assertEqual(event1.event_type.name, event_name)

        #create usd payment associated to the event
        payment = TestUtils.get_payment(event1, 20, USD, "NOTES")
        payment.save()

        #make sure we debited the exact amount
        transactions = Transaction.objects.all()
        self.assertEqual(transactions.count(), 2)
        last_transaction = Transaction.objects.last()
        self.assertEqual(last_transaction.total, 5000 - 20)

        #create lbp payment associated to the event
        payment = TestUtils.get_payment(event1, 300000, LBP, "NOTES")
        payment.save()

        #make sure we debited the exact amount
        transactions = Transaction.objects.all()
        self.assertEqual(transactions.count(), 3)
        last_transaction = Transaction.objects.last()
        self.assertEqual(last_transaction.total, 5000 - 20 - 300000/1500)

        #assert total amount of money spent on an event
        self.assertEqual(event1.total, 20 + 300000/1500)
