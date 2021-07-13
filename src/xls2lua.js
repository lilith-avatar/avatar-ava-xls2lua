const util = require("util")
const fs = require('fs')
const XLSX = require('xlsx')

const INPUT_FOLDER = './xls'
const OUTPUT_FOLDER = './code'
const FILE_EXTENSIONS = ['xls', 'xlsm', 'xlsx']
const OUTPUT_LUA_TEMPLATE = "['World']['Global']['Xls']['%sXlsModule'].ModuleScript.lua" 
const TRANSLATE_XLS = 'LanguagePack.xls' 
const SCRIPT_HEAD = `--- This file is generated by ava-x2l.exe,
--- Don't change it manaully.
--- @copyright Lilith Games, Project Da Vinci(Avatar Team)
--- @see Official Website: https://www.projectdavinci.com/
--- @see Dev Framework: https://github.com/lilith-avatar/avatar-ava
--- @see X2L Tool: https://github.com/lilith-avatar/avatar-ava-xls2lua
--- source file: %s

`
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

const KEY_1 = 'key1',
    KEY_2 = 'key2',
    KEY_3 = 'key3'

/* 用于检查lua类型是否与Excel中cell类型相符
cell types: 
b	Boolean: value interpreted as JS boolean
e	Error: value is a numeric code and w property stores common name 
n	Number: value is a JS number 
d	Date: value is a JS Date object or string to be parsed as Date 
s	Text: value interpreted as JS string and written as text 
z	Stub: blank stub cell that is ignored by data processing utilities */
const type_checker = {
    b: [BOOL, LUA],
    e: [],
    n: [INT, FLOAT, LUA],
    d: [],
    s: [STRING, INT_ARR, FLOAT_ARR, STRING_ARR, BOOL_ARR, VECTOR2, VECTOR3, EULER, COLOR, LUA, COMMENT, TRANSLATE],
    z: []
}

const para_checker = {
    'vector2': {'num_required': 2, 'filler_str': 'Vector2('},
    'vector3': {'num_required': 3, 'filler_str': 'Vector3('},
    'euler': {'num_required': 3, 'filler_str': 'EulerDegree('},
    'color': {'num_required': 4, 'filler_str': 'Color('}
}

const types_check_list = [INT, FLOAT, STRING, BOOL, INT_ARR, FLOAT_ARR, STRING_ARR, BOOL_ARR, VECTOR2, VECTOR3, EULER, COLOR, COMMENT, LUA, TRANSLATE]

var lua_cnt = 0 
var max_xls_name_len = 0 
var g_lang_kv = {} 

function length(obj) {
    return Object.keys(obj).length
}

/* 辅助功能，Excel列名转为实际列数
   如单元格‘G5’表示G列第五行，实际列数为7 */
function titleToNumber(title) {
    let res = 0
    let len = title.length
    for(let i=0; i<len; i++)
        res+=(title[i].charCodeAt()-65+1)*Math.pow(26,len-i-1)
    return res 
}

/* 辅助功能，Excel实际列数转为列名
   如第七列第五行的单元格‘G5’，列名为G */
function numberToTitle(number) {
    const getChar = (num) => {
        return String.fromCharCode(64 + num);
    }
    let res = []
    for (let cur; number > 0; number = Math.floor((number - cur) / 26)) {
        cur = number % 26 || 26
        res.push(getChar(cur))
    }
    return res.reverse().join("")
}

/* 遍历Excel文档中的表，以生成excel对象并将其返回 */
function make_table(filename) {
    // console.log(filename+' is file: '+fs.statSync(filename).isFile())
    var excel = {'filename': filename, 'data': {}, 'meta': {}} 
    let only_filename = filename.split('/').pop()
    let workbook = XLSX.readFile(filename)
    let sheet_names = workbook.SheetNames
    const match_max_column = /^[A-Z]+/g
    const match_max_row = /[0-9]+$/g
    for (let sheet of sheet_names) {
        let sheet_name = sheet.replace(/ /g, '_')
        // 检查项：数据表表名应以output_或kv_为开头
        if (!(sheet_name.startsWith('output_')||sheet_name.startsWith('kv_'))) continue
        console.log('Processing: ',filename, util.format('Sheet[%s]', sheet_name))
        var data = excel['data'][sheet_name] = {}
        var meta = excel['meta'][sheet_name] = {}
        let worksheet = workbook.Sheets[sheet]
        // 获取表格行列范围，注意实际表格末尾可能存在为空白值的行或列
        let sheet_range = worksheet['!ref'].split(':')
        let column_title_range = sheet_range[1].match(match_max_column)
        let column_count = titleToNumber(column_title_range)
        let row_count = Number(sheet_range[1].match(match_max_row)[0])
        // 检查项：表单必须大于4行
        if (row_count < 4) {
            return {t: {}, ret: -1, err_str:'sheet['+sheet_name+'] rows must > 4'}
        } 
        var type_dict = {} 
        /* 检查项：标题行必须为String类型
           数据类型行必须为String类型且必须为types_check_list内允许的类型 */
        for (let col_idx=1; col_idx<=column_count; col_idx++) {
            let col_title = numberToTitle(col_idx)
            let title_cell = worksheet[col_title+'2']
            let type_cell = worksheet[col_title+'3']
            if (title_cell) {
                let title = String(title_cell.v).replace(/ /g, '_')
                let title_type = title_cell.t // s for String 
                let type_name = String(type_cell.v).toLowerCase()
                let type_type = type_cell.t 
                if (title_type != 's') {
                    return {t: {}, ret: -1, err_str:'sheet['+sheet_name+'] title column['+(col_idx)+'] must be String'}
                }
                if (type_type != 's') {
                    return {t: {}, ret: -1, err_str:'sheet['+sheet_name+'] type column['+(col_idx)+'] must be String'}
                }
                if (!types_check_list.includes(type_name)) {
                    return {t: {}, ret: -1, err_str:'sheet['+sheet_name+'] type column['+(col_idx)+'] type wrong'}
                }
                type_dict[title] = type_name
            } 
        }
        meta['type_dict'] = type_dict
        // try to fetch keys, then write into meta dict
        for (let col_idx=1; col_idx<=column_count; col_idx++) {
            let col_title = numberToTitle(col_idx)
            let key_cell = worksheet[col_title+'4']
            if (key_cell) {
                let key = String(key_cell.v).toLowerCase()
                if (!worksheet[col_title+'2'] || !worksheet[col_title+'3']) {
                    return {t: {}, ret: -1, err_str:'sheet['+sheet_name+'] title and type of column['+(col_idx)+'] must be String'}
                }
                let col_name = String(worksheet[col_title+'2'].v)
                let col_type = String(worksheet[col_title+'3'].v).toLowerCase()
                if ([KEY_1, KEY_2, KEY_3].includes(key)) {
                    if (!([INT, FLOAT, STRING].includes(col_type))) {
                        return {t: {}, ret: -1, err_str:'sheet['+sheet_name+'] type must be Int, Float, or String'}
                    }
                    meta[key] = col_name
                }
            }
        }
        if ((KEY_3 in meta && (!(KEY_2 in meta && KEY_1 in meta))) || (KEY_2 in meta && (!(KEY_1 in meta))) || (!(KEY_1 in meta)))  {
            return {t: {}, ret: -1, err_str:'sheet['+sheet_name+'] Key error'}
        }
        var key1 = (KEY_1 in meta) ? meta[KEY_1] : null 
        var key2 = (KEY_2 in meta) ? meta[KEY_2] : null 
        var key3 = (KEY_3 in meta) ? meta[KEY_3] : null 
        for (let row_idx=5; row_idx<=row_count; row_idx++) {
            let row = {}
            let key_v1 = null,
                key_v2 = null,
                key_v3 = null
            let lang_kv = {}
            // cell value traversal 
            for (let col_idx=1; col_idx<=column_count; col_idx++) {
                let col_title = numberToTitle(col_idx)
                let title_cell = worksheet[col_title+'2']
                if (! title_cell) continue 
                let title = String(title_cell.v).replace(/ /g, '_')
                let value_cell = worksheet[col_title+String(row_idx)]
                let v = null 
                if (value_cell) {
                    let value = value_cell.v 
                    let vtype = value_cell.t 
                    // console.log(vtype, type_dict[title])
                    if (type_checker[vtype].includes(type_dict[title])) {
                        //COMMENT 
                        if (type_dict[title] == COMMENT) continue 
                        // INT & FLOAT & LUA
                        else if (vtype == 'n') v = Number(value)
                        // STRING & STRING ARRAY
                        else if (type_dict[title] == STRING || type_dict[title] == STRING_ARR) v = format_str(value)
                        // TRANSLATE
                        else if (type_dict[title] == TRANSLATE) lang_kv[title] = sheet_name + '_' + title + '_' 
                        // BOOL 
                        else if (vtype == 'b') v = (value == 1) ? 'true' : 'false' 
                        // OTHERS 
                        else v = String(value) 
                    }
                } else {
                    v = 'nil'
                }
                row[title] = v
                if (title == key1) key_v1 = v 
                if (title == key2) key_v2 = v 
                if (title == key3) key_v3 = v 
                // TODO: 检查key_v1是类型是string的话，不能为数字，需要符合lua命名规范
            }
            // console.log('key_v1: %s, key_v2: %s, key_v3: %s',key_v1,key_v2,key_v3)
            // 检查项：键值检查 
            if (key1 && key2 && key3) {
                if (!(key_v1 in data)) data[key_v1] = {}
                if (!(key_v2 in data[key_v1])) data[key_v1][key_v2] = {}
                if (key_v3 == 'nil') {
                    // return {t: {}, ret: -1, err_str:'sheet['+sheet_name+']['+(row_idx+1)+'] '+KEY_3+' data '+key3+' is empty'}
                    continue
                } else if (key_v3 in data[key_v1][key_v2]) {
                    return {t: {}, ret: -1, err_str:'sheet['+sheet_name+']['+(row_idx+1)+'] '+KEY_3+' data '+key3+' is duplicated'}
                } else {
                    data[key_v1][key_v2][key_v3] = row
                    lang_suffix = key_v1+'_'+key_v2+'_'+key_v3
                }
            } else if (key1 && key2) {
                if (!(key_v1 in data)) data[key_v1] = {}
                if (key_v2 == 'nil') {
                    // return {t: {}, ret: -1, err_str:'sheet['+sheet_name+']['+(row_idx+1)+'] '+KEY_2+' data '+key2+' is empty'}
                    continue
                } else if (key_v2 in data[key_v1]) {
                    return {t: {}, ret: -1, err_str:'sheet['+sheet_name+']['+(row_idx+1)+'] '+KEY_2+' data '+key2+' is duplicated'}
                } else {
                    data[key_v1][key_v2] = row
                    lang_suffix = key_v1+'_'+key_v2
                }
            } else if (key1) {
                if (key_v1 == 'nil') {
                    // return {t: {}, ret: -1, err_str:'sheet['+sheet_name+']['+(row_idx+1)+'] '+KEY_1+' data '+key1+' is empty'}
                    continue
                } else if (key_v1 in data) {
                    return {t: {}, ret: -1, err_str:'sheet['+sheet_name+']['+(row_idx+1)+'] '+KEY_1+' data '+KEY_1+' is duplicated'}
                } else {
                    data[key_v1] = row
                    lang_suffix = String(key_v1)
                }
            } else {
                return {t: {}, ret: -1, err_str:'sheet['+sheet_name+'] missing Keys'}
            }

            for (let key in lang_kv) {
                let lang_id = lang_kv[key] + lang_suffix
                g_lang_kv[lang_id] = row[key]
                row[key] = lang_id
            }
        }
    }
    // for (let e in excel) {console.log(e, excel[e])} 
    return {t: excel, ret: 0, err_str: only_filename + ' processed successfully.'}
}

function format_str(st) {
    if (typeof(st) == "number") st = String(st)
    st = st.replace(/\"/g, '\\\"').replace(/\'/g, '\\\'')
    return st
}

get_string = v => (v == 'nil') ? v : ('\'' + v + '\'') 

function get_array (v, data_type) {
    if (v == 'nil') {
        return v 
    }
    else {
        let splitted = v.split(',')
        let res_str = '{'
        let head_indicator = 0
        for (let val of splitted) {
            if (! val == '') {
                if (! head_indicator == 0) res_str += ', '
                if (data_type == INT_ARR || data_type == FLOAT_ARR) res_str += val 
                if (data_type == STRING_ARR) res_str = res_str + '\'' + val + '\'' 
                if (data_type == BOOL_ARR) res_str += val.toLowerCase()
                head_indicator += 1 
            }
        }
        res_str += '}'
        return res_str 
    } 
} 
/* */
function get_obj_property (v, type) {
    if (v == 'nil') {
        return v
    }
    else {
        let splitted = v.split(',')
        if (! length(splitted)==para_checker[type]['para_num']) return 'nil' 
        let res_str = para_checker[type]['filler_str']
        let head_indicator = 0 
        for (let val of splitted) {
            if (! val == '') {
                if (! head_indicator == 0) res_str += ', '
                res_str += val.toLowerCase()
                head_indicator += 1 
            }
        }
        res_str += ')' 
        return res_str 
    } 
}
// TODO: Implementation 
function update_translate_xls (filename) {
    if (! fs.statSync(filename).isFile()) console.error('%s is not a valid filename', filename) 
    let workbook = XLSX.readFile(filename)
    let sheet_names = workbook.SheetNames
}

/* 打开文件写入流outfp，将excel对象写入lua文件 */
function write_to_lua_script (workbook, output_path) {
    for (let sheet_name in workbook['data']) {
        let sheet = workbook['data'][sheet_name]
        let meta = workbook['meta'][sheet_name] 
        let type_dict = meta['type_dict'] 
        let key1 = (KEY_1 in meta) ? meta[KEY_1] : null 
        let key2 = (KEY_2 in meta) ? meta[KEY_2] : null 
        let key3 = (KEY_3 in meta) ? meta[KEY_3] : null 
        let output_sheetname = sheet_name
        // 截取output_和kv_之后的实际表名 
        if (sheet_name.startsWith('output_')) output_sheetname = sheet_name.substring(7)
        if (sheet_name.startsWith('kv_')) output_sheetname = sheet_name.substring(3)
        let path_filename = util.format(output_path+'/'+OUTPUT_LUA_TEMPLATE, output_sheetname)
        // TODO: 决定suffix固定为xls还是根据excel文档格式定义
        let suffix = 'Xls'
        var outfp = fs.createWriteStream(path_filename, {
            flags: 'w' // 'w': File system flag, 写入并覆盖文件
        })
        outfp.write(util.format(SCRIPT_HEAD, workbook['filename']))
        outfp.write('local ' + output_sheetname + suffix + ' = {\r\n')
        if (key1&&key2&&key3) {
            write_to_lua_key(sheet, [key1, key2, key3], type_dict, outfp, 1)
        } else if (key1 && key2) {
            write_to_lua_key(sheet, [key1, key2], type_dict, outfp, 1) 
        } else if (key1 && sheet_name.startsWith('kv_')) { 
            write_to_lua_kv(sheet, [key1], type_dict, outfp, 1)
        } else if (key1) { 
            write_to_lua_key(sheet, [key1], type_dict, outfp, 1) 
        } else {
            outfp.end()
            console.error('key missing')
        }
        outfp.write('}\r\n\r\nreturn ' + output_sheetname + suffix + '\r\n')
        outfp.end() // 关闭文件写入流
        lua_cnt += 1 
    }
}
/* */
function write_to_lua_key (data, keys, type_dict, outfp, depth) {
    let counter = 0 
    let keyX = keys[depth - 1] 
    let indent = get_indent(depth) 
    let prefix = [INT, FLOAT].includes(type_dict[keyX]) ? '[%s] = {\r\n' : '%s = {\r\n' 
    let suffix_comma = '},\r\n' 
    let suffix_end = '}\r\n' 
    prefix = indent + prefix
    suffix_comma = indent + suffix_comma
    suffix_end = indent + suffix_end 
    for (let key in data) {
        outfp.write(util.format(prefix, key))
        if (depth == length(keys)) {
            write_to_lua_row(data[key], type_dict, outfp, depth+1)
        } else {
            write_to_lua_key(data[key], keys, type_dict, outfp, depth+1)
        }
        counter += 1 
        if (counter == length(data)) {
            outfp.write(suffix_end)
        } else {
            outfp.write(suffix_comma)
        }
    }
}
/* */
function write_to_lua_row (row, type_dict, outfp, depth) {
    let counter = 0 
    let indent = get_indent(depth) 
    for (let key in row) {
        if ([INT, FLOAT, BOOL, LUA].includes(type_dict[key])) {
            outfp.write(indent+key+' = '+row[key])
        } else if ([TRANSLATE, STRING].includes(type_dict[key])) { 
            outfp.write(indent+key+' = '+get_string(row[key]))
        } else if ([INT_ARR, FLOAT_ARR, STRING_ARR, BOOL_ARR].includes(type_dict[key])) {
            outfp.write(indent+key+' = '+get_array(row[key],type_dict[key]))
        } else if ([VECTOR2, VECTOR3, EULER, COLOR].includes(type_dict[key])) {
            outfp.write(indent+key+' = '+get_obj_property(row[key],type_dict[key]))
        } else {
            outfp.end()
            console.error('key '+key+' type '+type_dict[key]+' is wrong')
        }
        counter += 1 
        if (counter == length(row)) {
            outfp.write('\r\n')
        } else {
            outfp.write(',\r\n')
        }
    }
} 
/* */
function write_to_lua_kv (data, keys, type_dict, outfp, depth) {
    let counter = 0 
    let keyX = keys[depth-1] 
    let indent = get_indent(depth) 
    let prefix = [INT, FLOAT].includes(type_dict[keyX]) ? '[%s] = ' : '%s = ' 
    let suffix_comma = ',\r\n'
    let suffix_end = '\r\n'
    prefix = indent + prefix 
    for (let element in data) {
        let key = null 
        let value = null
        let kv = data[element]
        for (let index in kv) {
            if ((type_dict[index]==INT || type_dict[index]==FLOAT)&& index.toLowerCase()=='key') {
                key = kv[index]
            } else if (type_dict[index]==STRING && index.toLowerCase()=='key') {
                key = kv[index]
            } else if (type_dict[index]==LUA && index.toLowerCase()=='value') {
                value = String(kv[index])
            } else console.error('kv excel format is wrong')
        }
        if (!(key && value)) {
            outfp.end()
            console.error('kv excel format is wrong')
        }
        outfp.write(util.format(prefix, key))
        outfp.write(value)
        counter += 1
        if (counter == length(data)) {
            outfp.write(suffix_end)
        } else {
            outfp.write(suffix_comma)
        }
    }
} 

function get_indent (depth) {
    let indent = ''
    for (let k=0; k<depth; k++) {
        indent += '    '
    }
    return indent 
}

async function transferToLua (input_path=INPUT_FOLDER, output_path=OUTPUT_FOLDER) { 
    let exl_list = []
    let file_counter = 0
    let success_counter = 0
    let err_msgs = []
    if (! fs.existsSync(input_path)) return console.error('input path does NOT exist.')
    if (! fs.existsSync(output_path)) {
        fs.mkdir(output_path, (err) => {
            if (err) return console.error(err)
            console.log('Output directory created successfully!');
        })
    }
    fs.readdirSync(input_path).forEach(file => {
        if (FILE_EXTENSIONS.includes(file.split('.').pop())) exl_list.push(file)
    })
    // todo: move translate excel to last element
    for (let xls_file of exl_list) {
        if (xls_file == TRANSLATE_XLS) update_translate_xls(input_path +'/'+ xls_file)
        let {t, ret, err_str} = make_table(input_path +'/'+ xls_file) 
        file_counter += 1
        err_msgs.push(err_str)
        if (! ret == 0) {
            console.error(err_str)
        } else {
            write_to_lua_script(t, output_path)
            success_counter += 1
        }
    }
    let return_msg = util.format('共%s个文件处理完毕, 成功转化%s个lua代码文件', file_counter, success_counter)
    let return_msgs = {
        message: return_msg, // 所有文件处理完成后的返回信息
        file_list: exl_list, // 已处理的文件列表
        error_messages: err_msgs // 数组，包含每个文件返回的err_str
    }
    console.log(return_msgs)
    return return_msgs
} 

// transferToLua()