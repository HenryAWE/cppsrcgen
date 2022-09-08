[English](README.md) **简体中文**

# CppSrcGen
## 简介
用于生成嵌入外部数据到 C++ 代码的 Python 脚本

## 参数
- `--format FORMAT`：格式化字符串（见下文）
- `--text TEXT`：将 TEXT 作为字符串输入
- `--file FILE`：读取指定文件

## 格式化字符串
基础语法和 Python 的 `format` 相同  
命令行参数中输入的数据可以使用参数名引用
### `text`：`--text` 参数所输入的字符串
``` BNF
<文本格式化说明> ::= ["q"]["u"]["e"]["r"]
```
- `"q"`：输出的字符串将会被引号包裹
- `"u"`：将非 ASCII 字符用转义序列表示  
  其中，小于等于 0xFFFF 的会被转化为 `\unnnn` 的形式（如“我”会被转化为 `\u6211`）；大于 0xFFFF 的会被转化为 `\Unnnnnnnn`
- `"e"`：将文本中的特殊字符用转义序列表示。如换行符会被转化为 `\n`
- `"r"`：按照原始字符串输出，保证字符串的内容不受 C++ 语法影响。  
  该选项会同时设置 `"u"` 与 `"e"` 选项，并将 `"` 和 `\` 分别转化为 `\"` 和 `\\`
### `file`：从 `--file` 所指定的文件中读取的数据
``` BNF
<文件格式化说明> ::= ["x"[分隔符]|"t"["q"]["u"]["e"]["r"]]
<分隔符>        ::= <任意字符>+
```
- `"x"` （默认）：以十六进制数字（`0xNN`）输出字节
- `分隔符`：默认分隔符为 `,` 。若要指定 `;` 为分隔符，则对应的格式化参数是 `x;`
- `"t"`：使用 UTF-8 编码，以文本的形式输出  
  **注意：这个模式会自动转换源文件中的换行符**  
- `"u"`、`"e"`、`"r"`：同 `text` 中的对应参数

## 示例
### 1、输出文本数据
参数：`--format "const char* hello = {text:q}" --text "hello world!"`  
输出：
``` c++
const char* hello = "hello world!"
```
### 2、非 ASCII 文本数据
参数：`--format "{text:qu}" --text "Chinese 你好世界"`  
输出：
``` c++
"Chinese \u4f60\u597d\u4e16\u754c"
```
参数：`--format "{text:qu}" --text "🔈🔉🔊"`  
**注意：部分命令行可能不支持输入或显示大于 0xFFFF 的字符**  
输出：
``` c++
"\U0001f508\U0001f509\U0001f50a"
```
### 3、读取文件，并输出原始字符串
参数：`--format "{file:tqr}" --file "examples\new line.txt"`  
输出：
``` c++
"first line\nsecond line"
```
参数：`--format "{file:tqr}" --file "examples\nonascii.txt"`  
输出：
``` c++
"non-ASCII characters\ncaf\u00e9\n\u6d4b\u8bd5\n\u30c6\u30b9\u30c8"
```
### 4、读取文件，并输出十六进制数
参数：`--format "char arr[] = {{{file:x}}};" --file "examples\new line.txt"`  
可能的输出：
``` c++
char arr[] = {0x66,0x69,0x72,0x73,0x74,0x20,0x6c,0x69,0x6e,0x65,0x0a,0x73,0x65,0x63,0x6f,0x6e,0x64,0x20,0x6c,0x69,0x6e,0x65};
```
**注意：如果你的 git 设置了自动转换行尾，输出可能会有不同**
