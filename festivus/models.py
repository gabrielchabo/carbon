from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
import datetime

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

def validatePhone(value):
    if not (value.isdigit() and len(value) == 8):
        raise ValidationError(
            _('%(value)s is not an valid phone number'),
            params={'value': value},
        )

class Person(models.Model):
    MALE = "M"
    FEMALE = "F"
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
        (COMPLICATE, 'Complicated'),
    )
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    birth_date = models.DateField()
    email = models.EmailField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default=MALE,)
    marital_status = models.CharField(max_length=10, choices=MARITAL_CHOICES, default=SINGLE,)

    def __str__(self):
        return self.first_name + ' ' + self.last_name.upper()

class Payment(models.Model):
    person = models.ForeignKey(Person)
    year = models.IntegerField(('year'), choices=YEAR_CHOICES, default=datetime.datetime.now().year)
    month = models.CharField(max_length=20, choices=MONTH_CHOICES, default=JANUARY,)
    amount = models.DecimalField(default=10, max_digits=6, decimal_places=2)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default=USD,)
    enrolled = models.BooleanField(default=True)
    comment = models.TextField(max_length=400, blank=True)

    def __str__(self):
        return "Payment-" + str(self.id)

class PlaceCategory(models.Model):
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
    category = models.ForeignKey(PlaceCategory)
    name = models.CharField(max_length=30)
    address = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=8, validators=[validatePhone], blank=True)
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
    event_type = models.ForeignKey(EventType)
    organizer = models.ForeignKey(Person, related_name='event_organizer')
    victim = models.ForeignKey(Person)
    name = models.CharField(max_length=30)
    event_date = models.DateField()
    location = models.CharField(max_length=30, blank=True)
    budget = models.IntegerField(default=0)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default=USD,)
    gift_card = models.BooleanField(default=False)
    comment = models.TextField(max_length=400, blank=True)

    def __str__(self):
        return self.name

class Transaction(models.Model):
    DEBIT = "D"
    CREDIT = "C"

    TRANSACTION_CHOICES = (
        (DEBIT, 'Debit'),
        (CREDIT, 'Credit'),
    )
    event = models.ForeignKey(Event)
    transaction_type = models.CharField(max_length=1, choices=TRANSACTION_CHOICES, default=DEBIT,)
    amount = models.DecimalField(default=10, max_digits=6, decimal_places=2)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default=USD,)
    transaction_date = models.DateField(default=datetime.date.today)
    note = models.TextField(max_length=400, blank=True)
    #Add Transaction details like "Solde"

    def __str__(self):
        return "Transaction-" + str(self.id)

#Relationship