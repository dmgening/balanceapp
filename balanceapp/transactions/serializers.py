from django.core.serializers.json import Serializer


class JsonHookSerializer(Serializer):

    def get_dump_object(self, obj):
        data = super(JsonHookSerializer, self).get_dump_object(obj)
        serialization_hook = getattr(obj, 'serializer_hook', None)
        if serialization_hook is not None:
            assert hasattr(serialization_hook, '__call__')
            data = serialization_hook(obj, data)
        return data
