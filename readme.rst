=========================
datatables |PyPi Version|
=========================

.. |PyPi Version| image:: http://img.shields.io/pypi/v/datatables.svg?style=flat
    :target: https://pypi.python.org/pypi/datatables


Installation
------------

The package is available on `PyPI <https://pypi.python.org/pypi/datatables>`_

.. code-block:: bash

    pip install datatables


Quickstart
----------

**models.py**

.. code-block:: python

    class User(Base):
        __tablename__ = 'users'

        id          = Column(Integer, primary_key=True)
        full_name   = Column(Text)
        created_at  = Column(DateTime, default=datetime.datetime.utcnow)

        address     = relationship("Address", uselist=False, backref="user")

    class Address(Base):
        __tablename__ = 'addresses'

        id          = Column(Integer, primary_key=True)
        description = Column(Text, unique=True)
        user_id     = Column(Integer, ForeignKey('users.id'))

**views.py**

.. code-block:: python

    @view_config(route_name="data", request_method="GET", renderer="json")
    def scopes_data(request):

        table = DataTable(request.params, User, User.query, [
            "id",
            ("name", "full_name"),
            ("address", "address.description"),
        ])
        table.add_data(link=lambda o: request.route_url("view_user", id=o.id))

        return table.json()

**template.jinja2**

.. code-block:: html

    <table class="table" id="simple-example">
        <thead>
            <tr>
                <th>Id</th>
                <th>User name</th>
                <th>Address description</th>
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