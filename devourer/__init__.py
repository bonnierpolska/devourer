"""
Devourer is a generic API client. It features an object-oriented, declarative approach to simplify the communication.
It depends on the brilliant requests package as the gateway to API server. A simple example:

>>> from devourer import GenericAPI, APIMethod, APIError
>>>
>>>
>>> class TestApi(GenericAPI):
>>>     posts = APIMethod('get', 'posts/')
>>>     comments = APIMethod('get', 'posts/{id}/comments')
>>>     post = APIMethod('get', 'posts/{id}/')
>>>     add_post = APIMethod('post', 'posts/')
>>>
>>>     def __init__(self,
>>>                  url=None,
>>>                  auth=None,
>>>                  throw_on_error=True,
>>>                  load_json=True):
>>>         params = (url or 'http://jsonplaceholder.typicode.com/',
>>>                   auth or None,  # this can be ('user', 'password')
>>>                                  # or requests auth object
>>>                   load_json=load_json,
>>>                   throw_on_error=throw_on_error)
>>>         super(TestApi, self).__init__(*params)
>>>
>>> api = TestApi()
>>> posts = api.posts()
>>> post = api.post(id=posts[0]['id'])
>>> comments = api.comments(id=post['id'])
>>> new_post_id = api.add_post(userId=1,
>>>                            title='Breaking news',
>>>                            body='I just got devoured.')
>>> try:
>>>     post = api.post(id=new_post_id)
>>> except APIError:
>>>     print('Oops, this API is not persistent!')

The init function gives details so you don't need to repeat them elsewhere, enables parsing json responses and
raising exceptions on error. You can also obtain raw string with `load_json=False` and silence errors getting
None instead when they happen with `throw_on_error=False`.

"""
from .api import GenericAPI, APIMethod, APIError, PrepareCallArgs, GenericAPICreator, GenericAPIBase
from .async import AsyncAPI, AsyncAPIBase
