import datetime
import pytest

from .factories import Account, Transaction


@pytest.fixture
def account_with_history(request, transactional_db):
    account = Account.create()
    for date_offset in range(0, 5):
        Transaction.create_batch(
            5, account=account,
            date=datetime.date.today() - datetime.timedelta(days=date_offset)
        )
    yield account
