===============================================
datatables |PyPi Version| |TravisCI| |Coverage|
===============================================

.. |PyPi Version| image:: http://img.shields.io/pypi/v/datatables.svg?style=flat
    :target: https://pypi.python.org/pypi/datatables

.. |TravisCI| image:: https://api.travis-ci.org/orf/datatables.svg
    :target: https://travis-ci.org/orf/datatables

.. |Coverage| image:: https://coveralls.io/repos/orf/datatables/badge.png?branch=master
  :target: https://coveralls.io/r/orf/datatables?branch=master




Installation
------------

The package is available on `PyPI <https://pypi.python.org/pypi/datatables>`_ and is tested on Python 2.7 to 3.4

.. code-block:: bash

    pip install datatables

Usage
-----

Using Datatables is simple. Construct a DataTable instance by passing it your request parameters (or another dict-like
object), your model class, a base query and a set of columns. The columns list can contain simple strings which are
column names, or tuples containing (datatable_name, model_name), (datatable_name, model_name, filter_function) or
(datatable_name, filter_function).

Additional data such as hyperlinks can be added via DataTable.add_data, which accepts a callable that is called for
each instance. Check out the usage example below for more info.


Example
-------

**models.py**

.. code-block:: python

    class User(Base):
        __tablename__ = 'users'

        id          = Column(Integer, primary_key=True)
        full_name   = Column(Text)
        created_at  = Column(DateTime, default=datetime.datetime.utcnow)

        # Use lazy=joined to prevent O(N) queries
        address     = relationship("Address", uselist=False, backref="user", lazy="joined")

    class Address(Base):
        __tablename__ = 'addresses'

        id          = Column(Integer, primary_key=True)
        description = Column(Text, unique=True)
        user_id     = Column(Integer, ForeignKey('users.id'))

**views.py (pyramid)**

.. code-block:: python

    @view_config(route_name="data", request_method="GET", renderer="json")
    def users_data(request):
        # User.query = session.query(User)
        table = DataTable(request.GET, User, User.query, [
            "id",
            ("name", "full_name", lambda i: "User: {}".format(i.full_name)),
            ("address", "address.description"),
        ])
        table.add_data(link=lambda o: request.route_url("view_user", id=o.id))
        table.searchable(lambda queryset, user_input: perform_search(queryset, user_input))
        table.searchable_column(
            lambda model_column, queryset, user_input:
                perform_column_search(model_column, queryset, user_input)
        )

        return table.json()

**views.py (flask)**

.. code-block:: python

    @app.route("/data")
    def datatables():
        table = DataTable(request.args, User, db.session.query(User), [
            "id",
            ("name", "full_name", lambda i: "User: {}".format(i.full_name)),
            ("address", "address.description"),
        ])
        table.add_data(link=lambda obj: url_for('view_user', id=obj.id))
        table.searchable(lambda queryset, user_input: perform_search(queryset, user_input))
        table.searchable_column(
            lambda model_column, queryset, user_input:
                perform_column_search(model_column, queryset, user_input)
        )

        return json.dumps(table.json())

**Global and individual column searching**

.. code-block:: python

    def perform_search(queryset, user_input):
        return queryset.filter(
            db.or_(
                User.full_name.like('%' + user_input + '%'),
                Address.description.like('%' + user_input + '%')
                )
            )

    def perform_column_search(model_column, queryset, user_input):
        return queryset.filter(model_column.like("%" + user_input + "%"))

**template.jinja2**

.. code-block:: html

    <table class="table" id="clients_list">
        <thead>
            <tr>
                <th>Id</th>
                <th>User name</th>
                <th>Address</th>
            </tr>
        </thead>
        <tbody>
        </tbody>
    </table>

    <script>
        $("#clients_list").dataTable({
            serverSide: true,
            processing: true,
            ajax: "{{ request.route_url("data") }}",
            columns: [
                {
                    data: "id",
                    "render": function(data, type, row){
                        return $("<div>").append($("<a/>").attr("href", row.DT_RowData.link).text(data)).html();
                    }
                },
                { data: "name" },
                { data: "address" }
            ]
    </script>