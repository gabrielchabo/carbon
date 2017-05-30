from django.db import models

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
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default=MALE,)
    marital_status = models.CharField(max_length=10, choices=MARITAL_CHOICES, default=SINGLE,)
    #gender = models.ForeignKey(Gender)

    def __str__(self):
        return self.first_name + ' ' + self.last_name.upper()
