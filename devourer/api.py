"""
This module contains a generator of declarative, object-oriented API representation and
all the helper classes it requires to work.
"""
from string import Formatter
import requests
import json

__all__ = ['APIMethod', 'GenericAPI', 'APIError', 'PrepareCallArgs']


class APIError(Exception):
    """
    An error while querying the API.
    """
    pass


class PrepareCallArgs(object):  # pylint: disable=too-few-public-methods
    """
    An inner class containing properties required to fire off a request to an API.
    It's not a namedtuple because it provides default values.
    """
    __slots__ = ['call', 'args', 'kwargs']

    def __init__(self, call=None, args=None, kwargs=None):
        """
        This method initializes the instance's properties with sane defaults.
        :param call: a callable that should be used to request the API.
        :param args: arguments passed to that function.
        :param kwargs: keyword arguments passed to that function.
        :return:
        """
        self.call = call or (lambda *arguments, **keywords: None)
        self.args = args or []
        self.kwargs = kwargs or {}


class APIMethod(object):
    """
    This class represents a single method in an API. It's able to dynamically
    create request URL using schema and call parameters.
    """
    def __init__(self, http_method, schema):
        """
        This method initializes instance's properties, especially schema and parameters
        list which is inferred from schema.
        :param schema: Python 3-style format string containing relative method address
        with parameters.
        :param http_method: HTTP method to call the API method with.
        :return:
        """
        self.name = None
        self.api = None
        self.http_method = http_method
        self._params = []
        self._schema = None
        self.schema = schema

    @property
    def schema(self):
        """
        Method's address relative to API address.
        :return: Method's address relative to API address.
        """
        return self._schema

    @schema.setter
    def schema(self, schema):
        """
        This method updates method's address schema and available parameters list.
        :param schema: Python 3-style format string containing relative method address
        with parameters.
        :return: None
        """
        self._schema = schema
        self._params = [a[1] for a in Formatter().parse(self.schema) if a[1]]

    @property
    def params(self):
        """
        List of available parameters for this method.
        :return: List of available parameters for this method.
        """
        return self._params

    def __call__(self, **kwargs):
        """
        This method sends a request to API through invoke function from API object
        the method is assigned to. It calls invoke with formatted schema, additional
        arguments and http method already calculated.
        :return: API request's result.
        """
        params = {key: value for key, value in kwargs.iteritems() if key not in self.params}
        return self.api.invoke(self.http_method, self.schema.format(**kwargs), params=params)


class GenericAPICreator(type):
    """
    This creator is a metaclass (it's a subclass of type, not object) responsible for
    creating and injecting helper methods as well as connecting APIMethods with
    GenericAPI.
    """

    def __new__(mcs, name, bases, attrs):
        """
        This method creates a new class and prepares it to use by creating and
        injecting helper methods (if they were not provided) and assigns APIMethods
        to created class.
        :param mcs:
        :param name:
        :param bases:
        :param attrs:
        :return:
        """
        methods = {}
        # We don't want to modify the base classes, just the implementations of them.
        if not (len(bases) == 1 and object in bases):
            attrs['_methods'] = {}
            for key, item in attrs.iteritems():
                if isinstance(item, APIMethod):
                    attrs['_methods'][key] = item
                    item.name = key
                    methods['prepare_{}'.format(key)] = GenericAPI.prepare
                    methods['{}'.format(key)] = attrs['call_{}'.format(key)] if \
                        'call_{}'.format(key) in attrs else GenericAPI.outer_call(key)
                    methods['finalize_{}'.format(key)] = GenericAPI.finalize
            for key in attrs['_methods']:
                del attrs[key]
                if 'call_{}'.format(key) in attrs:
                    del attrs['call_{}'.format(key)]
            methods.update(attrs)
            model = super(GenericAPICreator, mcs).__new__(mcs, name, bases, methods)
        else:
            model = super(GenericAPICreator, mcs).__new__(mcs, name, bases, attrs)
        return model


class GenericAPI(object):
    """
    This is the base API representation class.
    You can build a concrete API by declaring methods while creating the class, ie.:
        method1 = APIMethod('get', 'people/')
        method2 = APIMethod('get', 'my/news/items/')
    Hooks can be overridden globally:
        def prepare(self, name, **args, **kwargs):
            pass
    As well as for particular methods:
        def prepare_method1(self, name, *args, **kwargs):
            pass
        def call_method1(self, name, *args, **kwargs):
            pass
        def finalize_method2(self, name, result, *args, **kwargs):
            pass
    :type _methods: dict
    """
    __metaclass__ = GenericAPICreator
    _methods = None

    def __init__(self, url, auth, throw_on_error=False, load_json=False):
        """
        This method initializes a concrete API class.
        :param url: API's base address
        :param auth: a tuple (user, password) for HTTP authentication, None for
        no authentication, requests' Auth object otherwise.
        :param throw_on_error: should an error be thrown on response with code >= 400
        (True) or full response object be returned (False).
        :return:
        """
        self.url = url
        self.auth = auth
        self.throw_on_error = throw_on_error
        self.load_json = load_json
        for item in self._methods.itervalues():
            item.api = self

    def prepare(self, name, *args, **kwargs):
        """
        This function is a pre-request hook. It receives the exact same parameters
        as the API method call and the name of the method. It should return a
        PrepareCallArgs instance.
        By default it doesn't change the args and selects 'name' method from the
        class declaration as the callable to execute.
        :param name: name of API method to call.
        :param args:
        :param kwargs:
        :return: PrepareCallArgs instance
        """
        return PrepareCallArgs(call=self._methods[name], args=args, kwargs=kwargs)

    def finalize(self, name, result, *args, **kwargs):
        """
        Post-request hook.
        By default it takes care of throw_on_error and returns response content.
        :param name: name of the called method.
        :param result: requests' response object.
        :param args:
        :param kwargs:
        :return: result.content
        """
        if self.throw_on_error and result.status_code >= 400:
            error_msg = "Error when invoking {} with parameters {} {}: {}"
            raise APIError(error_msg.format(name, args, kwargs, result.__dict__))
        if self.load_json:
            return json.loads(result.content)
        return result.content

    def call(self, name, *args, **kwargs):
        """
        This function invokes the API method from the class declaration
        according to the name parameter along with all the hooks.
        :param name: name of method to call.
        :param args:
        :param kwargs:
        :return: Result of finalize_method call, by default content of
        API's response.
        """
        prepared = getattr(self, 'prepare_{}'.format(name))(name, *args, **kwargs)
        return getattr(self, 'finalize_{}'.format(name))(name,
                                                         prepared.call(*prepared.args, **prepared.kwargs),
                                                         *prepared.args,
                                                         **prepared.kwargs)

    @classmethod
    def outer_call(cls, name):
        """
        This is a wrapper creating anonymous function invoking call with correct
        method name.
        :param name: Name of method for which call wrapper has to be created.
        :return: drop-in call replacement lambda.
        """
        return lambda obj, *args, **kwargs: obj.call(name, *args, **kwargs)

    def invoke(self, http_method, url, params):
        """
        This method makes a request to given API address concatenating the method
        path and passing along authentication data.
        :param http_method: http method to be used for this call.
        :param url: exact address to be concatenated to API address.
        :return: response object as in requests.
        """
        return getattr(requests, http_method)(self.url + url, auth=self.auth, params=params)
