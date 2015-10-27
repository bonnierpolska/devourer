Devourer
========

Devourer is a generic API client. It features an object-oriented, declarative approach to simplify the communication.
It depends on the brilliant requests package as the gateway to API server. A simple example:

```python
from devourer import GenericAPI


class TestApi(GenericAPI):
    categories = APIMethod('get', 'categories/')
    news_list = APIMethod('get', 'news/list/{id}/')
    news = APIMethod('get', 'news/{id}/')
    add_news = APIMethod('post', 'news/')

    def __init__(self):
        super(TestApi, self).__init__('https://test.api.com/v1/',
                                      (user, password),
                                      load_json=True,
                                      throw_on_error=True
                                     )
                                     
api = TestApi()
categories = api.categories()
news_list = api.news_list(id=categories[0]['id'])
news = api.news(id=news_list[0]['id'])
status = api.add_news(author='John Doe', title='Breaking news', content='I just got devoured.')
```

The init function gives details so you don't need to repeat them elsewhere, enables parsing json responses and
raising exceptions on error.

Contributions
=============

Please read CONTRIBUTORS file before submitting a pull request.
For now we don't have any CI going on, but you can run lint and coverage by hand. The targets are 10.00 and 100%,
respectively. You will need to pip install coverage pylint to do it.

```
pylint devourer --rcfile=.pylintrc
coverage run --source=devourer -m devourer.tests && coverage report -m
```