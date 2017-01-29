from __future__ import unicode_literals

import architect

from django.db import models
from django.dispatch import receiver


class Account(models.Model):
    """ Account holding transactions
    """

    title = models.CharField(max_length=200)

    @classmethod
    def serializer_hook(cls, obj, data):
        """ Pluggable hook to extend generic django serialization.
            Adds balance to field list
        """
        current_balance = obj.balance_set.order_by('date').last()
        if not current_balance:
            data['fields']['balance'] = 0
        else:
            data['fields']['balance'] = current_balance.amount
        return data

@architect.install('partition', type='range', subtype='date',
                   constraint='day', column='date')
class Transaction(models.Model):
    """ Single transaction
    """

    description = models.CharField(max_length=140)
    amount = models.IntegerField()
    date = models.DateField()

    account = models.ForeignKey(Account)


@architect.install('partition', type='range', subtype='date',
                   constraint='year', column='date')
class Balance(models.Model):
    """ Account final balance for date
    """

    date = models.DateField()
    amount = models.IntegerField()

    account = models.ForeignKey(Account)


@receiver(models.signals.pre_save, sender=Transaction)
def update_balance(sender, instance, **kwargs):
    """ Update account balance for all dependent dates
    """
    amount_change = instance.amount
    try:
        amount_change -= Transaction.objects.get(id=instance.id).amount
    except Transaction.DoesNotExist:
        pass

    balance_qs = Balance.objects

    # Check that we have balance record for transaction date or create it
    if not balance_qs.filter(account=instance.account,
                             date=instance.date).exists():
        last_known_balance = balance_qs.filter(account=instance.account,
                                               date__lte=instance.date).last()
        if last_known_balance is None:
            last_known_balance_amount = 0
        else:
            last_known_balance_amount = last_known_balance.amount

        Balance(amount=last_known_balance_amount, date=instance.date,
                account=instance.account).save()

    # FIXME: Would be much faster if we use SQL level functions
    for balance in balance_qs.filter(account=instance.account,
                                     date__gte=instance.date).all():
        balance.amount += amount_change
        # FIXME: Should not be commited to db independently of transaction
        balance.save()
