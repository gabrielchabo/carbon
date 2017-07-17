from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver
import datetime
import decimal
import calendar

class Constants:

    EXCHANGE_RATE = 1500
    INSUFFICIENT_FUNDS = "Insufficient funds!"
    USD = 'USD'
    LBP = 'LBP'
    CURRENCY_CHOICES = (
        (USD, '$'),
        (LBP, 'LL'),
    )
    
    JANUARY = 'JAN'
    FEBRUARY = 'FEB'
    MARCH = 'MAR'
    APRIL = 'APR'
    MAY = 'MAY'
    JUNE = 'JUN'
    JULY = 'JUL'
    AUGUST = 'AUG'
    SEPTEMBER = 'SEP'
    OCTOBER = 'OCT'
    NOVEMBER = 'NOV'
    DECEMBER = 'DEC'
    
    MONTH_CHOICES = (
        (JANUARY, 'January'),
        (FEBRUARY, 'February'),
        (MARCH, 'March'),
        (APRIL, 'April'),
        (MAY, 'May'),
        (JUNE, 'June'),
        (JULY, 'July'),
        (AUGUST, 'August'),
        (SEPTEMBER, 'September'),
        (OCTOBER, 'October'),
        (NOVEMBER, 'November'),
        (DECEMBER, 'December'),
    )
    
    YEAR_CHOICES = []
    for r in range(2016, (datetime.datetime.now().year+1)):
        YEAR_CHOICES.append((r, r))
    
    DEBIT = "D"
    CREDIT = "C"
    
    TRANSACTION_CHOICES = (
        (DEBIT, 'Debit'),
        (CREDIT, 'Credit'),
    )

def validate_phone(value):
    if not (value.isdigit() and len(value) == 8):
        raise ValidationError(
            _('%(value)s is not an valid phone number'),
            params={'value': value},
        )

class CurrencyUtils(object):
    @staticmethod
    def to_usd(amount, currency):
        actual_amount = amount / (Constants.EXCHANGE_RATE if currency == Constants.LBP else 1)
        return actual_amount

    @staticmethod
    def normalize_transaction_amount(amount, currency, transaction_type):
        """
        Normalizes the amount to USD using the EXCHANGE_RATE
        """
        actual_amount = CurrencyUtils.to_usd(amount, currency)
        actual_amount = actual_amount * (-1 if transaction_type == Constants.DEBIT else 1)
        return actual_amount

class Team(models.Model):
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=200, blank=True, null=True)
    representative = models.ForeignKey('Person', limit_choices_to={'squad_member': True}, related_name='representative')

    def __str__(self):
        return self.name

class Person(models.Model):
    MALE = 'M'
    FEMALE = 'F'
    SINGLE = 'S'
    ENGAGED = 'E'
    MARRIED = 'D'
    WIDOWED = 'W'
    COMPLICATE = 'C'

    GENDER_CHOICES = (
        (MALE, 'Male'),
        (FEMALE, 'Female'),
    )
    MARITAL_CHOICES = (
        (SINGLE, 'Single'),
        (ENGAGED, 'Engaged'),
        (MARRIED, 'Married'),
        (WIDOWED, 'Windowed'),
        (COMPLICATE, 'It\'s Complicated'),
    )
    team = models.ForeignKey(Team, blank=True, null=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    birth_date = models.DateField()
    email = models.EmailField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default=MALE,)
    marital_status = models.CharField(max_length=10, choices=MARITAL_CHOICES, default=SINGLE,)
    squad_member = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    food_allergies = models.CharField(max_length=200, blank=True, null=True)
    birth_date.alphabetic_filter = True
    
    @staticmethod
    def autocomplete_search_fields():
        return ("first_name__icontains", "last_name__icontains",)
    
    @property
    def month(self):
        """
        Returns the month of birth of a person
        """
        year, month, day = self.birth_date.split('-')
        return calendar.month_name[int(month)]

    def __str__(self):
        return self.first_name + ' ' + self.last_name.upper()

    def __unicode__(self):
        return self.first_name + ' ' + self.last_name.upper()

class Membership(models.Model):
    person = models.ForeignKey(Person)
    year = models.IntegerField(('year'), choices=Constants.YEAR_CHOICES, default=datetime.datetime.now().year)
    month = models.CharField(max_length=20, choices=Constants.MONTH_CHOICES, default=Constants.JANUARY,)
    collected_by = models.ForeignKey('Person', limit_choices_to={'squad_member': True}, related_name='collected_by')
    amount = models.DecimalField(default=10, max_digits=15, decimal_places=2)
    currency = models.CharField(max_length=3, choices=Constants.CURRENCY_CHOICES, default=Constants.USD) # editable = False
    notes = models.TextField(max_length=400, blank=True)


    def __str__(self):
        return "Membership of " + str(self.person) + " for " + str(self.month) + " " + str(self.year)

    def save(self, *args, **kwargs):
        #if we're editing an existing membership, don't add a transaction
        if self.pk is not None:
            super(Membership, self).save(*args, **kwargs)
            return
        #save a record in Transactions
        transaction = Transaction()
        transaction.amount = self.amount
        transaction.transaction_type = Constants.CREDIT
        transaction.currency = self.currency
        transaction.transaction_date = datetime.datetime.now()
        transaction.total = transaction.total_amount
        membership_note = "Membership of " + str(self.person) + " for " + str(self.month) + " " + str(self.year)
        transaction.note = membership_note
        transaction.description = "MEMBERSHIP"
        super(Membership, self).save(*args, **kwargs)
        transaction.membership = self
        transaction.save()

class Payment(models.Model):
    event = models.ForeignKey('Event')
    amount = models.DecimalField(default=10, max_digits=15, decimal_places=2)
    payment_date = models.DateTimeField(auto_now=True)
    currency = models.CharField(max_length=3, choices=Constants.CURRENCY_CHOICES, default=Constants.USD,)
    invoice = models.FileField(blank=True, upload_to='invoices')
    notes = models.TextField(max_length=400, blank=True)

    def __str__(self):
        return "Payment for " + str(self.event)

    def save(self, *args, **kwargs):
        """
        save a record in Transactions
        """
        transaction = Transaction()
        transaction.event = self.event
        transaction.amount = self.amount
        transaction.transaction_type = Constants.DEBIT
        transaction.currency = self.currency
        transaction.transaction_date = datetime.datetime.now()
        transaction.total = transaction.total_amount
        transaction.note = self.notes
        transaction.description = "PAYMENT"
        transaction.save()

        #transaction = Transaction.objects.create_transaction(event="", transaction_type=TRANSACTION_CHOICES.DEBIT, amount=self.amount, currency=self.currency, transaction_date=datetime.now, total="", note=note)
        super(Payment, self).save(*args, **kwargs)

class PlaceClassification(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name

class Place(models.Model):
    RATINGS_CHOICES = (
        (1, 'Unless Necessary'),
        (2, 'Good Enough'),
        (3, 'Average'),
        (4, 'Great'),
        (5, 'Amazing'),
    )
    classification = models.ForeignKey(PlaceClassification)
    name = models.CharField(max_length=30)
    address = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=8, validators=[validate_phone], blank=True)
    description = models.CharField(max_length=200, blank=True)
    rating = models.IntegerField(default=3, choices=RATINGS_CHOICES)
    comment = models.TextField(max_length=400, blank=True)

    def __str__(self):
        return self.name

class EventType(models.Model):
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.name

class Event(models.Model):

    @property
    def __get_total_cost(self):
        #transactions = Transaction.objects.filter(membership=self)
        transactions = Transaction.objects.filter(event=self)
        total_cost = 0
        for transaction in transactions:
            #since all payments are debits, the amount will be negative so we have to multiply by -1
            total_cost += -1 * CurrencyUtils.normalize_transaction_amount(transaction.amount, transaction.currency, transaction.transaction_type)
        return total_cost

    event_type = models.ForeignKey(EventType)
    order_from = models.ManyToManyField(Place, related_name='places')
    organizer = models.ForeignKey(Person, limit_choices_to={'squad_member': True}, related_name='event_organizer')
    squad = models.ManyToManyField(Person, limit_choices_to={'squad_member': True}, related_name='squad')
    targets = models.ManyToManyField(Person, related_name='targets')
    name = models.CharField(max_length=30)
    event_date = models.DateField()
    location = models.CharField(max_length=30, blank=True)
    gift_card = models.BooleanField(default=False)
    notes = models.TextField(max_length=400, null=True, blank=True)
    total = __get_total_cost

    def __str__(self):
        return self.name
    
    @staticmethod
    def autocomplete_search_fields():
        return ("name__icontains",)

class Transaction(models.Model):

    @property
    def transactions(self):
        """
        Return the queryset of transactions belonging to this system
        """
        return Transaction.objects.all()

    @property
    def total_amount(self):
        """
        Calculate the total amount of money stored in the accouting suystem
        as an algebraic sum of the balances of all transactions
        """
        total_amount = 0
        for transaction in self.transactions:
            total_amount += CurrencyUtils.normalize_transaction_amount(transaction.amount, transaction.currency, transaction.transaction_type)
        return total_amount

    def _total_amount_by_event(self, event):
        total_amount = 0
        for transaction in self.transactions:
            if transaction.event == event:
                total_amount += transaction.amount
        return total_amount

    @property
    def dollar_total(self):
        return "$%s" % self.total if self.total else ""

    def save(self, *args, **kwargs):
        #disable edit an existing record
        if self.pk is not None:
            raise ValidationError("Editing an existing transaction is not allowed")

        #if self.total is None:
        self.total = self.total_amount
        if self.transaction_type == Constants.DEBIT and self.total == 0:
            raise ValidationError(Constants.INSUFFICIENT_FUNDS)
        actual_amount = CurrencyUtils.normalize_transaction_amount(self.amount, self.currency, self.transaction_type)
        if decimal.Decimal(actual_amount) + self.total < 0:
            raise ValidationError(Constants.INSUFFICIENT_FUNDS)
        self.total = self.total_amount + decimal.Decimal(actual_amount)
        super(Transaction, self).save(*args, **kwargs)

    membership = models.ForeignKey(Membership, blank=True, null=True)
    event = models.ForeignKey(Event, blank=True, null=True)
    transaction_type = models.CharField(max_length=1, choices=Constants.TRANSACTION_CHOICES, default=Constants.DEBIT,)
    amount = models.DecimalField(default=10, max_digits=15, decimal_places=2)
    currency = models.CharField(max_length=3, choices=Constants.CURRENCY_CHOICES, default=Constants.USD,)
    transaction_date = models.DateTimeField(auto_now=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=10, blank=True)
    note = models.TextField(max_length=400, blank=True)

    def __str__(self):
        return "Transaction-" + str(self.id)

@receiver(pre_delete, sender=Transaction)
def _mymodel_delete(sender, instance, **kwargs):
    """
    Prevent deleting a record if it's not the final record
    """
    #latest_transaction = Transaction.objects.filter(event=instance.event).last()
    latest_transaction = Transaction.objects.all().last()
    if instance.transaction_date != latest_transaction.transaction_date:
        raise ValidationError('Can only delete the latest record for a given activity')#cancel the deletion

#Relationship