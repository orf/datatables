from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import faker

from .models import User, Address, Base
from datatables import DataTable, DataColumn


class TestDataTables:
    def setup_method(self, method):
        engine = create_engine('sqlite://', echo=True)
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)

        self.session = Session()

    def make_data(self, user_count):
        f = faker.Faker()
        users = []

        for i in range(user_count):
            user, addr = self.make_user(f.name(), f.address())
            users.append(user)

        self.session.add_all(users)
        self.session.commit()

    def make_user(self, name, address):
        addr = Address()
        addr.description = address

        u = User()
        u.full_name = name
        u.address = addr

        return u, addr

    def make_params(self, order=None, search=None, column_search=None, start=0, length=10):
        x = {
            "draw": "1",
            "start": str(start),
            "length": str(length)
        }

        if column_search is None:
            column_search = {}

        for i, item in enumerate(("id", "name", "address")):
            b = "columns[{}]".format(i)
            x[b + "[data]"] = item
            x[b + "[name]"] = ""
            x[b + "[searchable]"] = "true"
            x[b + "[orderable]"] = "true"
            x[b + "[search][regex]"] = "false"
            x[b + "[search][value]"] = column_search.get(item, {}).get("value", "")

        for i, item in enumerate(order or []):
            for key, value in item.items():
                x["order[{}][{}]".format(i, key)] = str(value)

        if search:
            for key, value in search.items():
                x["search[{}]".format(key)] = str(value)

        return x

    def test_basic_function(self):
        self.make_data(10)

        req = self.make_params()

        table = DataTable(req, User, self.session.query(User), [
            "id",
            ("name", "full_name"),
            ("address", "address.description"),
        ])

        x = table.json()

        assert len(x["data"]) == 10

    def test_relation_ordering(self):
        self.make_data(10)
        u1, addr_asc = self.make_user("SomeUser", "0" * 15)
        u2, addr_desc = self.make_user("SomeOtherUser", "z" * 15)
        self.session.add_all((u1, u2))
        self.session.commit()

        req = self.make_params(order=[{"column": 2, "dir": "desc"}])
        table = DataTable(req,
                          User,
                          self.session.query(User),
                          [
                              "id",
                              ("name", "full_name"),
                              ("address", "address.description")
                          ])
        result = table.json()
        assert result["data"][0]["address"] == addr_desc.description

        req = self.make_params(order=[{"column": 2, "dir": "asc"}])
        table = DataTable(req,
                          User,
                          self.session.query(User),
                          [
                              "id",
                              ("name", "full_name"),
                              ("address", "address.description")
                          ])
        result = table.json()
        assert result["data"][0]["address"] == addr_asc.description

    def test_filter(self):
        self.make_data(10)
        req = self.make_params()

        table = DataTable(req,
                          User,
                          self.session.query(User),
                          [
                              "id",
                              ("name", "full_name", lambda i: "User: " + i.full_name)
                          ])
        result = table.json()
        assert all(r["name"].startswith("User: ") for r in result["data"])

    def test_extra_data(self):
        self.make_data(10)

        req = self.make_params()
        table = DataTable(req,
                          User,
                          self.session.query(User),
                          [
                              "id"
                          ])
        table.add_data(id_multiplied=lambda i: i.id * 10)

        result = table.json()
        assert all(r["id"] * 10 == r["DT_RowData"]["id_multiplied"] for r in result["data"])

    def test_column_inputs(self):
        self.make_data(10)
        req = self.make_params()

        table = DataTable(req,
                          User,
                          self.session.query(User),
                          [
                              DataColumn(name="id", model_name="id", filter=None),
                              ("full_name", lambda i: str(i)),
                              "address"
                          ])
        table.json()

    def test_ordering(self):
        self.make_data(10)
        desc_user, _ = self.make_user("z" * 20, "z" * 20)
        self.session.add(desc_user)
        self.session.commit()

        req = self.make_params(order=[{"column": 1, "dir": "desc"}])

        table = DataTable(req,
                          User,
                          self.session.query(User),
                          [
                              "id",
                              ("name", "full_name"),
                              ("address", "address.description")
                          ])

        x = table.json()

        assert x["data"][0]["name"] == desc_user.full_name

        req = self.make_params(order=[{"column": 1, "dir": "asc"}], length=100)

        table = DataTable(req,
                          User,
                          self.session.query(User),
                          [
                              "id",
                              ("name", "full_name"),
                              ("address", "address.description")
                          ])

        x = table.json()

        assert x["data"][-1]["name"] == desc_user.full_name

    def test_error(self):
        req = self.make_params()
        req["start"] = "invalid"

        table = DataTable(req,
                          User,
                          self.session.query(User),
                          ["id"])
        assert "error" in table.json()

        req = self.make_params()
        del req["start"]

        table = DataTable(req,
                          User,
                          self.session.query(User),
                          ["id"])
        assert "error" in table.json()

    def test_search(self):
        user, addr = self.make_user("Silly Sally", "Silly Sally Road")
        user2, addr2 = self.make_user("Silly Sall", "Silly Sally Roa")
        self.session.add_all((user, user2))
        self.session.commit()

        req = self.make_params(search={
            "value": "Silly Sally"
        })

        table = DataTable(req, User, self.session.query(User), [("name", "full_name")])
        table.searchable(lambda qs, sq: qs.filter(User.full_name.startswith(sq)))
        results = table.json()
        assert len(results["data"]) == 1

        req = self.make_params(search={
            "value": "Silly Sall"
        })

        table = DataTable(req, User, self.session.query(User), [("name", "full_name")])
        table.searchable(lambda qs, sq: qs.filter(User.full_name.startswith(sq)))
        results = table.json()
        assert len(results["data"]) == 2

    def test_column_search(self):
        user, addr = self.make_user("Silly Sally", "Silly Sally Road")
        user2, addr2 = self.make_user("Silly Sall", "Silly Sally Roa")
        self.session.add_all((user, user2))
        self.session.commit()

        req = self.make_params(column_search={
            "name": {
                "value": "Silly Sally"
            }
        })

        table = DataTable(req, User, self.session.query(User), [("name", "full_name")])
        table.searchable_column(lambda mc, qs, sq: qs.filter(mc.startswith(sq)))
        results = table.json()
        assert len(results["data"]) == 1

        req = self.make_params(column_search={
            "name": {
                "value": "Silly Sall"
            }
        })

        table = DataTable(req, User, self.session.query(User), [("name", "full_name")])
        table.searchable_column(lambda mc, qs, sq: qs.filter(mc.startswith(sq)))
        results = table.json()
        assert len(results["data"]) == 2

        req = self.make_params(column_search={
            "name": {
                "value": "Silly Sall"
            },
            "address": {
                "value": "Silly Sally Road"
            }
        })

        table = DataTable(
            req,
            User, self.session.query(User),
            [("name", "full_name"), ("address", "address.description")]
        )
        table.searchable_column(lambda mc, qs, sq: qs.filter(mc.startswith(sq)))
        results = table.json()
        assert len(results["data"]) == 1
