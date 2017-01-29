from django.core.serializers.json import Serializer


class JsonHookSerializer(Serializer):

    def start_serialization(self):
        self._init_options()
        self.stream.write("{ \"data\": [")

    def end_serialization(self):
        super(JsonHookSerializer, self).end_serialization()
        self.stream.write("}")

    def get_dump_object(self, obj):
        """ Run additional hooks attached to model after object serialization
        """
        data = super(JsonHookSerializer, self).get_dump_object(obj)
        serialization_hook = getattr(obj, 'serializer_hook', None)
        if serialization_hook is not None:
            assert hasattr(serialization_hook, '__call__')
            data = serialization_hook(obj, data)
        return data
