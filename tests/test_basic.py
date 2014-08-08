from .models import User, Address, Session
from datatables import DataTable
import faker


class TestDataTables:
    def setup_method(self, method):
        self.session = Session()

    def make_data(self, user_count):
        f = faker.Faker()
        users = []

        for i in range(user_count):
            addr = Address()
            addr.description = f.address()

            u = User()
            u.full_name = f.name()
            u.address = addr
            users.append(u)

        self.session.add_all(users)
        self.session.commit()

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

        for i, item in enumerate(order):
            for key, value in item.items():
                x["order[{}][{}]".format(i, key)] = str(value)

        if search:
            for key, value in search.items():
                x["search[{}]".format(key)] = str(value)

        return x

    def test_basic_function(self):
        self.make_data(10)

        req = self.make_params(order=[{"column": 1, "dir": "asc"}])

        table = DataTable(req, User, self.session.query(User), [
            "id",
            ("name", "full_name"),
            ("address", "address.description"),
        ])

        x = table.json()

        assert len(x["data"]) == 10