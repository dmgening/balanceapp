import factory
import factory.fuzzy

from transactions import models


class Account(factory.django.DjangoModelFactory):
    title = factory.Faker('company')

    class Meta:
        model = models.Account


class Transaction(factory.django.DjangoModelFactory):
    description = factory.Faker('company')
    amount = factory.fuzzy.FuzzyInteger(-1E4, 1E4)

    class Meta:
        model = models.Transaction
