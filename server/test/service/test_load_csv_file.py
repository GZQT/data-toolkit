import json
import os
from unittest import mock

import responses

from constant import CONFIG_FILE
from dto.generator import GeneratorConfigRequest
from service.load_csv_file import LoadCsvFile

expected_format = '%Y-%m-%d-%H-%M-%S.%f'

builtin_open = open


def _check_format(dt):
    return dt.strftime(expected_format) == dt.strftime(expected_format)


current_file_path = os.path.abspath(__file__)
test_file = os.path.abspath(os.path.join(os.path.dirname(current_file_path), "test.csv"))


class TestLoadCsv:

    def test_file_error(self):
        load = LoadCsvFile("test_no_exist.csv")
        assert '不存在' in load.output
        load = LoadCsvFile("__init__.py")
        assert '不是 csv 类型' in load.output

    def test_no_config(self):
        loader = LoadCsvFile(test_file)
        loader = loader.load_data()
        assert len(loader.data) == 50
        assert len(loader.data.columns) == 18
        assert "col0" in loader.data.columns
        assert "col16" in loader.data.columns
        for i in range(50):
            assert loader.data['col1'][i] == i + 1
        for i in range(50):
            assert loader.data['col2'][i] == 1
        for i in range(50):
            s = (i + 1) % 5
            if s == 0:
                assert loader.data['col3'][i] == 5
            else:
                assert loader.data['col3'][i] == s
        assert loader.times.apply(lambda x: _check_format(x)).all(), \
            f"'time' column contains values not in the format '{expected_format}'."

    def test_apply_expressions(self):
        param = {
            'converters': [
                {'columnKey': 'col1', 'expression': 'c1+100'},
                {'columnKey': 'col2', 'expression': 'c2-100'},
                {'columnKey': 'col3', 'expression': 'c3+c2'},
                {'columnKey': 'col4', 'expression': 'c4-c2'},
                {'columnKey': 'col5', 'expression': 'c5*0'},
                {'columnKey': 'col6', 'expression': 'c5*c2'},
                {'columnKey': 'col7', 'expression': '(c2+1)*3'},
                {'columnKey': 'col8', 'expression': '(c8+1)/2'},
            ],
            'dauConfig': None
        }
        loader = LoadCsvFile(test_file).load_data(GeneratorConfigRequest(**param))
        for i in range(50):
            assert loader.data['col1'][i] == i + 1 + 100
            assert loader.data['col2'][i] == 1 - 100
            assert loader.data['col4'][i] == 4
            assert loader.data['col5'][i] == 0
            assert loader.data['col6'][i] == 50 - i
            assert loader.data['col7'][i] == 6
            assert loader.data['col8'][i] == 1

    def mock_open(*args, **kwargs):
        config_content = {
            "remoteServer": "http://fake_server",
            "mapping": "mapping"
        }
        if args[0] == CONFIG_FILE:
            return mock.mock_open(read_data=json.dumps(config_content))(*args, **kwargs)
        return builtin_open(*args, **kwargs)

    @mock.patch("builtins.open", mock_open)
    @responses.activate
    def test_apply_dau_config(self):
        param = {
            'converters': [],
            'dauConfig': [
                {'column': 'col1', 'mapping': 1},
                {'column': 'col2', 'mapping': 2},
                {'column': 'col3', 'mapping': 3},
            ]
        }
        return_value = [
            {"id": 1, "installNo": "test1"},
            {"id": 2, "installNo": "test2"},
            {"id": 3, "installNo": "test3"}
        ]
        responses.add(
            responses.GET,
            "http://fake_server/dau/ids",
            json=return_value,
            status=200
        )

        data = GeneratorConfigRequest(**param)
        loader = LoadCsvFile(test_file)
        loader.load_data(data)
        assert len(loader.data) > 0
        columns = loader.data.columns
        assert 'test1' in columns
        assert 'test2' in columns
        assert 'test3' in columns
        assert 'col1' not in columns
        assert 'col2' not in columns
        assert 'col3' not in columns

        loader_origin = LoadCsvFile(test_file)
        param = {'converters': [], 'dauConfig': []}
        data = GeneratorConfigRequest(**param)
        loader_origin.load_data(data)
        columns_origin = loader_origin.data.columns
        assert len(columns) == len(columns_origin)
        assert 'col1' in columns_origin
        assert 'col2' in columns_origin
        assert 'col3' in columns_origin

        assert loader.data['test1'].equals(loader_origin.data['col1'])
        assert loader.data['test2'].equals(loader_origin.data['col2'])
        assert loader.data['test3'].equals(loader_origin.data['col3'])
