"""
.. module:: async
    :platform: Unix, Windows
    :synopsis: This module extends basic api with gevent-based async capabilities.

"""
from functools import partial

from concurrent.futures import ThreadPoolExecutor
from six import with_metaclass

from devourer import GenericAPIBase
from devourer import GenericAPICreator


# Default time (seconds) to wait for thread before timing out.
DEFAULT_ASYNC_TIMEOUT = 5.0

# Default executor class.
DEFAULT_EXECUTOR = ThreadPoolExecutor  # pylint: disable=invalid-name

# Default number of executors for an API instance.
DEFAULT_EXECUTORS = 2


class AsyncAPIBase(GenericAPIBase):
    """This is the async API representation class without declarative syntax.

    Requires GenericAPICreator metaclass to work.

    :type _methods: dict
    """
    _methods = None

    def __init__(self, *args, **kwargs):
        """
        Add async settings and invoke base initializer.
        :param args:
        :param executors: number of concurrent executor workers.
        :param executor_class: executor class.
        :param executor: executor instance. Takes priority over executor_class.
        :param kwargs:
        """
        executor = kwargs.pop('executor', None)
        executors = kwargs.pop('executors', DEFAULT_EXECUTORS)
        executor_class = kwargs.pop('executor_class', DEFAULT_EXECUTOR)
        if executor:
            self._executor = executor
        else:
            self._executor = executor_class(max_workers=executors)
        super(AsyncAPIBase, self).__init__(*args, **kwargs)

    def call(self, name, *args, **kwargs):
        """
        This function invokes the API method from the class declaration
        according to the name parameter along with all the hooks.

        :param name: name of method to call.
        :param args: non-keyword arguments of API method call.
        :param kwargs: keyword arguments of API method call.
        :returns: Result of finalize_method call, by default content of API's response.
        """
        prepared = getattr(self, 'prepare_{}'.format(name))(name, *args, **kwargs)
        method_partial = partial(prepared.call, self, *prepared.args, **prepared.kwargs)
        callback_partial = partial(
            getattr(self, 'finalize_{}'.format(name)),
            name,
            *prepared.args,
            **prepared.kwargs
        )
        future = self._executor.submit(lambda c, m: c(m()), callback_partial, method_partial)
        return future


class AsyncAPI(with_metaclass(GenericAPICreator, AsyncAPIBase)):
    """This is the async API representation class.

    You can build a concrete API by declaring methods while creating the class, ie.:

    >>> class MyAPI(AsyncAPI):
    >>>     method1 = APIMethod('get', 'people/')
    >>>     method2 = APIMethod('post', 'my/news/items/')

    Hooks can be overridden globally:

    >>> def prepare(self, name, **args, **kwargs):
    >>>     return PrepareCallArgs(call=self._methods[name],
    >>>                            args=args,
    >>>                            kwargs=kwargs)

    As well as for particular methods only:

    >>> def prepare_method1(self, name, *args, **kwargs):
    >>>     return PrepareCallArgs(call=self._methods[name],
    >>>                            args=args,
    >>>                            kwargs=kwargs)

    >>> def call_method1(self, name, *args, **kwargs):
    >>>     prepared = getattr(self, 'prepare_{}'.format(name))
    >>>     prepared = prepared(name, *args, **kwargs)
    >>>     callback = getattr(self, 'finalize_{}'.format(name))
    >>>     return callback(name,
    >>>                     prepared.call(*prepared.args,
    >>>                                   **prepared.kwargs),
    >>>                     *prepared.args,
    >>>                     **prepared.kwargs)

    >>> def finalize_method2(self, name, future, *args, **kwargs):
    >>>     result = future.result()
    >>>     if self.throw_on_error and result.status_code >= 400:
    >>>         error_msg = "Error when invoking {} with parameters {} {}: {}"
    >>>         params = (name, args, kwargs, result.__dict__)
    >>>         raise APIError(error_msg.format(*params))
    >>>     if self.load_json:
    >>>         return json.loads(result.content)
    >>>     return result.content
    """
    pass
