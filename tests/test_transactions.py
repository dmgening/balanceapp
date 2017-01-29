import datetime

from .factories import Account, Transaction


def test_update_balance_hook(transactional_db):
    today = datetime.date.today()

    account = Account.create()
    transaction = Transaction.create(account=account,
                                     date=today)

    # Check that we create balance for today
    created_balances = account.balance_set.all()
    assert len(created_balances) == 1
    assert created_balances[0].date == today
    assert created_balances[0].amount == transaction.amount

    yesterday = today - datetime.timedelta(days=1)

    second_transaction = Transaction.create(account=account,
                                            date=yesterday)

    created_balances = account.balance_set.all()
    assert len(created_balances) == 2
    assert created_balances[0].date == yesterday
    assert created_balances[0].amount == second_transaction.amount
    assert created_balances[1].amount == (transaction.amount +
                                          second_transaction.amount)
