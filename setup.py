from distutils.core import setup

setup(
    name='devourer',
    packages=['devourer'],
    version='0.4.4',
    install_requires=[
        'requests',
        'futures',
        'six',
    ],
    description='Devourer is a generic API client.'
                'It features an object-oriented, declarative approach to simplify the communication.',
    author='Bonnier Business Polska / Krzysztof Bujniewicz',
    author_email='racech@gmail.com',
    url='https://github.com/bonnierpolska/devourer',
    download_url='https://github.com/bonnierpolska/devourer/tarball/0.4.4',
    keywords=['api', 'generic api', 'api client'],
    classifiers=[]
)
