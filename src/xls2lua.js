const util = require("util")
const path = require('path');
const fs = require('fs')
const xlrd = require('node-xlrd')

const INPUT_FOLDER = './xls'
const OUTPUT_FOLDER = './code'
// 支持的Excel文件后缀，其实xlrd和node-xlrd只支持xls
// TODO 改用sheetjs处理excel文件
// https://zhuanlan.zhihu.com/p/138405727
// https://www.cnblogs.com/liuxianan/p/js-excel.html
const FILE_EXTENSIONS = ['xls', 'xlsm', 'xlsx']
const OUTPUT_LUA_TEMPLATE = "['World']['Global']['Xls']['%sXlsModule'].ModuleScript.lua"
const KV_XLS = ['GlobalSetting.xlsx']
const TRANSLATE_XLS = 'LanguagePack.xls'
/*
const INFO = '\033[36minfo\033[0m'
const ERROR = '\033[31merror\033[0m'
const SUCCESS = '\033[92msucess\033[0m'
const FAILED = '\033[91mfailed\033[0m'
*/
const INT = "int", 
    FLOAT = "float",
    STRING = "string",
    BOOL = "bool"

const INT_ARR = "int[]", 
    FLOAT_ARR = "float[]", 
    STRING_ARR = "string[]" , 
    BOOL_ARR = "bool[]"

const VECTOR2 = 'vector2', 
    VECTOR3 = 'vector3', 
    EULER = 'euler', 
    COLOR = 'color'

const LUA = 'lua', 
    COMMENT = 'comment', 
    TRANSLATE = 'translate'

const CONFIG_FILE = '.ava-x2l-config.json'

const KEY_1 = 'key1',
    KEY_2 = 'key2',
    KEY_3 = 'key3'
/* cell types: 
exports.XL_CELL_EMPTY = 0;
exports.XL_CELL_TEXT = 1;
exports.XL_CELL_NUMBER = 2;
exports.XL_CELL_DATE = 3;
exports.XL_CELL_BOOLEAN = 4;
exports.XL_CELL_ERROR = 5;
exports.XL_CELL_BLANK = 6; */
const type_checker = {
    0: [],
    1: [STRING, INT_ARR, FLOAT_ARR, STRING_ARR, BOOL_ARR, VECTOR2, VECTOR3, EULER, COLOR, LUA, COMMENT, TRANSLATE],
    2: [INT, FLOAT, LUA],
    3: [],
    4: [BOOL, LUA],
    5: [],
    6: []
}

const para_checker = {
    'vector2': {'num_required': 2, 'filler_str': 'Vector2('},
    'vector3': {'num_required': 3, 'filler_str': 'Vector3('},
    'euler': {'num_required': 3, 'filler_str': 'EulerDegree('},
    'color': {'num_required': 4, 'filler_str': 'Color('}
}

const TYPES_CHECK_LIST = [INT, FLOAT, STRING, BOOL, INT_ARR, FLOAT_ARR, STRING_ARR, BOOL_ARR, VECTOR2, VECTOR3, EULER, COLOR, COMMENT, LUA, TRANSLATE]

var lua_cnt = 0 
var max_xls_name_len = 0 
var g_lang_kv = {} 

var ret_flag = true 

function read_file(filename) {
    console.log(filename+' is file: '+fs.statSync(filename).isFile())
    var excel = {'filename': filename, 'data': {}, 'meta': {}}    
    var t = {}, 
    ret = -1, 
    err_str = ''
    xlrd.open(filename, make_table)
    setTimeout(() => console.log('waiting for parse'), 100)
    function make_table(err, book) {
        if (err) {
            console.log('make_table error', err.name, err.message)
        }
        // var excel = {'filename': filename, 'data': {}, 'meta': {}}
        for (let sheet of book.sheets) {
            var rowCount = sheet.row.count,
                columnCount = sheet.column.count
            var sheet_name = sheet.name.replace(/ /g, '_')
            
            if (! sheet_name.startsWith('output_')) continue
            sheet_name = sheet_name.substring(7)
            console.log(filename, 'Sheet[%s]', sheet_name)
            var data = excel['data'][sheet_name] = {}
            var meta = excel['meta'][sheet_name] = {}
            //表单必须大于4行
            if (rowCount < 4) {
                // return {t: {}, ret: -1, err_str:'sheet['+sheet_name+'] rows must > 4'}
                t = {}
                ret = -1 
                err_str = 'sheet['+sheet_name+'] rows must > 4'
                return 
            } 
            var type_dict = {}
            for (let col_idx=0; col_idx<columnCount; col_idx++) {
                let title = String(sheet.cell(1, col_idx)).replace(/ /g, '_')
                let title_type = sheet.cell.getType(1, col_idx)
                let type_name = String(sheet.cell(2, col_idx)).toLowerCase()
                let type_type = sheet.cell.getType(2, col_idx)
                //检查标题数据格式
                if (title == null) {
                    // return {t: {}, ret: -1, err_str:'sheet['+sheet_name+'] title column['+(col_idx+1)+'] must be String'}
                    t = {}
                    ret = -1 
                    err_str = 'sheet['+sheet_name+'] title column['+(col_idx+1)+'] must be String'
                    return 
                }
                if (title_type != 1) {
                    // return {t: {}, ret: -1, err_str:'sheet['+sheet_name+'] title column['+(col_idx+1)+'] must be String'}
                    t = {}
                    ret = -1 
                    err_str = 'sheet['+sheet_name+'] title column['+(col_idx+1)+'] must be String'
                    return 
                }
                if (type_type != 1) {
                    // return {t: {}, ret: -1, err_str:'sheet['+sheet_name+'] type column['+(col_idx+1)+'] must be String'}
                    t = {}
                    ret = -1 
                    err_str = 'sheet['+sheet_name+'] type column['+(col_idx+1)+'] must be String'
                    return
                }
                if (!TYPES_CHECK_LIST.includes(type_name)) {
                    // return {t: {}, ret: -1, err_str:'sheet['+sheet_name+'] type column['+(col_idx+1)+'] type wrong'}
                    t = {}
                    ret = -1 
                    err_str = 'sheet['+sheet_name+'] type column['+(col_idx+1)+'] type wrong'
                    return
                }
                type_dict[title] = type_name
            }
            meta['type_dict'] = type_dict
            
            for (let row_idx=3, col_idx=0; col_idx<columnCount; col_idx++) {
                let key = String(sheet.cell(row_idx, col_idx)).toLowerCase()
                let col_name = String(sheet.cell(1, col_idx))
                let col_type = String(sheet.cell(2, col_idx)).toLowerCase()
                if ([KEY_1, KEY_2, KEY_3].includes(key)) {
                    if (!([INT, FLOAT, STRING].includes(col_type))) {
                        // return {t: {}, ret: -1, err_str:'sheet['+sheet_name+'] type must be Int, Float, or String'}
                        t = {}
                        ret = -1 
                        err_str = 'sheet['+sheet_name+'] type must be Int, Float, or String'
                        return
                    }
                    meta[key] = col_name
                }
            }
            if ((KEY_3 in meta && (!(KEY_2 in meta && KEY_1 in meta))) || (KEY_2 in meta && (!(KEY_1 in meta))) || (!(KEY_1 in meta)))  {
                // return {t: {}, ret: -1, err_str:'sheet['+sheet_name+'] Key error'}
                t = {}
                ret = -1 
                err_str = 'sheet['+sheet_name+'] Key error'
                return
            }
            var key1 = (KEY_1 in meta) ? meta[KEY_1] : null 
            var key2 = (KEY_2 in meta) ? meta[KEY_2] : null 
            var key3 = (KEY_3 in meta) ? meta[KEY_3] : null 
            for (let row_idx=4; row_idx<rowCount; row_idx++) {
                var row = {}
                var key_v1 = null,
                    key_v2 = null,
                    key_v3 = null
                var lang_kv = {}
                for (let col_idx=0; col_idx<columnCount; col_idx++) {
                    let title = sheet.cell(1, col_idx)
                    let value = sheet.cell(row_idx, col_idx)
                    let vtype = sheet.cell.getType(row_idx, col_idx)
                    // 本行有数据
                    var v = null 
                    // console.log(vtype, type_dict[title])
                    // todo: problem fixed, keep an eye on it though
                    if (type_checker[vtype].includes(type_dict[title])) {
                        //COMMENT 
                        if (type_dict[title] == COMMENT) continue 
                        // INT & FLOAT & LUA
                        else if (vtype == 2) v = Number(value)
                        // STRING & STRING ARRAY
                        else if (type_dict[title] == STRING || type_dict[title] == STRING_ARR) v = format_str(value)
                        // TRANSLATE
                        else if (type_dict[title] == TRANSLATE) lang_kv[title] = sheet_name + '_' + title + '_' 
                        // BOOL 
                        else if (vtype == 4) v = (value == 1) ? 'true' : 'false' 
                        // OTHERS 
                        else v = String(value) 
                    }
                    row[title] = v
                    if (title == key1) key_v1 = v 
                    if (title == key2) key_v2 = v 
                    if (title == key3) key_v3 = v 
                }
                // console.log('key_v1: %s, key_v2: %s, key_v3: %s',key_v1,key_v2,key_v3)
                // 键值检查 
                if (key1 && key2 && key3) {
                    if (!(key_v1 in data)) data[key_v1] = {}
                    if (!(key_v2 in data[key_v1])) data[key_v1][key_v2] = {}
                    if (key_v3 == null) {
                        // return {t: {}, ret: -1, err_str:'sheet['+sheet_name+']['+(row_idx+1)+'] '+KEY_3+' data '+key3+' is empty'}
                        t = {}
                        ret = -1 
                        err_str = 'sheet['+sheet_name+']['+(row_idx+1)+'] '+KEY_3+' data '+key3+' is empty'
                        return
                    } else if (key_v3 in data[key_v1][key_v2]) {
                        // return {t: {}, ret: -1, err_str:'sheet['+sheet_name+']['+(row_idx+1)+'] '+KEY_3+' data '+key3+' is duplicated'}
                        t = {}
                        ret = -1 
                        err_str = 'sheet['+sheet_name+']['+(row_idx+1)+'] '+KEY_3+' data '+key3+' is duplicated'
                        return
                    } else {
                        data[key_v1][key_v2][key_v3] = row
                        lang_suffix = key_v1+'_'+key_v2+'_'+key_v3
                    }
                } else if (key1 && key2) {
                    if (!(key_v1 in data)) data[key_v1] = {}
                    if (key_v2 == null) {
                        // return {t: {}, ret: -1, err_str:'sheet['+sheet_name+']['+(row_idx+1)+'] '+KEY_2+' data '+key2+' is empty'}
                        t = {}
                        ret = -1 
                        err_str = 'sheet['+sheet_name+']['+(row_idx+1)+'] '+KEY_2+' data '+key2+' is empty'
                        return
                    } else if (key_v2 in data[key_v1]) {
                        // return {t: {}, ret: -1, err_str:'sheet['+sheet_name+']['+(row_idx+1)+'] '+KEY_2+' data '+key2+' is duplicated'}
                        t = {}
                        ret = -1 
                        err_str = 'sheet['+sheet_name+']['+(row_idx+1)+'] '+KEY_2+' data '+key2+' is duplicated'
                        return
                    } else {
                        data[key_v1][key_v2] = row
                        lang_suffix = key_v1+'_'+key_v2
                    }
                } else if (key1) {
                    if (key_v1 == null) {
                        // return {t: {}, ret: -1, err_str:'sheet['+sheet_name+']['+(row_idx+1)+'] '+KEY_1+' data '+key1+' is empty'}
                        t = {}
                        ret = -1 
                        err_str = 'sheet['+sheet_name+']['+(row_idx+1)+'] '+KEY_1+' data '+key1+' is empty'
                        return
                    } else if (key_v1 in data) {
                        // return {t: {}, ret: -1, err_str:'sheet['+sheet_name+']['+(row_idx+1)+'] '+KEY_1+' data '+KEY_1+' is duplicated'}
                        t = {}
                        ret = -1 
                        err_str = 'sheet['+sheet_name+']['+(row_idx+1)+'] '+KEY_1+' data '+KEY_1+' is duplicated'
                        return
                    } else {
                        data[key_v1] = row
                        lang_suffix = String(key_v1)
                    }
                } else {
                    // return {t: {}, ret: -1, err_str:'sheet['+sheet_name+'] missing Keys'}
                    t = {}
                    ret = -1 
                    err_str = 'sheet['+sheet_name+'] missing Keys'
                    return
                }

                for (let key in lang_kv) {
                    let lang_id = lang_kv[key] + lang_suffix
                    g_lang_kv[lang_id] = row[key]
                    row[key] = lang_id
                }
            }
        }
        // for (let e in excel) {console.log(e, excel[e])}
        console.log('phase success')
        // TODO: make_table() nested in read_file() and no results returned by make_table()
        // return {t: excel, ret: 0, err_str: 'OK'}
        t = excel
        ret = 0 
        err_str = 'OK'
        ret_flag = false
    }
    return {t: t, ret: ret, err_str: err_str}
}

function format_str(st) {
    if (typeof(st) == "number") st = String(st)
    st = st.replace(/\"/g, '\\\"').replace(/\'/g, '\\\'')
    return st
}

get_number = v => v ? v : null
get_string = v => v ? ('\'' + v + '\'') : null 
get_bool = v => v ? v : null 

function get_array (v, data_type) {
    if (v) {
        let splited = v.split(',')
        let res_str = '{'
        let head_indicator = 0
        for (let val of splited) {
            if (! val == '') {
                if (! head_indicator == 0) res_str += ', '
                if (type == INT || type == FLOAT) res_str += val 
                if (type == STRING) res_str = res_str + '\'' + val + '\'' 
                if (type == BOOL) res_str += val.toLowerCase()
                head_indicator += 1 
            }
        }
        res_str += '}'
        return res_str 
    } else return null 
} 

function get_obj_property (v, type) {
    if (v) {
        let splited = v.split(',')
        if (! splited.length()==para_checker[type]['num_required']) return null 
        let res_str = para_checker[type]['filler_str']
        let head_indicator = 0 
        for (let val of splited) {
            if (! val == '') {
                if (! head_indicator == 0) res_str += ', '
                res_str += val.toLowerCase()
                head_indicator += 1 
            }
        }
        res_str += '}' 
        return res_str 
    } else return null 
}

get_lua = v => v ? v : null
get_lang = v => get_string(v)

function update_translate_xls (filename) {
    if (! fs.statSync(filename).isFile()) console.error('%s is not a valid filename', filename) 
}

function write_to_lua_script (workbook, output_path, xls_file) {
    for (let sheet in workbook['data']) {
        let meta = workbook['meta'][sheet] 
        let type_dict = meta['type_dict'] 
        let key1 = (KEY_1 in meta) ? meta[KEY_1] : null 
        let key2 = (KEY_2 in meta) ? meta[KEY_2] : null 
        let key3 = (KEY_3 in meta) ? meta[KEY_3] : null 

        let path_filename = util.format(output_path+'/'+OUTPUT_LUA_TEMPLATE, sheet)
        var outfp = fs.createWriteStream(path_filename, {
            flags: 'a' // 'a' means appending 即在文件结尾写入内容
        })
        outfp.write('local ' + sheet + suffix + ' = {\r\n')
        if (key1&&key2&&key3) {
            write_to_lua_key(sheet, [key1, key2, key3], type_dict, outfp, 1)
        } else if (key1 && key2) {
            write_to_lua_key(sheet, [key1, key2], type_dict, outfp, 1)
        } else if (key1 && !(KV_XLS.includes(xls_file))) {
            write_to_lua_key(sheet, [key1], type_dict, outfp, 1) //redundancy
        } else if (key1) {
            write_to_lua_key(sheet, [key1], type_dict, outfp, 1)
        } else {
            outfp.end()
            console.error('key missing')
        }
        outfp.write('}\r\n\r\nreturn ' + sheet_name + suffix + '\r\n')
        outfp.end() // close stream 
        lua_cnt += 1 
        // console.log(util.format(SUCCESS))
    }
}

function write_to_lua_key (data, keys, type_dict, outfp, depth) {
    let counter = 0 
    let keyX = keys[depth - 1] 
    let indent = get_indent(depth) 
    let prefix = [INT, FLOAT].includes(type_dict[keyX]) ? '[%s] = {{\r\n' : '%s = {{\r\n' 
    let suffix_coma = '},\r\n' 
    let suffix_end = '}\r\n' 
    prefix = indent + prefix
    suffix_comma = indent + suffix_comma
    suffix_end = indent + suffix_end 
    for (let key in data) {
        outfp.write(util.format(prefix, key))
        if (depth == keys.length()) {
            write_to_lua_row(data[key], type_dict, outfp, depth + 1)
        } else {
            write_to_lua_key(data[key], value, keys, type_dict, outfp, depth + 1)
        }
        counter += 1 
        if (counter == data.length()) {
            outfp.write(suffix_end)
        } else {
            outfp.write(suffix_comma)
        }
    }
}

function write_to_lua_row (row, type_dict, outfp, depth) {
    let counter = 0 
    let indent = get_indent(depth) 
    for (let key in row) {
        if ([INT, FLOAT].includes(type_dict[key])) {
            outfp.write(indent+key+' = '+get_number(row[key]))
        } else if (type_dict[key] == STRING) {
            outfp.write(indent+key+' = '+get_string(row[key]))
        } else if (type_dict[key] == BOOL) {
            outfp.write(indent+key+' = '+get_bool(row[key]))
        } else if ([INT_ARR, FLOAT_ARR, STRING_ARR, BOOL_ARR].includes(type_dict[key])) {
            outfp.write(indent+key+' = '+get_array(row[key]))
        } else if ([VECTOR2, VECTOR3, EULER, COLOR].includes(type_dict[key])) {
            outfp.write(indent+key+' = '+get_obj_property(row[key]))
        } else if (type_dict[key] == LUA) {
            outfp.write(indent+key+' = '+get_lua(row[key]))
        } else if (type_dict[key] == TRANSLATE) {
            outfp.write(indent+key+' = '+get_lang(row[key]))
        } else {
            outfp.end()
            console.error('key '+key+' type '+type_dict[key]+' is wrong')
        }
        counter += 1 
        if (counter == row.length()) {
            outfp.write('\r\n')
        } else {
            outfp.write(',\r\n')
        }
    }
} 

function write_to_lua_kv () {} 

function get_indent (depth) {
    let indent = ''
    for (let k=0; k<depth; k++) {
        indent += '    '
    }
    return indent 
}

function check_config () {
    if (! fs.statSync(CONFIG_FILE).isFile()) {
        let default_config = {
            'input_folder': INPUT_FOLDER,
            'output_folder': OUTPUT_FOLDER,
            'output_lua_template': OUTPUT_LUA_TEMPLATE,
            'kv_xls': KV_XLS,
            'translate_xls': TRANSLATE_XLS,
        }
        let json_dump = JSON.stringify(user)
        fs.writeFile(CONFIG_FILE, json_dump, (err) => {
            if (err) {
                throw err
            }
            console.log('generate config at '+CONFIG_FILE)
        })
    }
}
function load_config () {}
function save_config () {}
// main()
async function main () {
    let output_path = OUTPUT_FOLDER
    let kv_xls = KV_XLS 
    let translate_xls = TRANSLATE_XLS 
    let file_list = []
    if (! fs.existsSync(INPUT_FOLDER)) return console.error('input path does NOT exist.')
    if (! fs.existsSync(output_path)) {
        fs.mkdir(output_path, (err) => {
            if (err) return console.error(err)
            console.log('Output directory created successfully!');
        })
    }
    fs.readdirSync(INPUT_FOLDER).forEach(file => {
        if (FILE_EXTENSIONS.includes(file.split('.').pop())) file_list.push(file)
    })
    for (let xls_file of file_list) {
        if (xls_file == TRANSLATE_XLS) update_translate_xls(xls_file)
        let {t, ret, err_str} = read_file(INPUT_FOLDER +'/'+ xls_file) 
        if (! ret == 0) {
            console.error(err_str)
        } else write_to_lua_script(t, output_path, xls_file)
    }
} 

function run () {}

// read_file('test.xls')

let {t, ret, err_str} = read_file('./xls/ExampleTable1.xls')
console.log('t', t, 'ret', ret, 'err_str', err_str)

// read_file('./xls/ExampleTable1.xls')

// main()
// TODO：检查全部in 与includes 关键字