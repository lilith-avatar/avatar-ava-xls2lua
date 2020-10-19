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
import xlwt
from xlutils.copy import copy
import subprocess
import json

__authors__ = ['zfengzhen', 'luzexi', 'Yuancheng Zhang']
__copyright__ = 'Copyright 2020, Lilith Games, Project DaVinci, Avatar Team'
__credits__ = ['zfengzhen', 'luzexi', 'Yuancheng Zhang']
__license__ = 'MIT'
__version__ = '2.3.1'
__maintainer__ = 'Yuancheng Zhang'
__status__ = 'Development'

INPUT_FOLDER = './xls'
OUTPUT_FOLDER = './code'
OUTPUT_LUA_TEMPLATE = "['World']['Global']['Xls']['{sheet_name}XlsModule'].ModuleScript.lua"
KV_XLS = ['GlobalSetting.xlsx']
TRANSLATE_XLS = 'LanguagePack.xls'

INFO = '\033[36minfo\033[0m'
ERROR = '\033[31merror\033[0m'
SUCCESS = '\033[92msucess\033[0m'
FAILED = '\033[91mfailed\033[0m'

SCRIPT_HEAD = '''--- This file is generated by ava-x2l.exe,
--- Don't change it manaully.
--- @copyright Lilith Games, Project Da Vinci(Avatar Team)
--- @see https://www.projectdavinci.com/
--- @see https://github.com/endaye/avatar-ava-xls2lua
--- source file: %s

'''

# data type
INT, FLOAT, STRING, BOOL = r"int", r"float", r"string", r"bool"
INT_ARR, FLOAT_ARR, STRING_ARR, BOOL_ARR = r"int[]", r"float[]", r"string[]", r"bool[]"
VECTOR2, VECTOR3, EULER, COLOR = 'vector2', 'vector3', 'euler', 'color'
LUA, COMMENT, TRANSLATE = 'lua', 'comment', 'translate'

CONFIG_FILE = '.ava-x2l-config.json'

KEY_1, KEY_2, KEY_3 = 'key1', 'key2', 'key3'

gui = None
lua_cnt = 0
max_xls_name_len = 0
g_lang_kv = {}


def make_table(filename):
    if not os.path.isfile(filename):
        raise NameError('%s is	not	a valid	filename' % filename)
    book_xlrd = xlrd.open_workbook(filename)

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
        data = excel['data'][sheet_name] = {}
        meta = excel['meta'][sheet_name] = {}

        # 必须大于4行
        if sheet.nrows < 4:
            return {}, -1, 'sheet[{}] rows must > 4'.format(sheet_name)

        # 解析标题和类型
        col_idx = 1
        type_dict = {}
        for col_idx in range(sheet.ncols):
            title = str(sheet.cell_value(1, col_idx)).replace(' ', '_')
            title_type = sheet.cell_type(1, col_idx)
            type_name = str(sheet.cell_value(2, col_idx)).lower()
            type_type = sheet.cell_type(2, col_idx)
            # 检查标题数据格式
            if not title:
                return {}, -1, 'sheet[{}] title columns[{}] must be string'.format(sheet_name, col_idx + 1)
            if title_type != xlrd.XL_CELL_TEXT:
                return {}, -1, 'sheet[{}] title columns[{}] must be string'.format(sheet_name, col_idx + 1)
            # 检查类型数据格式
            if type_type != xlrd.XL_CELL_TEXT:
                return {}, -1, 'sheet[{}] type columns[{}] must be string'.format(sheet_name, col_idx + 1)
            if (type_name != INT
                and type_name != FLOAT
                and type_name != STRING
                and type_name != BOOL
                and type_name != INT_ARR
                and type_name != FLOAT_ARR
                and type_name != STRING_ARR
                and type_name != BOOL_ARR
                and type_name != VECTOR2
                and type_name != VECTOR3
                and type_name != EULER
                and type_name != COLOR
                and type_name != COMMENT
                and type_name != LUA
                and type_name != TRANSLATE
                ):
                return {}, -1, 'sheet[{}] type column[{}] type wrong'.format(sheet_name, col_idx + 1)
            type_dict[title] = type_name

        meta['type_dict'] = type_dict

        # *读取主键key1，key2，key3，主键类型必须是Int或者String
        row_idx, col_idx = 3, 0
        for col_idx in range(sheet.ncols):
            key = sheet.cell_value(row_idx, col_idx).lower()
            col_name = sheet.cell_value(1, col_idx)
            col_type = sheet.cell_value(2, col_idx).lower()
            if key in (KEY_1, KEY_2, KEY_3):
                if col_type not in (INT, STRING):
                    return {}, -1, 'sheet[{}] {} type must be Int or Float'.format(sheet_name, key)
                meta[key] = col_name

        # 检查主键
        if (KEY_3 in meta and not (KEY_2 in meta and KEY_1 in meta)) or (KEY_2 in meta and KEY_1 not in meta) or (KEY_1 not in meta):
            return {}, -1, 'sheet[{}] {} {} {} are wrong'.format(sheet_name, KEY_1, KEY_2, KEY_3)

        key1 = meta[KEY_1] if KEY_1 in meta else None
        key2 = meta[KEY_2] if KEY_2 in meta else None
        key3 = meta[KEY_3] if KEY_3 in meta else None

        # 读取数据，从第5行开始
        row_idx = 4
        for row_idx in range(row_idx, sheet.nrows):
            row = {}
            key_v1, key_v3, key_v2 = None, None, None
            lang_kv = {}

            for col_idx in range(sheet.ncols):
                title = sheet.cell_value(1, col_idx)
                value = sheet.cell_value(row_idx, col_idx)
                vtype = sheet.cell_type(row_idx, col_idx)
                # 本行有数据
                v = None
                if type_dict[title] == INT and vtype == xlrd.XL_CELL_NUMBER:
                    v = int(value)
                elif type_dict[title] == FLOAT and vtype == xlrd.XL_CELL_NUMBER:
                    v = float(value)
                elif type_dict[title] == STRING:
                    v = format_str(value)
                elif type_dict[title] == BOOL and vtype == xlrd.XL_CELL_BOOLEAN:
                    v = 'true' if value == 1 else 'false'
                elif type_dict[title] == INT_ARR and vtype == xlrd.XL_CELL_TEXT:
                    v = str(value)
                elif type_dict[title] == FLOAT_ARR and vtype == xlrd.XL_CELL_TEXT:
                    v = str(value)
                elif type_dict[title] == STRING_ARR:
                    v = format_str(value)
                elif type_dict[title] == BOOL_ARR and vtype == xlrd.XL_CELL_TEXT:
                    v = str(value)
                elif type_dict[title] == VECTOR2 and vtype == xlrd.XL_CELL_TEXT:
                    v = str(value)
                elif type_dict[title] == VECTOR3 and vtype == xlrd.XL_CELL_TEXT:
                    v = str(value)
                elif type_dict[title] == EULER and vtype == xlrd.XL_CELL_TEXT:
                    v = str(value)
                elif type_dict[title] == COLOR and vtype == xlrd.XL_CELL_TEXT:
                    v = str(value)
                elif type_dict[title] == LUA and vtype in (xlrd.XL_CELL_TEXT, xlrd.XL_CELL_NUMBER):
                    v = str(value)
                elif type_dict[title] == LUA and vtype == xlrd.XL_CELL_BOOLEAN:
                    v = 'true' if value == 1 else 'false'
                elif type_dict[title] == TRANSLATE and vtype == xlrd.XL_CELL_TEXT:
                    v = str(value)
                    lang_kv[title] = '{}_{}_'.format(sheet_name, title)
                elif type_dict[title] == COMMENT:
                    continue

                row[title] = v

                if title == key1:
                    key_v1 = v
                if title == key2:
                    key_v2 = v
                if title == key3:
                    key_v3 = v

                # TODO: 检查key_v1是类型是string的话，不能为数字，需要符合lua命名规范

            # 键值检查
            if key1 and key2 and key3:
                if key_v1 not in data:
                    data[key_v1] = {}
                if key_v2 not in data[key_v1]:
                    data[key_v1][key_v2] = {}
                if not key_v3:
                    return {}, -1, 'sheet[{}][{}] {} data "{}" is empty'.format(sheet_name, row_idx + 1, KEY_3, key3)
                elif key_v3 in data[key_v1][key_v2]:
                    return {}, -1, 'sheet[{}][{}] {} data "{}" is duplicated'.format(sheet_name, row_idx + 1, KEY_3, key3)
                else:
                    data[key_v1][key_v2][key_v3] = row
                    lang_suffix = '{}_{}_{}'.format(key_v1, key_v2, key_v3)
            elif key1 and key2:
                if key_v1 not in data:
                    data[key_v1] = {}
                if not key_v2:
                    return {}, -1, 'sheet[{}][{}] {} data "{}" is empty'.format(sheet_name, row_idx + 1, KEY_2, key2)
                elif key_v2 in data[key_v1]:
                    return {}, -1, 'sheet[{}][{}] {} data "{}" is duplicated'.format(sheet_name, row_idx + 1, KEY_2, key2)
                else:
                    data[key_v1][key_v2] = row
                    lang_suffix = '{}_{}'.format(key_v1, key_v2)
            elif key1:
                if not key_v1:
                    return {}, -1, 'sheet[{}][{}] {} data "{}" is empty'.format(sheet_name, row_idx + 1, KEY_1, key1)
                elif key_v1 in data:
                    return {}, -1, 'sheet[{}][{}] {} data "{}" is duplicated'.format(sheet_name, row_idx + 1, KEY_1, key1)
                else:
                    data[key_v1] = row
                    lang_suffix = str(key_v1)
            for k, v in lang_kv.items():
                lang_id = v + lang_suffix
                g_lang_kv[lang_id] = row[k]
                row[k] = lang_id

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
    return '\'' + v + '\''


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
    if not v:
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


def get_lua(v):
    if not v:
        return 'nil'
    return v


def get_lang(v):
    return get_string(v)


def update_translate_xls(filename):
    if not os.path.isfile(filename):
        raise NameError('%s is	not	a valid	filename' % filename)
    book_xlrd = xlrd.open_workbook(filename)
    book_xlwt = copy(book_xlrd)
    for sheet in book_xlrd.sheets():
        sheet_name = sheet.name.replace(' ', '_')
        sheet_edit = book_xlwt.get_sheet(sheet_name)
        if not sheet_name.startswith('output_'):
            continue
        if sheet.nrows < 4:
            raise NameError('sheet[{}] rows must > 4'.format(sheet_name))
        row_idx = 4
        exist_lang_ids = []
        for row_idx in range(row_idx, sheet.nrows):
            lang_id = sheet.cell_value(row_idx, 0)
            lang_chs = sheet.cell_value(row_idx, 1)
            exist_lang_ids.append(lang_id)
            if lang_id in g_lang_kv:
                # TODO: write cell data
                sheet_edit.write(row_idx, 0, lang_id)
                sheet_edit.write(row_idx, 1, g_lang_kv[lang_id])

        # new lang ids
        new_row_idx = sheet.nrows
        for lang_id, lang_chs in g_lang_kv.items():
            if lang_id not in exist_lang_ids:
                sheet_edit.write(new_row_idx, 0, lang_id)
                sheet_edit.write(new_row_idx, 1, lang_chs)
                new_row_idx += 1
    book_xlwt.save(filename)


def write_to_lua_script(excel, output_path, xls_file):
    for (sheet_name, sheet) in excel['data'].items():
        meta = excel['meta'][sheet_name]
        type_dict = meta['type_dict']
        key1 = meta[KEY_1] if KEY_1 in meta else None
        key2 = meta[KEY_2] if KEY_2 in meta else None
        key3 = meta[KEY_3] if KEY_3 in meta else None

        file_name = OUTPUT_LUA_TEMPLATE.format(sheet_name=sheet_name)
        suffix = 'Xls'
        outfp = codecs.open(output_path + '/' + file_name, 'w', "utf-8")
        outfp.write(SCRIPT_HEAD % (excel['filename']))
        outfp.write('local ' + sheet_name + suffix + ' = {\r\n')

        if key1 and key2 and key3:
            write_to_lua_key(sheet, [key1, key2, key3], type_dict, outfp, 1)
        elif key1 and key2:
            write_to_lua_key(sheet, [key1, key2], type_dict, outfp, 1)
        elif key1 and (xls_file not in KV_XLS):
            write_to_lua_key(sheet, [key1], type_dict, outfp, 1)
        elif key1:
            write_to_lua_kv(sheet, [key1], type_dict, outfp, 1)
        else:
            outfp.close()
            raise RuntimeError('key missing')

        outfp.write('}\r\n\r\nreturn ' + sheet_name + suffix + '\r\n')
        outfp.close()
        global lua_cnt
        lua_cnt += 1
        log(SUCCESS, '[{{0:02d}}] {{1:{0}}} => {{2}}'
            .format(max_xls_name_len).format(lua_cnt, xls_file, file_name))


def write_to_lua_key(data, keys, type_dict, outfp, depth):
    cnt = 0
    keyX = keys[depth - 1]
    indent = get_indent(depth)
    prefix = '[{}] = {{\r\n' if type_dict[keyX] == INT else '{} = {{\r\n'
    suffix_comma = '},\r\n'
    suffix_end = '}\r\n'

    prefix = indent + prefix
    suffix_comma = indent + suffix_comma
    suffix_end = indent + suffix_end

    for (key, value) in data.items():
        outfp.write(prefix.format(key))
        if depth == len(keys):
            write_to_lua_row(value, type_dict, outfp, depth + 1)
        else:
            write_to_lua_key(value, keys, type_dict,
                             outfp, depth + 1)
        cnt += 1
        outfp.write(suffix_end if cnt == len(data) else suffix_comma)


def write_to_lua_row(row, type_dict, outfp, depth):
    cnt = 0
    indent = get_indent(depth)
    for (key, value) in row.items():
        if type_dict[key] == INT:
            outfp.write('{}{} = {}'.format(indent, key, get_int(value)))
        elif type_dict[key] == FLOAT:
            outfp.write('{}{} = {}'.format(indent, key, get_float(value)))
        elif type_dict[key] == STRING:
            outfp.write('{}{} = {}'.format(indent, key, get_string(value)))
        elif type_dict[key] == BOOL:
            outfp.write('{}{} = {}'.format(indent, key, get_bool(value)))
        elif type_dict[key] == INT_ARR:
            outfp.write('{}{} = {}'.format(indent, key, get_int_arr(value)))
        elif type_dict[key] == FLOAT_ARR:
            outfp.write('{}{} = {}'.format(indent, key, get_float_arr(value)))
        elif type_dict[key] == STRING_ARR:
            outfp.write('{}{} = {}'.format(indent, key, get_string_arr(value)))
        elif type_dict[key] == BOOL_ARR:
            outfp.write('{}{} = {}'.format(indent, key, get_bool_arr(value)))
        elif type_dict[key] == VECTOR2:
            outfp.write('{}{} = {}'.format(indent, key, get_vector2(value)))
        elif type_dict[key] == VECTOR3:
            outfp.write('{}{} = {}'.format(indent, key, get_vector3(value)))
        elif type_dict[key] == EULER:
            outfp.write('{}{} = {}'.format(indent, key, get_euler(value)))
        elif type_dict[key] == COLOR:
            outfp.write('{}{} = {}'.format(indent, key, get_color(value)))
        elif type_dict[key] == LUA:
            outfp.write('{}{} = {}'.format(indent, key, get_lua(value)))
        elif type_dict[key] == TRANSLATE:
            outfp.write('{}{} = {}'.format(indent, key, get_lang(value)))
        else:
            outfp.close()
            raise RuntimeError(
                'key "{}" type "{}" is wrong'.format(key, type_dict[key]))

        cnt += 1
        if cnt == len(row):
            outfp.write('\r\n')
        else:
            outfp.write(',\r\n')


def write_to_lua_kv(data, keys, type_dict, outfp, depth):
    cnt = 0
    keyX = keys[depth - 1]
    indent = get_indent(depth)
    prefix = '[{}] = ' if type_dict[keyX] == INT else '{} = '
    suffix_comma = ',\r\n'
    suffix_end = '\r\n'

    prefix = indent + prefix
    suffix_comma = suffix_comma
    suffix_end = suffix_end

    for (_, kv) in data.items():
        key, value = None, None
        for (k, v) in kv.items():
            if type_dict[k] == INT and k.lower() == 'key':
                key = get_int(v)
            elif type_dict[k] == STRING and k.lower() == 'key':
                key = get_lua(v)
            elif type_dict[k] == LUA and k.lower() == 'value':
                value = get_lua(v)
            else:
                raise RuntimeError('kv excel format is wrong')

        if not (key and value):
            outfp.close()
            raise RuntimeError('kv excel format is wrong')

        outfp.write(prefix.format(key))
        outfp.write(value)
        cnt += 1
        outfp.write(suffix_end if cnt == len(data) else suffix_comma)


def get_indent(depth):
    indent = ''
    for _ in range(depth):
        indent += '    '
    return indent


def check_config():
    if not os.path.isfile(CONFIG_FILE):
        default_config = {
            'input_folder': INPUT_FOLDER,
            'output_folder': OUTPUT_FOLDER,
            'output_lua_template': OUTPUT_LUA_TEMPLATE,
            'kv_xls': KV_XLS,
            'translate_xls': TRANSLATE_XLS,
        }
        with open(CONFIG_FILE, 'w') as json_file:
            json_file.write(json.dumps(default_config, indent=True))
            json_file.close()
            subprocess.check_call(['attrib', '+H', CONFIG_FILE])
            log(INFO, 'generate config at {}'.format(CONFIG_FILE))


def load_config():
    check_config()
    log(INFO, 'load config from \t{}'.format(CONFIG_FILE))

    with open(CONFIG_FILE) as json_file:
        config = json.load(json_file)
        global INPUT_FOLDER, OUTPUT_FOLDER, OUTPUT_LUA_TEMPLATE, KV_XLS, TRANSLATE_XLS
        INPUT_FOLDER = config['input_folder']
        OUTPUT_FOLDER = config['output_folder']
        OUTPUT_LUA_TEMPLATE = config['output_lua_template']
        KV_XLS = config['kv_xls']
        TRANSLATE_XLS = config['translate_xls']
        json_file.close()


def save_config():
    if not os.path.isfile(CONFIG_FILE):
        return

    config = {
        'input_folder': INPUT_FOLDER,
        'output_folder': OUTPUT_FOLDER,
        'output_lua_template': OUTPUT_LUA_TEMPLATE,
        'kv_xls': KV_XLS,
        'translate_xls': TRANSLATE_XLS
    }
    with open(CONFIG_FILE, 'r+') as json_file:
        json_file.truncate(0)  # need '0' when using r+
        json_file.write(json.dumps(config, indent=True))
        json_file.close()
        log(INFO, 'save config at {}'.format(CONFIG_FILE))


def main():
    global lua_cnt
    lua_cnt = 0
    input_path = INPUT_FOLDER
    output_path = OUTPUT_FOLDER
    kv_xls = KV_XLS
    translate_xls = TRANSLATE_XLS
    log(INFO, 'input path: \t{}'.format(input_path))
    log(INFO, 'output path: \t{}'.format(output_path))
    log(INFO, 'kv excels: \t\t{}'.format(kv_xls))
    log(INFO, 'translate excel: \t{}'.format(translate_xls))
    if not os.path.exists(input_path):
        raise RuntimeError('input path does NOT exist.')
    if not os.path.exists(output_path):
        os.mkdir(output_path)
        log(INFO, 'make a new dir: \t{}'.format(output_path))

    xls_files = os.listdir(input_path)
    if len(xls_files) == 0:
        raise RuntimeError('input dir is empty.')

    # find max string len
    global max_xls_name_len
    max_xls_name_len = len(max(xls_files, key=len))

    # filer files by .xls
    xls_files = [x for x in xls_files
                 if (x[-4:] in ['.xls'] or x[-5:] in ['.xlsm', '.xlsx']) and x[0:2] not in ['~$']]
    log(INFO, 'total XLS: \t\t%s' % len(xls_files))

    # move translate excel to last element
    if TRANSLATE_XLS in xls_files:
        idx = xls_files.index(TRANSLATE_XLS)
        xls_files[idx], xls_files[-1] = xls_files[-1], xls_files[idx]
    # print(xls_files)

    for i in range(len(xls_files)):
        xls_file = xls_files[i]
        if xls_file == TRANSLATE_XLS:
            update_translate_xls('%s/%s' % (INPUT_FOLDER, xls_file))

        t, ret, errstr = make_table('%s/%s' % (INPUT_FOLDER, xls_file))
        if ret != 0:
            lua_cnt += 1
            log(FAILED, '[{:02d}] {}'.format(lua_cnt, xls_file))
            raise RuntimeError(errstr)
        else:
            write_to_lua_script(t, output_path, xls_file)


def run():
    try:
        log(INFO,
            'time: \t\t{0:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()))
        load_config()
        main()
        global lua_cnt
        log(INFO, 'total Lua: \t\t{}'.format(lua_cnt))
        log(INFO, 'done.')
        if gui is None:
            log(INFO, 'press Enter to exit...')
            input()
    except (RuntimeError, ValueError, SyntaxError, AssertionError) as err:
        log(ERROR, str(err))
        if gui is None:
            log(INFO, 'check error please...')
            input()


def set_gui(frame):
    global gui
    if frame is not None:
        gui = frame
        global INFO, ERROR, SUCCESS, FAILED
        INFO = 'info'
        ERROR = 'error'
        SUCCESS = 'sucess'
        FAILED = 'failed'
    else:
        log(ERROR, 'frame is None.')


def log(prefix, s):
    if gui is not None:
        gui.write(prefix, s)
    else:
        print('[{}] {}'.format(prefix, s))


if __name__ == '__main__':
    run()
