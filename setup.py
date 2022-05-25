from distutils.core import setup
import os
from setuptools import find_packages

# User-friendly description from README.md
current_directory = os.path.dirname(os.path.abspath(__file__))
try:
    with open(os.path.join(current_directory, 'README.md'), encoding='utf-8') as f:
        long_description = f.read()
except Exception:
    long_description = ''


setup(
    # Name of the package
    name='authoriz',
    # Packages to include into the distribution
    packages=find_packages('.'),
    # Start with a small number and increase it with
    # every change you make https://semver.org
    version='0.0.3',
    # Chose a license from here: https: //
    # help.github.com / articles / licensing - a -
    # repository. For example: MIT
    license='BSD-2',
    # Short description of your library
    description='Django rules-based authorization framework.',
    # Long description of your library
    long_description=long_description,
    long_description_content_type='text/markdown',
    # Your name
    author='Ilya Vouk',
    # Your email
    author_email='ilya.vouk@gmail.com',
    # Either the link to your github or to your website
    url='https://github.com/VoIlAlex/authoriz',
    # Link from which the project can be downloaded
    download_url='',
    # List of keywords
    keywords=[],
    # List of packages to install with this one
    install_requires=[
        'Django==3.2.12',
        'python-rapidjson==1.6',
        'djangorestframework==3.13.1'
    ],
    # https://pypi.org/classifiers/
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Framework :: Django :: 3.2',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ]
)
