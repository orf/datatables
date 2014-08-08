from .models import User, Address, Session
from datatables import DataTable
import unittest
import faker


class DataTablesTest(unittest.TestCase):
    def setUp(self):
        self.session = Session()

    def make_data(self, user_count):
        f = faker.Faker()
        users = []

        for i in range(user_count):
            addr = Address()
            addr.description = f.address()

            u = User()
            u.first_name = f.first_name()
            u.last_name = f.last_name()
            u.address = addr
            users.append(u)

        self.session.add_all(users)
        self.session.commit()

    def make_params(self, columns, order=None, search=None, start=0, length=10):
        x = {
            "draw": "1",
            "start": str(start),
            "length": str(length)
        }
        for i, item in enumerate(order):
            for key, value in order[item].items():
                x["order[{}][{}]".format(i, key)] = str(value)

        if search:
            for key, value in search.items():
                x["search[{}]".format(key)] = str(value)

    def test_basic_function(self):
        self.make_data(10)

        table = DataTable()


        self.assertEqual(self.session.query(User).count(), 10)