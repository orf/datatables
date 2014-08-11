from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import User, Address, Base
from datatables import DataTable
import faker


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

    def make_params(self, order=None, search=None, start=0, length=10):
        x = {
            "draw": "1",
            "start": str(start),
            "length": str(length)
        }

        for i, item in enumerate(("id", "name", "address")):
            b = "columns[{}]".format(i)
            x[b + "[data]"] = item
            x[b + "[name]"] = ""
            x[b + "[searchable]"] = "true"
            x[b + "[orderable]"] = "true"
            x[b + "[search][value]"] = ""
            x[b + "[search][regex]"] = "false"

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
        req = self.make_params(order=[{"column": 2, "dir": "desc"}])
        table = DataTable(req,
                          User,
                          self.session.query(User),
                          [
                              "id",
                              ("name", "full_name"),
                              ("address", "address.description")
                          ])
        x = table.json()

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