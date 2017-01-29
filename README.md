Запуск контейнеров:
`docker-compose up -d`

Запуск тестов на запущенном контейнере:
`docker-compose exec pytest -v`

Запросы API:

Создание счета:
```
$ curl localhost:8000/api/0.1/accounts -H "Content-Type: application/json" -X POST -d "{\"title\": \"my account\"}"
{ "data": [{"model": "transactions.account", "pk": 103, "fields": {"title": "my account", "balance": 0}}]}
```

Получение счета:
```
$ curl localhost:8000/api/0.1/accounts/103 
{ "data": [{"model": "transactions.account", "pk": 103, "fields": {"title": "my account", "balance": 0}}]}
```

Получение баланса счета:
```
$ curl localhost:8000/api/0.1/accounts/10/balance\?from_date=2017-01-25\&to_date=2017-01-26
{"data": [["2017-01-25", -181019], ["2017-01-26", -190008]]}
```

Создание транзакции:
```
$ curl localhost:8000/api/0.1/transactions -H "Content-Type: application/json" -X POST -d "{\"description\": \"my transaction\", \"amount\": 100, \"account\": 10, \"date\": \"2016-11-01\"}"
{ "data": [{"model": "transactions.transaction", "pk": 510001, "fields": {"description": "my transaction", "amount": 100, "date": "2016-11-01", "account": 10}}]}%
```

Получение транзакции:
```
$ curl localhost:8000/api/0.1/transactions/50001
{ "data": [{"model": "transactions.transaction", "pk": 50001, "fields": {"description": "Watson Inc", "amount": -2119, "date": "2017-01-28", "account": 11}}]}
```
