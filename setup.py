
from pathlib import Path
from setuptools import find_packages, setup

BASE_DIR = Path(__file__).resolve().parent
README = (BASE_DIR / 'README.md').read_text(encoding='utf-8')

setup(
    name='django5-rolodex',
    version='0.2.0',
    packages=find_packages(exclude=('example', 'example.*')),
    include_package_data=True,
    license='MIT License',
    description='Contact and organization relationship graph for Django projects.',
    long_description=README,
    long_description_content_type='text/markdown',
    url='https://github.com/iraabbott/django-rolodex',
    author='Infinity Stack Team',
    author_email='ops@softoboros.com',
    python_requires='>=3.11',
    install_requires=[
        'Django>=4.2,<6.0',
        'djangorestframework>=3.15.0',
        'dj-database-url>=0.5.0',
        'networkx>=2.8',
        'django-taggit>=5.0',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 4',
        'Framework :: Django :: 5',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.11',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
