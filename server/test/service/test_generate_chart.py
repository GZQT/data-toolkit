import os.path
import shutil
from unittest import mock
from conf_test_db import override_get_db
from dto.generator import TaskGeneratorStartRequest
from schema.task import TaskGenerator, Task
from service.chart_generator import generate_chart

chart_param = {
    "generate": True,
    "column_index": [],
    "time_range": '1S',
    "x_label": "test_x",
    "y_label": "test_y",
    "x_rotation": 45,
    "name": [],
    "fill": "LINE",
    "line_width": 0.65,
    "show_grid": True
}
no_chart_param = {
    "generate": False,
    "column_index": [],
    "time_range": '1S',
    "x_label": "test_x",
    "y_label": "test_y",
    "x_rotation": 45,
    "name": [],
    "fill": None,
    "line_width": 0.65,
    "show_grid": True
}
request_template = {
    'average_line_chart': no_chart_param,
    'max_min_line_chart': no_chart_param,
    'root_mean_square_line_chart': no_chart_param,
    'raw_line_chart': no_chart_param,
    'config': None,
    'average_bar_chart': False,
    'max_min_bar_chart': False,
    'average_data_table': False,
    'max_min_data_table': False,
    'root_mean_square_data_table': False,
    'raw_data_table': False,
    'average_bar_group': [],
    'max_min_bar_group': [],
}

current_file_path = os.path.abspath(__file__)
current_tmp = os.path.abspath(os.path.join(os.path.dirname(current_file_path), 'tmp'))


class TestGenerateChart:

    def setup_class(self):
        if not os.path.exists(current_tmp):
            os.makedirs(current_tmp)
        else:
            shutil.rmtree(current_tmp)
            os.makedirs(current_tmp)

        self.database = next(override_get_db())
        self.database.add(Task(name="test_task"))
        self.database.commit()
        self.database.add(
            TaskGenerator(name="test_generate",
                          files=f"{os.path.abspath(os.path.join(os.path.dirname(current_file_path), 'test.csv'))}",
                          task_id=1))
        self.database.commit()

    def _test_generate_chart(self, param, chart_type):
        data = self.database.query(TaskGenerator).filter_by(name="test_generate").one()
        assert data.id > 0

        chart_path = os.path.join(current_tmp, "test_generate", f"{chart_type}折线图")
        if os.path.exists(chart_path):
            shutil.rmtree(chart_path)

        generate_chart(data, TaskGeneratorStartRequest(**param), self.database)

        data = self.database.query(TaskGenerator).filter_by(name="test_generate").one()
        assert data.result == '生成成功'
        chart_list = os.listdir(chart_path)
        for i in range(15):
            assert f"col{i + 1}{'' if chart_type == '原始值' else chart_type}时程曲线图.png" in chart_list

    @mock.patch('constant.ROOT_DIRECTORY', current_tmp)
    def test_generate_average_line_chart(self):
        request_dict = request_template
        request_dict['average_line_chart'] = chart_param
        self._test_generate_chart(request_dict, "平均值")

    @mock.patch('constant.ROOT_DIRECTORY', current_tmp)
    def test_generate_root_square_line_chart(self):
        request_dict = request_template
        request_dict['root_mean_square_line_chart'] = chart_param
        self._test_generate_chart(request_dict, "均方根")

    @mock.patch('constant.ROOT_DIRECTORY', current_tmp)
    def test_generate_min_max_line_chart(self):
        request_dict = request_template
        request_dict['max_min_line_chart'] = chart_param
        self._test_generate_chart(request_dict, "最大最小值")

    @mock.patch('constant.ROOT_DIRECTORY', current_tmp)
    def test_generate_raw_line_chart(self):
        request_dict = request_template
        request_dict['raw_line_chart'] = chart_param
        self._test_generate_chart(request_dict, "原始值")

    @mock.patch('constant.ROOT_DIRECTORY', current_tmp)
    def test_generate_average_data_table(self):
        request_dict = request_template
        request_dict["average_data_table"] = True
