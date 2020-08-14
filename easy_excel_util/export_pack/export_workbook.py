# !user/bin/env python3
# -*- coding: utf-8 -*-
# Author: ChaoqiYin
import xlwt

from .export_row import ExportRow
from .export_sheet import ExportSheet
from .sheet_map import SheetMap


class ExportWorkBook(object):
    def __init__(self, file_path_or_stream, converters):
        self.file_path = file_path_or_stream  # 文件路径
        self.converters = converters  # 转换类
        self.sync = True  # 是否为同步模式
        self.max_workers = 3  # 异步最大线程数
        self.style = None  # 单元格样式
        self.sheet_map = None  # 表索引: [表名, parse_map, list_data]关系

    def set_style(self, style):
        '''
        设置单元格样式
        :param style:
        :return:
        '''
        self.style = style

    def __check_sheet_map_index_unique(self, index):
        if index in self.sheet_map:
            raise Exception("the index {index} of sheet_map is not unique".format(index=index))

    def _check_map_index_unique(self, parse_map):
        '''
        验证index是否唯一
        :param parse_map:
        :return:
        '''
        index_list = []
        for field_name, build_field in parse_map.items():
            # 设置field的自身__name属性
            build_field.name = field_name
            if build_field.index in index_list:
                raise Exception("the index {index} of field '{name}' is not unique".format(index=build_field.index, name=field_name))
            index_list.append(build_field.index)

    def thread(self, max_workers):
        '''
        开启多线程模式
        :param max_workers 最大线程数
        :return:
        '''
        self.sync = False
        self.max_workers = max_workers
        return self

    def set_sheet_map(self, index, data, parse_map, sheet_name=None, title_style=None):
        '''
        设置sheet对应map
        :param index: sheet索引
        :param parse_map: 解析map
        :param data: 数据
        :param sheet_name: 表名
        :param title_style: 标题样式
        :return:
        '''
        if self.sheet_map is None:
            self.sheet_map = {}
        self.__check_sheet_map_index_unique(index)
        self._check_map_index_unique(parse_map)
        rel_sheet_name = 'sheet_' + str(index) if sheet_name is None else sheet_name
        self.sheet_map[index] = SheetMap(rel_sheet_name, parse_map, data, title_style)
        return self

    def validate_before_action(self):
        if self.file_path is None:
            raise Exception("file_path can't all be None!")
        if self.sheet_map is None:
            raise Exception("sheet_map can't be None!")

    def sort_sheet_map(self):
        keys = list(self.sheet_map.keys())
        keys.sort(reverse=False)
        new_map = {}
        for key in keys:
            new_map[key] = self.sheet_map[key]
        self.sheet_map = new_map

    def do_export(self, row_del_class=None, row_validate_func=None):
        rel_row_del_class = ExportRow if row_del_class is None else row_del_class
        self.validate_before_action()
        # 创建一个workbook 设置编码
        workbook = xlwt.Workbook(encoding='utf-8')
        # 升序排序
        self.sort_sheet_map()
        for index, sheet_info in self.sheet_map.items():
            sheet = ExportSheet(self, workbook, rel_row_del_class, row_validate_func, index, sheet_info)
            sheet.parse_export()
        workbook.save(self.file_path)  # file_path可能会是stream，这里因为使用了父类变量，没法改变量名
