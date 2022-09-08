**English** [简体中文](README.zh-CN.md)

# CppSrcGen
## Introduction
Python script for embedding extra data into C++ code

## Arguments
- `--format FORMAT`: Formatting string (see below)
- `--text TEXT`: Input TEXT as string
- `--file FILE`: Read the specific file

## Formatting String
Basic syntax is as same as `format` of Python.  
The inputs from command line can be referred by named replacement fields.
### `text`: String Input by `--text` Argument
``` BNF
<text-format-spec> ::= ["q"]["u"]["e"]["r"]
```
- `"q"`: The output will be quoted by quotation marks (`"`)
- `"u"`: Converting non-ASCII characters into escape sequences  
  The characters lesser than 0xFFFF will be converted to the form of `\unnnn`, while characters greater than 0xFFFF will be converted to `\Unnnnnnnn`
- `"e"`：Converting special characters in text to escape sequences. For example, a newline will be converted to `\n`
- `"r"`: Output as raw string, preventing the content of string from being modified by C++ syntax.  
  This option will turn on `"u"` and `"e"` at the same time. In addition, it will convert `"` and `\` to `\"` and `\\`, respectively.
### `file`: Data read from file specified by `--file`
``` BNF
<file-format-spec> ::= ["x"[separator]|"t"["q"]["u"]["e"]["r"]]
<separator>        ::= <any character>+
```
- `"x"` (Default): Output bytes as hexadecimal numbers (`0xNN`)
- `separator`: Default separator is `,` . If you want to set `;` as separator, the complete format specifier will be `x;`
- `"t"`: Output text using UTF-8 encoding.  
  *Note: The line endings will be automatically converted in this mode`*  
- `"u"`, `"e"`, `"r"`: Same as the corresponding arguments in `text`

## Examples
### 1. Output text data
Arguments: `--format "const char* hello = {text:q}" --text "hello world!"`  
Output:
``` c++
const char* hello = "hello world!"
```
### 2. Non-ASCII text data
Arguments: `--format "{text:qu}" --text "café"`  
Output:
``` c++
"caf\u00e9"
```
Arguments: `--format "{text:qu}" --text "🔈🔉🔊"`  
*Note: Some command line may not support inputting or displaying characters greater than 0xFFFF*  
Output:
``` c++
"\U0001f508\U0001f509\U0001f50a"
```
### 3. Read file and output it in raw string
Arguments: `--format "{file:tqr}" --file "examples\new line.txt"`  
Output:
``` c++
"first line\nsecond line"
```
Arguments: `--format "{file:tqr}" --file "examples\nonascii.txt"`  
Output:
``` c++
"non-ASCII characters\ncaf\u00e9\n\u6d4b\u8bd5\n\u30c6\u30b9\u30c8"
```
### 4. Read file and output hexidecimal numbers
Arguments: `--format "char arr[] = {{{file:x}}};" --file "examples\new line.txt"`  
Possible output:
``` c++
char arr[] = {0x66,0x69,0x72,0x73,0x74,0x20,0x6c,0x69,0x6e,0x65,0x0a,0x73,0x65,0x63,0x6f,0x6e,0x64,0x20,0x6c,0x69,0x6e,0x65};
```
*Note: If your git is set to automatically convert line endings, the output may be different*
