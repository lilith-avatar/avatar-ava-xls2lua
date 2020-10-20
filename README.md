# Avatar Ava-xls2lua
莉莉丝游戏达芬奇计划内容组Excel转Lua工具（适用于Ava框架）

[![](https://img.shields.io/badge/-DaVinci-MediumPurple)](http://api.projectdavinci.com/)
[![](https://img.shields.io/badge/project-Ava-ff69b4)](https://github.com/lilith-avatar/avatar-ava/projects/1)
[![](https://img.shields.io/badge/-wiki-DeepSkyBlue)](https://github.com/lilith-avatar/avatar-ava/wiki)
[![](https://img.shields.io/github/v/release/lilith-avatar/avatar-ava-xls2lua)](https://github.com/lilith-avatar/avatar-ava-xls2lua/releases)

[![ava-xls2lua](https://repository-images.githubusercontent.com/297525841/444b3700-fee4-11ea-9eed-f345ead4f44b)](https://github.com/lilith-avatar/avatar-ava-xls2lua)

## 介绍

ava-xls2lua是一款编辑器的外部工具，可将Excel表格批量转换成Lua脚本

Clone from [luzexi/xls2lua](https://github.com/luzexi/xls2lua)

程序语言：[Python 3](https://www.python.org/)

引用模块：[xlrd](https://pypi.org/project/xlrd/)，[xlwt](https://pypi.org/project/xlutils/)，[xlutils](https://pypi.org/project/xlutils/)，[wxPython](https://wxpython.org/)

打包模块：[PyInstaller](https://pypi.org/project/pyinstaller/)

证书：[MIT License](https://github.com/lilith-avatar/avatar-ava-xls2lua/blob/master/LICENSE)

## 主要功能

* 将Excel文件批量生成对应的Lua脚本，支持`.xls` `.xlsx` `.xlsm`
* 可以根据不同的项目结构配置目录和文件名前后缀
* 支持多语言导出，自动在翻译表中生成翻译ID和条目

## 在Excel中支持的数据类型

* 基础类型：`Int`，`Float`，`String`，`Bool`
* 数组类型：`Int[]`，`Float[]`，`String[]`，`Bool[]`
* 编辑器类型：`Vector2`，`Vector3`，`Euler`，`Color`
* Lua代码：`Lua`
* 批注类型：`Comment`（不会被转换成Lua代码）
* 翻译类型：`Translate`（在翻译表中生成对应的翻译ID，并导出Lua代码）

## 配置介绍

双击`ava-x2l.exe`，打开ava-xls2lua GUI

勾选右下角的Config可以配置相关设置

![GUI](https://user-images.githubusercontent.com/64057282/96594287-08599500-131d-11eb-9c6b-f64ba1dc42ef.png)

* Input Path：Excel文件所在目录
* Output Path：生成的Lua脚本所在目录
* Output Lua Template：Lua脚本文件名前缀，其中`{sheet_name}`是通配符，请保留
* KV Format Excel Files：配置方式为KV键值对的表，只含有`Key`和`Value`，通常用于全局变量
* Translate Excel Files：翻译表的名称，必须在Excel文件目录下

## 使用

## Excel格式

## 翻译表的配置

## 示例

---------------------------
Convert xls to lua script for game resource

(将xls数据文件转化为lua脚本，作为游戏资源使用)

use [python xlrd](https://pypi.python.org/pypi/xlrd)

(使用python xlrd模块)

Blog: http://www.luzexi.com

Email: jesse_luzexi@163.com

# What's this.(是什么)
This is a script to convert xls to lua.

If you use lua language , the data write in lua is the best thing for you to code.

So this script will help you convert xls to lua , so you can do your job more easily.

(如果你在使用Lua语言，将数据写进Lua文件是最方便的做法。这个脚本将帮助你将数据xls文件转化为lua文件，这样你就可以更好的工作了。)

### Declare (声明)
This script is inherit from https://github.com/zfengzhen/xls2lua .

I improve it to fit my data rule like add array type in script and remove the different talbe name in xls and so on.

Any way , you can choose one that more fit your project.

(这个脚本是从 https://github.com/zfengzhen/xls2lua 继承过来的，我改进了很多东西，也去除了很多东西，我改成了适合我自己的脚本。不管怎样，你可以选择一个适合你的脚本去运行。)

### Example（例子xls表格）
./xls/ExampleTable1.xls  

<table>
    <tr>
        <td>id</td>
        <td>name</td>
        <td>use_money</td>
        <td>use_food</td>
        <td>is_init</td>
        <td>defense</td>
        <td>args1</td>
        <td>args2</td>
        <td>args3</td>
        <td>args4</td>
        <td>args5</td>
        <td>args6</td>
        <td>args7</td>
        <td>args8</td>
    </tr>
    <tr>
        <td>int</td>
        <td>string</td>
        <td>int</td>
        <td>float</td>
        <td>bool</td>
        <td>int</td>
        <td>int[]</td>
        <td>float[]</td>
        <td>string[]</td>
        <td>bool[]</td>
        <td>Vector2</td>
        <td>Vector3</td>
        <td>Euler</td>
        <td>Color</td>
    </tr>
    <tr>
        <td>1</td>
        <td>house</td>
        <td>1000</td>
        <td>2.33</td>
        <td>TRUE</td>
        <td>100</td>
        <td>1;2;3</td>
        <td>1.23;2;3.23</td>
        <td>sdf;23e;s</td>
        <td>true;false;true</td>
        <td>-1;0.5</td>
        <td>2;0.3;-4</td>
        <td>12;23;43</td>
        <td>129;12;3;0</td>
    </tr>
    <tr>
        <td>2</td>
        <td>house2</td>
        <td>123</td>
        <td>336.2</td>
        <td>TRUE</td>
        <td></td>
        <td>1;2;3</td>
        <td>1;2.3445;3</td>
        <td>你好;你在哪</td>
        <td>true;false</td>
        <td>0;4</td>
        <td>-2;3;5</td>
        <td>0;0;0</td>
        <td>255;255;255;0</td>
    </tr>
    <tr>
        <td>3</td>
        <td></td>
        <td>456</td>
        <td>222.33665</td>
        <td>FALSE</td>
        <td>130</td>
        <td>3;2;5;;</td>
        <td>3;2;2.5;;</td>
        <td>我在这里啊;你在那;呢</td>
        <td>false;true</td>
        <td>2;0.5</td>
        <td>0.6;3;-8.4</td>
        <td></td>
        <td></td>
    </tr>
    <tr>
        <td>4</td>
        <td>farm</td>
        <td>100</td>
        <td>220</td>
        <td>FALSE</td>
        <td>200</td>
        <td>2;3;</td>
        <td>200.3;3;234.23;</td>
        <td>df;ssd;dd;dd</td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
    </tr>
    <tr>
        <td>5</td>
        <td>house5</td>
        <td></td>
        <td>22.1</td>
        <td></td>
        <td>2343;6;6;;;7</td>
        <td>3;6.3;6;;;7</td>
        <td>ss;d;d;d</td>
        <td>true;true</td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
    </tr>
    <tr>
        <td>6</td>
        <td>horse3</td>
        <td>200</td>
        <td></td>
        <td>FALSE</td>
        <td>333</td>
        <td></td>
        <td></td>
        <td>2e;w;e;we</td>
        <td>false;false;false;false</td>
        <td></td>
        <td></td>
        <td></td>
        <td></td>
    </tr>
</table>

### Excute Example (举例执行命令)
`python ./ava_xls2lua.py`

### build .exe
`build.bat`

### NOTICE:(注意点)
> The sheet name must start with "output_" , the lua file name will be the name behind "output_". <br />
> The **first row** must be **title**.  <br />
> The **second row** must be **type** <br />
> The **type** must be `int`, `float`, `sring`, `bool`, `int[]`, `float[]`, `string[]`, `bool[]`, `Vector2`, `Vector3`, `Euler`, `Color`. <br />
> i mean int , f mean float , s mean string , b mean bool , ai mean array int , af mean array float , as mean array string , ab mean array bool. <br />
> The **first column** must be int , so the type in first column must be i. <br />
> The string type with char `"` or `'` will be replace by `\"` or `\'` <br />
> The empty col will be a default value like 0 or "" or false or {} <br />
> (sheet名以"output_"开头的才会被识别转换，否则将被忽略) <br />
> (第1行必须是关键字名) <br />
> (第2行必须为类型) <br />
> (类型有：`int`, `float`, `sring`, `bool`, `int[]`, `float[]`, `string[]`, `bool[]`, `Vector2`, `Vector3`, `Euler`, `Color`) <br />
> (第1列必须为int类型的唯一关键字) <br />
> (string类型中`"`和`'`会自动用`\"`和`\'`替代)
> (空列将会被默认值代替，例如:0,"",false,{})

### Lua script (生成后的Lua文件示例)
```lua
--- This file is generated by ava-xls2lua.py,
--- Don't change it manaully.--- @copyright Lilith Games, Project Da Vinci(Avatar Team)
--- @see https://www.projectdavinci.com/
--- source file: ./xls/ExampleTable1.xls

local Example1Xls = {
    [None] = {
        id = 0,
        name = 'string',
        use_money = 0,
        use_food = 0,
        is_init = false,
        defense = 0,
        args1 = {int[]},
        args2 = {float[]},
        args3 = {'string[]'},
        args4 = {bool[]},
        args5 = Vector2(-1, 0.5),
        args6 = Vector3(2, 0.3, -4),
        args7 = EulerDegree(12, 23, 43),
        args8 = Color(129, 12, 3, 0)
    },
    [1] = {
        id = 1,
        name = 'house',
        use_money = 1000,
        use_food = 2.33,
        is_init = true,
        defense = 100,
        args1 = {1, 2, 3},
        args2 = {1.23, 2, 3.23},
        args3 = {'sdf', '23e', 's'},
        args4 = {true, false, true},
        args5 = Vector2(0, 4),
        args6 = Vector3(-2, 3, 5),
        args7 = EulerDegree(0, 0, 0),
        args8 = Color(0, 0, 0, 0)
    },
    [2] = {
        id = 2,
        name = '你好吗？',
        use_money = 123,
        use_food = 336.2,
        is_init = true,
        defense = 0,
        args1 = {1, 2, 3},
        args2 = {1, 2.3445, 3},
        args3 = {'你好', '你在哪'},
        args4 = {true, false},
        args5 = Vector2(2, 0.5),
        args6 = Vector3(0.6, 3, -8.4),
        args7 = EulerDegree(0, 0, 0),
        args8 = Color(0, 0, 0, 0)
    },
    [3] = {
        id = 3,
        name = '',
        use_money = 456,
        use_food = 222.33665,
        is_init = false,
        defense = 130,
        args1 = {3, 2, 5},
        args2 = {3, 2, 2.5},
        args3 = {'我在这里啊', '你在那', '呢'},
        args4 = {false, true},
        args5 = Vector2.Zero,
        args6 = Vector3.Zero,
        args7 = EulerDegree(0, 0, 0),
        args8 = Color(0, 0, 0, 0)
    },
    [4] = {
        id = 4,
        name = 'farm',
        use_money = 100,
        use_food = 220.0,
        is_init = false,
        defense = 200,
        args1 = {2, 3},
        args2 = {200.3, 3, 234.23},
        args3 = {'df', 'ssd', 'dd', 'dd'},
        args4 = {},
        args5 = Vector2.Zero,
        args6 = Vector3.Zero,
        args7 = EulerDegree(0, 0, 0),
        args8 = Color(0, 0, 0, 0)
    },
    [5] = {
        id = 5,
        name = 'house5',
        use_money = 0,
        use_food = 22.1,
        is_init = false,
        defense = 234,
        args1 = {3, 6, 6, 7},
        args2 = {3, 6.3, 6, 7},
        args3 = {'ss', 'd', 'd', 'd'},
        args4 = {true, true},
        args5 = Vector2.Zero,
        args6 = Vector3.Zero,
        args7 = EulerDegree(0, 0, 0),
        args8 = Color(0, 0, 0, 0)
    },
    [6] = {
        id = 6,
        name = 'horse3',
        use_money = 200,
        use_food = 0,
        is_init = false,
        defense = 333,
        args1 = {},
        args2 = {},
        args3 = {'2e', 'w', 'e', 'we'},
        args4 = {false, false, false, false},
        args5 = Vector2.Zero,
        args6 = Vector3.Zero,
        args7 = EulerDegree(0, 0, 0),
        args8 = Color(0, 0, 0, 0)
    },
}

return Example1Xls


```

### How to use lua with data. (如何使用生成的lua数据)
```lua
local Example1 = require "Example1Xls"

print(Example1[1].name)
```
The console will print `house`
