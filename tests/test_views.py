import json
import datetime

import pytest

from django.urls import reverse

from balanceapp.transactions.models import Account, Transaction
from .factories import AccountFactory, TransactionFactory


@pytest.mark.usefixtures('transactional_db')
def test_create_account(client):
    account_title = 'Magic Title'

    result = client.post(reverse('account_view'), json.dumps({
        'title': account_title
    }), content_type='application/json')

    assert result.status_code == 201
    body = result.json()

    assert len(body) == 1
    account = body[0]

    assert account.get('pk') is not None
    assert account.get('fields').get('title') == account_title
    assert account.get('fields').get('balance') == 0

    instance = Account.objects.get(id=account.get('pk'))
    assert instance.title == account_title


@pytest.mark.usefixtures('transactional_db')
def test_retrieve_account(client):
    account = AccountFactory.create()
    result = client.get(reverse('account_view', args=(account.id, )))

    assert result.status_code == 200
    body = result.json()

    assert len(body) == 1
    resp_account = body[0]

    assert resp_account.get('pk') is not None
    assert resp_account.get('fields').get('title') == account.title
    assert resp_account.get('fields').get('balance') == 0


@pytest.mark.usefixtures('transactional_db')
def test_create_transaction(client):
    today = datetime.date.today()
    account = AccountFactory.create()

    stub = TransactionFactory.stub(account=account.id,
                                   date=today.isoformat())
    result = client.post(reverse('transaction_view'),
                         json.dumps(vars(stub)),
                         content_type='application/json')

    assert result.status_code == 201
    response_body = result.json()

    assert len(response_body) == 1
    transaction = response_body[0]

    assert transaction.get('pk') is not None
    assert transaction.get('fields').get('description') == stub.description
    assert transaction.get('fields').get('amount') == stub.amount
    transaction_date = datetime.datetime.strptime(
        transaction.get('fields').get('date'), "%Y-%m-%d"
    )
    assert transaction_date.date() == today

    instance = Transaction.objects.get(id=transaction.get('pk'))
    assert instance.description == stub.description
    assert instance.amount == stub.amount
    assert instance.date == today


@pytest.mark.usefixtures('transactional_db')
def test_retrieve_transaction(client):
    today = datetime.date.today()
    account = AccountFactory.create()

    instance = TransactionFactory.create(account=account, date=today)
    result = client.get(reverse('transaction_view', args=(instance.id, )))

    assert result.status_code == 200
    response_body = result.json()

    assert len(response_body) == 1
    transaction = response_body[0]

    assert transaction.get('pk') is not None
    assert transaction.get('fields').get('description') == instance.description
    assert transaction.get('fields').get('amount') == instance.amount
    transaction_date = datetime.datetime.strptime(
        transaction.get('fields').get('date'), "%Y-%m-%d"
    )
    assert transaction_date.date() == today


@pytest.mark.usefixtures('transactional_db')
def test_retrieve_balance(client):
    today = datetime.date.today()

    account = AccountFactory.create()
    for date_offset in range(0, 5):
        TransactionFactory.create_batch(
            5, account=account,
            date=today - datetime.timedelta(days=date_offset)
        )

    response = client.get(reverse('account_balance_view', args=(account.id, )))
    assert response.status_code == 200
    assert len(response.json().get('data')) == 5

    response = client.get(
        reverse('account_balance_view', args=(account.id, )),
        {
            'from_date': (today - datetime.timedelta(days=1)).isoformat()
        }
    )
    assert response.status_code == 200
    assert len(response.json().get('data')) == 2

    response = client.get(
        reverse('account_balance_view', args=(account.id, )),
        {
            'to_date': (today - datetime.timedelta(days=3)).isoformat()
        }
    )
    assert response.status_code == 200
    assert len(response.json().get('data')) == 2

    response = client.get(
        reverse('account_balance_view', args=(account.id, )),
        {
            'from_date': (today - datetime.timedelta(days=3)).isoformat(),
            'to_date': (today - datetime.timedelta(days=1)).isoformat()
        }
    )
    assert response.status_code == 200
    assert len(response.json().get('data')) == 3
