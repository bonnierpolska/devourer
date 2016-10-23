Devourer
========

[![Build Status](https://travis-ci.org/bonnierpolska/devourer.svg)](https://travis-ci.org/bonnierpolska/devourer)

Devourer is a generic REST API client for Python 2.7 and 3.3+.

You can also subclass it to wrap a set of system calls, FFI or a messy dependency.

It features an object-oriented, declarative approach to simplify the communication.
It depends on the brilliant requests package as the gateway to API server.

### Basic usage

```python
from devourer import GenericAPI, APIMethod, APIError


class TestApi(GenericAPI):
    posts = APIMethod('get', 'posts/')
    comments = APIMethod('get', 'posts/{id}/comments')
    post = APIMethod('get', 'posts/{id}/')
    add_post = APIMethod('post', 'posts/')

    def __init__(self):
        super(TestApi, self).__init__('http://jsonplaceholder.typicode.com/',
                                      None,  # this can be ('user', 'password')
                                             # or requests auth object
                                      load_json=True,
                                      throw_on_error=True
                                     )

api = TestApi()
posts = api.posts()
post = api.post(id=posts[0]['id'])
comments = api.comments(id=post['id'])
new_post_id = api.add_post(data={'userId': 1,
                                 'title': 'Breaking news',
                                 'body': 'I just got devoured.'})
try:
    post = api.post(id=new_post_id)
except APIError:
    print('Oops, this API is not persistent!')
```

The init function gives details so you don't need to repeat them elsewhere, enables parsing json responses and
raising exceptions on error. You can also obtain raw string with `load_json=False` and silence errors getting
None instead when they happen with `throw_on_error=False`.

When calling methods:
* `data` and `payload` kwargs will be passed to requests call as `data` and `json` parameters.
* all keyword arguments matching schema will be used in schema.
* all other kwargs will be passed to requests call as query string parameters.

### Async usage

Devourer supports asynchronous calls using concurrent.futures's ThreadPoolExecutor. API subclasses
are created and used as usual, they just need to inherit from `AsyncAPI` instead of `GenericAPI`.

Async mode will work with threads. They can be system threads or gevent threads, but that requires monkey patching them.

```python
class AsyncTestApi(AsyncAPI):
    posts = APIMethod('get', 'posts/')

api = AsyncTestApi()
posts = api.posts()  # Send HTTP request, but don't block. Returns a `concurrent.futures.Future`.
result = posts_r.result()     # Retrieve result, blocking if the request hasn't finished yet.
```

Installation
------------
You can just `pip install devourer`.

Documentation
-------------

Feel free to browse the code and especially the tests to see what's going on behind the scenes.
The current version of docs is available on http://devourer.readthedocs.org/en/latest/.

There's also an article on the thought process behind devourer on http://bujniewi.cz/devouring-an-api/ - it's a five
minute read, but it could answer a few questions you might have.

Questions and contact
---------------------

If you have any questions, feedback, want to say hi or talk about Python, just hit me up on
https://twitter.com/bujniewicz

Contributions
-------------

Please read CONTRIBUTORS file before submitting a pull request.

We use Travis CI. The targets are 10.00 for lint and 100% for coverage, as well as building sphinx docs.

You can also check the build manually, just make sure to `pip install -r requirements.txt` before:

```
pylint devourer --rcfile=.pylintrc
coverage run --source=devourer -m devourer.tests && coverage report -m
cd docs && make html
```

Additionally you can check cyclomatic complexity and maintenance index with radon:

```
radon cc devourer
radon mi devourer
```

The target is A for maintenance index, C for cyclomatic complexity - but don't worry if it isn't met, I can
refactor it after merging.
