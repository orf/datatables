from setuptools import setup
import os

desc = open("readme.rst").read() if os.path.isfile("readme.rst") else ""


setup(
    name='datatables',
    version='0.4.9',
    packages=['datatables'],
    url='https://github.com/orf/datatables/',
    license='MIT',
    long_description=desc,
    keywords='sqlalchemy datatables jquery pyramid flask',
    author='Tom',
    author_email='tom@tomforb.es',
    description='Integrates SQLAlchemy with DataTables (framework agnostic)',
    zip_safe=False,
    include_package_data=True,
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Pyramid',
        'Framework :: Flask',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
