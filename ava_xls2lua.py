#! /usr/bin/env python
# -*- coding: utf-8 -*
# description: A tool to convert excel files to lua, according to Ava framework
# git repo: https://github.com/lilith-avatar/avatar-ava-xls2lua
# forked from: https://github.com/luzexi/xls2lua
# Ava framework: https://github.com/lilith-avatar/avatar-ava

import os
import os.path
import time
import sys
import datetime
import codecs
import xlrd
import subprocess
import json

__authors__ = ["zfengzhen", "luzexi", "Yuancheng Zhang"]
__copyright__ = "Copyright 2020, Lilith Games, Project DaVinci, Avatar Team"
__credits__ = ["zfengzhen", "luzexi", "Yuancheng Zhang"]
__license__ = "MIT"
__version__ = "1.1"
__maintainer__ = "Yuancheng Zhang"
__status__ = "Development"

INPUT_FOLDER = './xls'
OUTPUT_FOLDER = './code'
OUTPUT_LUA_TEMPLATE = "['World']['Global']['Xls']['{sheet_name}XlsModule'].ModuleScript.lua"

INFO = '[\033[36minfo\033[0m] '
ERROR = '[\033[31merror\033[0m] '
SUCCESS = '[\033[92msucess\033[0m] '
FAILED = '[\033[91mfailed\033[0m] '

SCRIPT_HEAD = '''--- This file is generated by ava-xls2lua.py,
--- Don't change it manaully.\
--- @copyright Lilith Games, Project Da Vinci(Avatar Team)
--- @see https://www.projectdavinci.com/
--- source file: %s

'''

INT, FLOAT, STRING, BOOL = r"int", r"float", r"string", r"bool"
INT_ARR, FLOAT_ARR, STRING_ARR, BOOL_ARR = r"int[]", r"float[]", r"string[]", r"bool[]"
VECTOR2, VECTOR3, EULER, COLOR = 'vector2', 'vector3', 'euler', 'color'

CONFIG_FILE = '.ava-x2l-config.json'

gui = None
lua_cnt = 0
max_xls_name_len = 0


def make_table(filename):
    if not os.path.isfile(filename):
        raise NameError('%s is	not	a valid	filename' % filename)
    book_xlrd = xlrd.open_workbook(filename, formatting_info=True)
    # book_xlrd = xlrd.open_workbook(filename)

    excel = {}
    excel = {}
    excel['filename'] = filename
    excel['data'] = {}
    excel['meta'] = {}

    for sheet in book_xlrd.sheets():
        sheet_name = sheet.name.replace(' ', '_')
        if not sheet_name.startswith('output_'):
            continue
        sheet_name = sheet_name[7:]
        # log(sheet_name +' sheet')
        excel['data'][sheet_name] = {}
        excel['meta'][sheet_name] = {}

        # 必须大于2行
        if sheet.nrows <= 2:
            return {}, -1, 'sheet[' + sheet_name + ']' + ' rows must > 2'

        # 解析标题
        title = {}
        col_idx = 0
        for col_idx in range(sheet.ncols):
            value = sheet.cell_value(0, col_idx)
            vtype = sheet.cell_type(0, col_idx)
            if vtype != xlrd.XL_CELL_TEXT:
                return {}, -1, 'title columns[' + str(col_idx) + '] must be string'
            title[col_idx] = str(value).replace(' ', '_')

        excel['meta'][sheet_name]['title'] = title

        row_idx = 1
        # 类型解析
        type_dict = {}
        col_idx = 0
        for col_idx in range(sheet.ncols):
            value = sheet.cell_value(1, col_idx)
            vtype = sheet.cell_type(1, col_idx)
            type_dict[col_idx] = str(value)
            if (type_dict[col_idx].lower() != INT
                    and type_dict[col_idx].lower() != FLOAT
                    and type_dict[col_idx].lower() != STRING
                    and type_dict[col_idx].lower() != BOOL
                    and type_dict[col_idx].lower() != INT_ARR
                    and type_dict[col_idx].lower() != FLOAT_ARR
                    and type_dict[col_idx].lower() != STRING_ARR
                    and type_dict[col_idx].lower() != BOOL_ARR
                    and type_dict[col_idx].lower() != VECTOR2
                    and type_dict[col_idx].lower() != VECTOR3
                    and type_dict[col_idx].lower() != EULER
                    and type_dict[col_idx].lower() != COLOR):
                return {}, -1, 'sheet[{}] row[{}] column[{}] type wrong'.format(sheet_name, row_idx, col_idx)

        if type_dict[0].lower() != INT:
            return {}, -1, 'sheet[' + sheet_name + ']' + ' first column type must be [i]'

        excel['meta'][sheet_name]['type'] = type_dict

        row_idx = 2
        # 数据从第3行开始
        for row_idx in range(2, sheet.nrows):
            row = {}

            col_idx = 0
            for col_idx in range(sheet.ncols):
                value = sheet.cell_value(row_idx, col_idx)
                vtype = sheet.cell_type(row_idx, col_idx)
                # 本行有数据
                v = None
                if type_dict[col_idx].lower() == INT and vtype == xlrd.XL_CELL_NUMBER:
                    v = int(value)
                elif type_dict[col_idx].lower() == FLOAT and vtype == xlrd.XL_CELL_NUMBER:
                    v = float(value)
                elif type_dict[col_idx].lower() == STRING:
                    v = format_str(value)
                elif type_dict[col_idx].lower() == BOOL and vtype == xlrd.XL_CELL_BOOLEAN:
                    if value == 1:
                        v = 'true'
                    else:
                        v = 'false'
                elif type_dict[col_idx].lower() == INT_ARR and vtype == xlrd.XL_CELL_TEXT:
                    v = str(value)
                elif type_dict[col_idx].lower() == FLOAT_ARR and vtype == xlrd.XL_CELL_TEXT:
                    v = str(value)
                elif type_dict[col_idx].lower() == STRING_ARR:
                    v = format_str(value)
                elif type_dict[col_idx].lower() == BOOL_ARR and vtype == xlrd.XL_CELL_TEXT:
                    v = str(value)
                elif type_dict[col_idx].lower() == VECTOR2 and vtype == xlrd.XL_CELL_TEXT:
                    v = str(value)
                elif type_dict[col_idx].lower() == VECTOR3 and vtype == xlrd.XL_CELL_TEXT:
                    v = str(value)
                elif type_dict[col_idx].lower() == EULER and vtype == xlrd.XL_CELL_TEXT:
                    v = str(value)
                elif type_dict[col_idx].lower() == COLOR and vtype == xlrd.XL_CELL_TEXT:
                    v = str(value)
                row[col_idx] = v

            excel['data'][sheet_name][row[0]] = row

    return excel, 0, 'ok'


def format_str(v):
    if type(v) == int or type(v) == float:
        v = str(v)
    s = v
    s = v.replace('\"', '\\\"')
    s = s.replace('\'', '\\\'')
    return s


def get_int(v):
    if v is None:
        return 0
    return v


def get_float(v):
    if v is None:
        return 0
    return v


def get_string(v):
    if v is None:
        return ''
    return v


def get_bool(v):
    if v is None:
        return 'false'
    return v


def get_int_arr(v):
    if v is None:
        return '{}'
    tmp_vec_str = v.split(',')
    res_str = '{'
    i = 0
    for val in tmp_vec_str:
        if val != None and val != '':
            if i != 0:
                res_str += ', '
            res_str = res_str + val
            i += 1
    res_str += '}'
    return res_str


def get_float_arr(v):
    if v is None:
        return '{}'
    tmp_vec_str = v.split(',')
    res_str = '{'
    i = 0
    for val in tmp_vec_str:
        if val != None and val != '':
            if i != 0:
                res_str += ', '
            res_str = res_str + val
            i += 1
    res_str += '}'
    return res_str


def get_string_arr(v):
    if v is None:
        return '{}'
    tmp_vec_str = v.split(',')
    res_str = '{'
    i = 0
    for val in tmp_vec_str:
        if val != None and val != '':
            if i != 0:
                res_str += ', '
            res_str = res_str + '\'' + val + '\''
            i += 1
    res_str += '}'
    return res_str


def get_bool_arr(v):
    if v is None:
        return '{}'
    tmp_vec_str = v.split(',')
    res_str = '{'
    i = 0
    for val in tmp_vec_str:
        if val != None and val != '':
            if i != 0:
                res_str += ', '
            res_str = res_str + val.lower()
            i += 1
    res_str += '}'
    return res_str


def get_vector2(v):
    if v is None:
        return 'Vector2.Zero'
    tmp_vec_str = v.split(',')
    if len(tmp_vec_str) != 2:
        # todo: error check
        return 'Vector2.Zero'
    res_str = 'Vector2('
    i = 0
    for val in tmp_vec_str:
        if val != None and val != '':
            if i != 0:
                res_str += ', '
            res_str = res_str + val.lower()
            i += 1
    res_str += ')'
    return res_str


def get_vector3(v):
    if v is None:
        return 'Vector3.Zero'
    tmp_vec_str = v.split(',')
    if len(tmp_vec_str) != 3:
        # todo: error check
        return 'Vector3.Zero'
    res_str = 'Vector3('
    i = 0
    for val in tmp_vec_str:
        if val != None and val != '':
            if i != 0:
                res_str += ', '
            res_str = res_str + val.lower()
            i += 1
    res_str += ')'
    return res_str


def get_euler(v):
    if v is None:
        return 'EulerDegree(0, 0, 0)'
    tmp_vec_str = v.split(',')
    if len(tmp_vec_str) != 3:
        # todo: error check
        return 'EulerDegree(0, 0, 0)'
    res_str = 'EulerDegree('
    i = 0
    for val in tmp_vec_str:
        if val != None and val != '':
            if i != 0:
                res_str += ', '
            res_str = res_str + val.lower()
            i += 1
    res_str += ')'
    return res_str


def get_color(v):
    if v is None:
        return 'Color(0, 0, 0, 0)'
    tmp_vec_str = v.split(',')
    if len(tmp_vec_str) != 4:
        # todo: error check
        return 'Color(0, 0, 0, 0)'
    res_str = 'Color('
    i = 0
    for val in tmp_vec_str:
        if val != None and val != '':
            if i != 0:
                res_str += ', '
            res_str = res_str + val.lower()
            i += 1
    res_str += ')'
    return res_str


def write_to_lua_script(excel, output_path, xls_file):
    for (sheet_name, sheet) in excel['data'].items():
        file_name = OUTPUT_LUA_TEMPLATE.format(sheet_name=sheet_name)
        suffix = 'Xls'
        outfp = codecs.open(output_path + '/' + file_name, 'w', "utf-8")
        outfp.write(SCRIPT_HEAD % (excel['filename']))
        outfp.write('local ' + sheet_name + suffix + ' = {\n')
        title = excel['meta'][sheet_name]['title']
        type_dict = excel['meta'][sheet_name]['type']
        for (row_idx, row) in sheet.items():
            outfp.write('    [' + str(row_idx) + '] = {\n')
            for (col_idx, field) in row.items():
                if type_dict[col_idx].lower() == INT:
                    tmp_str = get_int(row[col_idx])
                    outfp.write(
                        '        ' + str(title[col_idx]) + ' = ' + str(tmp_str))
                elif type_dict[col_idx].lower() == FLOAT:
                    tmp_str = get_float(row[col_idx])
                    outfp.write(
                        '        ' + str(title[col_idx]) + ' = ' + str(tmp_str))
                elif type_dict[col_idx].lower() == STRING:
                    tmp_str = get_string(row[col_idx])
                    outfp.write(
                        '        ' + str(title[col_idx]) + ' = \'' + str(tmp_str) + '\'')
                elif type_dict[col_idx].lower() == BOOL:
                    tmp_str = get_bool(row[col_idx])
                    outfp.write(
                        '        ' + str(title[col_idx]) + ' = ' + str(tmp_str))
                elif type_dict[col_idx].lower() == INT_ARR:
                    tmp_str = get_int_arr(row[col_idx])
                    outfp.write(
                        '        ' + str(title[col_idx]) + ' = ' + str(tmp_str))
                elif type_dict[col_idx].lower() == FLOAT_ARR:
                    tmp_str = get_float_arr(row[col_idx])
                    outfp.write(
                        '        ' + str(title[col_idx]) + ' = ' + str(tmp_str))
                elif type_dict[col_idx].lower() == STRING_ARR:
                    tmp_str = get_string_arr(row[col_idx])
                    outfp.write(
                        '        ' + str(title[col_idx]) + ' = ' + str(tmp_str))
                elif type_dict[col_idx].lower() == BOOL_ARR:
                    tmp_str = get_bool_arr(row[col_idx])
                    outfp.write(
                        '        ' + str(title[col_idx]) + ' = ' + str(tmp_str))
                elif type_dict[col_idx].lower() == VECTOR2:
                    tmp_str = get_vector2(row[col_idx])
                    outfp.write(
                        '        ' + str(title[col_idx]) + ' = ' + str(tmp_str))
                elif type_dict[col_idx].lower() == VECTOR3:
                    tmp_str = get_vector3(row[col_idx])
                    outfp.write(
                        '        ' + str(title[col_idx]) + ' = ' + str(tmp_str))
                elif type_dict[col_idx].lower() == EULER:
                    tmp_str = get_euler(row[col_idx])
                    outfp.write(
                        '        ' + str(title[col_idx]) + ' = ' + str(tmp_str))
                elif type_dict[col_idx].lower() == COLOR:
                    tmp_str = get_color(row[col_idx])
                    outfp.write(
                        '        ' + str(title[col_idx]) + ' = ' + str(tmp_str))
                else:
                    outfp.close()
                    raise RuntimeError(
                        'type "{}" is wrong.'.format(type_dict[col_idx]))

                if col_idx == len(row.items()) - 1:
                    outfp.write('\n')
                else:
                    outfp.write(',\n')

            if row_idx == len(sheet.items()):
                outfp.write('    }\n')
            else:
                outfp.write('    },\n')
        outfp.write('}\n\nreturn ' + sheet_name + suffix + '\n')
        outfp.close()
        global lua_cnt
        lua_cnt += 1
        log(SUCCESS + '[{{0:02d}}] {{1:{0}}} => {{2}}'.format(max_xls_name_len).format(lua_cnt,
                                                                                       xls_file, file_name))


def load_config():
    # todo: load config files
    global INPUT_FOLDER, OUTPUT_FOLDER, OUTPUT_LUA_TEMPLATE
    if not os.path.isfile(CONFIG_FILE):
        log(INFO + 'generate config:\t{}'.format(CONFIG_FILE))
        default_config = {'input_folder': INPUT_FOLDER,
                          'output_folder': OUTPUT_FOLDER,
                          'output_lua_template': OUTPUT_LUA_TEMPLATE
                          }
        with open(CONFIG_FILE, 'w') as json_file:
            json_file.write(json.dumps(default_config, indent=True))
            json_file.close()
            subprocess.check_call(['attrib', '+H', CONFIG_FILE])

    with open(CONFIG_FILE) as json_file:
        config = json.load(json_file)
        INPUT_FOLDER = config['input_folder']
        OUTPUT_FOLDER = config['output_folder']
        OUTPUT_LUA_TEMPLATE = config['output_lua_template']


def main():
    global lua_cnt
    lua_cnt = 0
    input_path = INPUT_FOLDER
    output_path = OUTPUT_FOLDER
    log(INFO + 'input path: \t{}'.format(input_path))
    log(INFO + 'output path: \t{}'.format(output_path))
    if not os.path.exists(input_path):
        raise RuntimeError('input path does NOT exist.')
    if not os.path.exists(output_path):
        os.mkdir(output_path)
        log(INFO + 'make a new dir: \t{}'.format(output_path))

    xls_files = os.listdir(input_path)
    if len(xls_files) == 0:
        raise RuntimeError('input dir is empty.')

    # find max string len
    global max_xls_name_len
    max_xls_name_len = len(max(xls_files, key=len))

    # filer files by .xls
    xls_files = [x for x in xls_files if '.xls' in x[-4:]]
    log(INFO + 'total XLS: \t{}'.format(len(xls_files)))

    for i in range(len(xls_files)):
        xls_file = xls_files[i]
        t, ret, errstr = make_table(INPUT_FOLDER + '/' + xls_file)
        if ret != 0:
            log(FAILED + '[{}] {}'.format(i + 1, xls_file))
            raise RuntimeError(errstr)
        else:
            # TODO 改成lua名字
            write_to_lua_script(t, output_path, xls_file)


def run():
    try:
        log(INFO +
            'time: \t\t{0:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()))
        load_config()
        main()
        global lua_cnt
        log(INFO + 'total Lua: \t{}'.format(lua_cnt))
        log(INFO + 'done.')
        if gui is None:
            log(INFO + 'press Enter to exit...')
            input()
    except RuntimeError as err:
        log(ERROR + str(err))
        if gui is None:
            log(INFO + 'check error please...')
            input()


def set_gui(frame):
    global gui
    if frame is not None:
        gui = frame
        global INFO, ERROR, SUCCESS, FAILED
        INFO = '[info] '
        ERROR = '[error] '
        SUCCESS = '[sucess] '
        FAILED = '[failed] '
    else:
        log(ERROR + 'frame is None.')


def log(s):
    if gui is not None:
        gui.write(s)
    else:
        print(s)


if __name__ == '__main__':
    run()
