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

    def test_basic_function(self):
        self.make_data(10)

        self.assertEqual(self.session.query(User).count(), 1)