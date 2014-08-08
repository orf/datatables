from collections import defaultdict, namedtuple
from sqlalchemy.sql.expression import asc, desc
from sqlalchemy.orm import joinedload
import re
import inspect


BOOLEAN_FIELDS = (
    "search.regex", "searchable", "orderable", "regex"
)


DataColumn = namedtuple("DataColumn", ("name", "model_name", "filter"))


class DataTablesError(ValueError):
    pass


class DataTable(object):
    def __init__(self, request, model, query, columns):
        self.request = request
        self.params = request.params
        self.model = model
        self.query = query
        self.data = {}
        self.columns = []

        for col in columns:
            name, model_name, filter_func = None, None, None

            if isinstance(col, DataColumn):
                self.columns.append(col)
            elif isinstance(col, tuple):
                # col is either 1. (name, model_name), 2. (name, filter) or 3. (name, model_name, filter)
                if len(col) == 3:
                    name, model_name, filter_func = col
                elif len(col) == 2:
                    # Work out the second argument. If it is a function then it's type 2, else it is type 3.
                    if callable(col[1]):
                        name, filter = col
                        model_name = name
                    else:
                        name, model_name = col
                else:
                    raise ValueError("Columns must be a tuple of 2 to 3 elements")
            else:
                # It's just a string
                name, model_name = col, col

            self.columns.append(DataColumn(name=name, model_name=model_name, filter=filter_func))

        for column in (col for col in self.columns if "." in col.model_name):
            self.query = self.query.options(joinedload(column.model_name.split(".")[0]))

    def _property_from_name(self, name):
        mapper = self.model.__mapper__
        return mapper.get_property(name)

    def query_into_dict(self, key_start):
        returner = defaultdict(dict)

        # Matches columns[number][key] with an [optional_value] on the end
        pattern = "{}\[(\d+)\]\[(\w+)\](?:\[(\w+)\])?".format(key_start)

        columns = (param for param in self.params if re.match(pattern, param))

        for param in columns:

            column_id, key, optional_subkey = re.search(pattern, param).groups()
            column_id = int(column_id)

            if optional_subkey is None:
                returner[column_id][key] = self.coerce_value(key, self.params[param])
            else:
                # Oh baby a triple
                returner[column_id].setdefault(key, {})[optional_subkey] = self.coerce_value("{}.{}".format(key, optional_subkey),
                                                                                             self.params[param])

        return dict(returner)

    @staticmethod
    def coerce_value(key, value):
        try:
            return int(value)
        except ValueError:
            if key in BOOLEAN_FIELDS:
                return value == "true"

        return value

    def get_integer_param(self, param_name):
        if not param_name in self.params:
            raise DataTablesError("Parameter {} is missing".format(param_name))

        try:
            return int(self.params[param_name])
        except ValueError:
            raise DataTablesError("Parameter {} is invalid".format(param_name))

    def add_data(self, **kwargs):
        self.data.update(**kwargs)

    def json(self):
        draw = self.get_integer_param("draw")
        start = self.get_integer_param("start")
        length = self.get_integer_param("length")

        columns = self.query_into_dict("columns")
        ordering = self.query_into_dict("order")
        search = self.query_into_dict("search")

        query = self.query
        total_records = query.count()

        for order in ordering.values():
            direction, column = order["dir"], order["column"]
            column_name = columns[column]["data"]

            #model_column = getattr(self.model, column_name)
            query = query.order_by(asc(column_name) if direction == "asc" else desc(column_name))
            #model_column = self._column_from_name()
            pass

        query = query.slice(start, length)
        filtered_records = query.count()

        return {
            "draw": draw,
            "recordsTotal": total_records,
            "recordsFiltered": filtered_records,
            "data": [
                self.output_instance(instance) for instance in self.query.all()
            ]
        }

    def output_instance(self, instance):
        returner = {
            key.name: self.get_value(key, instance) for key in self.columns
        }

        if self.data:
            returner["DT_RowData"] = {
                k: v(instance) for k, v in self.data.items()
            }

        return returner

    def get_value(self, key, instance):
        attr = key.model_name
        if "." in attr:
            subkey, attr = attr.split(".", 1)
            instance = getattr(instance, subkey)

        r = getattr(instance, attr)

        return r() if inspect.isfunction(r) else r