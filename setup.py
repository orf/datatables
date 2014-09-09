from setuptools import setup


setup(
    name='datatables',
    version='0.4.4',
    packages=['datatables'],
    url='https://github.com/orf/datatables/',
    license='MIT',
    long_description=open("readme.rst").read(),
    keywords='sqlalchemy datatables jquery pyramid flask',
    author='Tom',
    author_email='tom@tomforb.es',
    description='Integrates SQLAlchemy with DataTables (framework agnostic)',
    requires=['sqlalchemy', 'sqlalchemy_utils'],
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
