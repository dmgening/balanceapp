import datetime

import pytest

from .factories import AccountFactory, TransactionFactory


@pytest.mark.usefixtures('transactional_db')
def test_update_balance_hook():
    today = datetime.date.today()

    account = AccountFactory.create()
    today_transaction = TransactionFactory.create(account=account,
                                                  date=today)

    # Check that we create balance for today
    today_balance = account.balance_set.get(date=today)

    assert len(account.balance_set.all()) == 1
    assert today_balance.amount == today_transaction.amount

    yesterday = today - datetime.timedelta(days=1)

    yesterday_transaction = TransactionFactory.create(account=account,
                                                      date=yesterday)

    today_balance.refresh_from_db()
    yesterday_balance = account.balance_set.get(date=yesterday)

    assert len(account.balance_set.all()) == 2
    assert yesterday_balance.amount == yesterday_transaction.amount
    assert today_balance.amount == (today_transaction.amount +
                                    yesterday_transaction.amount)
