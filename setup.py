""" PyPI setup.cfg """

from setuptools import find_packages, setup

setup(
    name='goldman',
    packages=find_packages(),
    version='0.1.6',
    description='An opinionated WSGI web framework',
    author='Sassoo',
    author_email='noreply@devnull.seriously',
    url='https://github.com/sassoo/goldman',
    license='MIT',
    download_url='https://github.com/sassoo/goldman/tarball/0.1.6',
    keywords=['framework', 'http', 'jsonapi', 'rest', 'web', 'wsgi'],
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
    ],
    install_requires=[
        'blinker',
        'boto',
        'falcon',
        'phonenumbers',
        'psycopg2',
        'schematics',
        'us',
    ],
)
