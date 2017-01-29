import factory
import factory.fuzzy

from balanceapp.transactions.models import Account, Transaction


class AccountFactory(factory.django.DjangoModelFactory):
    title = factory.Faker('company')

    class Meta:
        model = Account


class TransactionFactory(factory.django.DjangoModelFactory):
    description = factory.Faker('company')
    amount = factory.fuzzy.FuzzyInteger(-1E4, 1E4)

    class Meta:
        model = Transaction
