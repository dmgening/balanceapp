import json

from django.http import HttpResponse
from django.views import View

from balanceapp.transactions import forms, models
from balanceapp.transactions.serializers import JsonHookSerializer


class RequestError(Exception):
    """
    """

    def __init__(self, status_code, *args, **kwargs):
        self.status_code = status_code
        self.payload = kwargs or args
        if args:
            self.payload['__other__'] = args


class GenericAPIView(View):
    model = None
    form = None
    serializer = JsonHookSerializer()

    def save_from_json(self, request, instance=None):
        """ Save model from JSON body
        """
        if request.content_type != 'application/json':
            return RequestError(400, 'Invalid Content-Type header')
        try:
            form = self.form(json.loads(request.body.decode('utf-8')))
        except json.JSONDecodeError:
            raise RequestError(400, 'Failed to load json')
        try:
            form.save()
        except ValueError as exc:
            raise RequestError(400, **form.errors)
        return form.instance

    def get(self, request, pk):
        if pk is None:
            return HttpResponse(self.serializer.serialize(self.model.objects.all()),
                                content_type='application/json')
        try:
            instance = self.model.objects.get(id=int(pk))
        except ValueError:
            raise RequestError(400, 'Primary key should be integer')
        except self.model.DoesNotExist:
            raise RequestError(404, 'Cant find object with id %s' % pk)
        return HttpResponse(self.serializer.serialize((instance, )),
                            content_type='application/json')

    def post(self, request, pk):
        if pk is not None:
            raise RequestError(400, 'Cant create object with primary key')
        instance = self.save_from_json(request)
        return HttpResponse(self.serializer.serialize((instance, )),
                            status=201, content_type='application/json')

    def patch(self, request, pk):
        if pk is None:
            raise RequestError(400, 'Cant patch object without primary key')
        try:
            instance = self.model.objects.get(id=int(pk))
        except ValueError:
            raise RequestError(400, 'Primary key should be integer')
        except self.model.DoesNotExist:
            raise RequestError(404, 'Cant find object with id %s' % pk)
        instance = self.save_from_json(request)
        return HttpResponse(self.serializer.serialize((instance, )),
                            status=200, content_type='application/json')

    def dispatch(self, request, *args, **kwargs):
        try:
            return super(GenericAPIView, self).dispatch(request, *args,
                                                        **kwargs)
        except RequestError as exc:
            return HttpResponse(json.dumps({'errors': exc.payload}),
                                status=exc.status_code)


class AccountView(GenericAPIView):
    model = models.Account
    form = forms.AccountForm

    @classmethod
    def balance(cls, request, pk):
        """ Retrieve balance changes for period.
        """
        try:
            account = cls.model.objects.get(id=int(pk))
        except ValueError:
            return HttpResponse(json.dumps({
                'errors': ['Primary key should be integer', ]
            }), status=400)
        except cls.model.DoesNotExist:
            return HttpResponse(json.dumps({
                'errors': ['Cant find account with id %s', ]
            }), status=404)

        request_form = forms.BalanceRequestForm(request.GET)
        if not request_form.is_valid():
            return HttpResponse(json.dumps(request_form.errors), status=400)

        queryset = account.balance_set
        if request_form.cleaned_data.get('from_date'):
            queryset = queryset.filter(
                date__gte=request_form.cleaned_data.get('from_date'))
        if request_form.cleaned_data.get('to_date'):
            queryset = queryset.filter(
                date__lte=request_form.cleaned_data.get('to_date'))

        response = [
            (balance.date.isoformat(), balance.amount)
            for balance in queryset.order_by('date').all()
        ]

        return HttpResponse(json.dumps({'data': response}),
                            content_type='application/json')


class TransactionView(GenericAPIView):
    model = models.Transaction
    form = forms.TransactionForm

    def get(self, request, pk):
        if pk is None:
            raise RequestError('Cant list transaction')
        return super(TransactionView, self).get(request, pk)

    def patch(self, request, pk):
        raise RequestError('Cant patch transaction')
