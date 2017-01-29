import datetime
import pytest

from .factories import AccountFactory, TransactionFactory


@pytest.fixture
def account_with_history(request, transactional_db):
    account = AccountFactory.create()
    for date_offset in range(0, 5):
        TransactionFactory.create_batch(
            5, account=account,
            date=datetime.date.today() - datetime.timedelta(days=date_offset)
        )
    yield account
