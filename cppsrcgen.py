#! /usr/bin/env python

# cppsrcgen.py
# Python script for embedding extra data into C++ code
# Author: HenryAWE <mouth11or12@outlook.com>

import argparse
import sys


parser = argparse.ArgumentParser()
parser.add_argument("--format", type=str, help="formatting string")
parser.add_argument("--text", type=str, help="text input")
parser.add_argument("--file", type=str, help="read specific file")
parsed = parser.parse_args()

if parsed.format is None:
    parser.print_help()
    sys.exit(0)


# helpers

def is_spec_ch(ch) -> bool:
    return ch == '\r' or ch == '\n' or ch == '\t' or ch == '\v'


def convert_spec_ch(ch) -> str:
    if ch == '\r':
        return "\\r"
    if ch == '\n':
        return "\\n"
    if ch == '\t':
        return "\\t"
    if ch == '\v':
        return "\\v"


def translate_str(src: str, replace_nonascii: bool, quoted: bool, convert_spec: bool, raw: bool) -> str:
    dst = ""
    for i in src:
        if replace_nonascii:
            # non-ASCII
            if ord(i) > 0x7F:
                cp = ord(i)
                # 16-bit
                if cp <= 0xffff:
                    dst += "\\u{:04x}".format(cp)
                    continue
                # 32-bit
                else:
                    dst += "\\U{:08x}".format(cp)
                    continue
        if convert_spec and is_spec_ch(i):
            dst += convert_spec_ch(i)
            continue
        if raw:
            if i == '\\':
                dst += "\\\\"
                continue
            elif i == '"':
                dst += "\\\""
                continue
        # else:
        dst += i

    if quoted:
        return '"' + dst + '"'
    else:
        return dst


class string_formatter:
    def __init__(self, replace_nonascii=False, quoted=False, convert_spec=False, raw=False):
        self.replace_nonascii = replace_nonascii
        self.quoted = quoted
        self.convert_spec = convert_spec
        self.raw = raw

    def format(self, input: str) -> str:
        return translate_str(
            input,
            replace_nonascii=self.replace_nonascii,
            quoted=self.quoted,
            convert_spec=self.convert_spec,
            raw=self.raw
        )

    @staticmethod
    def parse(spec: str):
        """Parse string formatting specifier, returning None when specifier is invalid"""
        result = string_formatter()
        proc = spec
        if proc.startswith('q'):
            result.quoted = True
            proc = proc[1:]
        if proc.startswith('u'):
            result.replace_nonascii = True
            proc = proc[1:]
        if proc.startswith('e'):
            result.convert_spec = True
            proc = proc[1:]
        if proc.startswith('r'):
            result.raw = True
            result.replace_nonascii = True
            result.convert_spec = True
            proc = proc[1:]

        if len(proc) != 0:
            return None
        return result


class text_fmt_spec:
    def __init__(self, spec: str):
        self.mode = 't'
        self.string = string_formatter.parse(spec)
        if self.string is None:
            self.raise_error(spec)

    @staticmethod
    def raise_error(spec):
        raise ValueError(
            "Unknown format code '{}' for class text".format(spec))


class text:
    def __init__(self, txt):
        if txt is None:
            self.txt = ""
        else:
            self.txt = str(txt)

    def __format__(self, spec: str) -> str:
        formatter = text_fmt_spec(spec)
        return formatter.string.format(self.txt)


class bin_format_spec:
    def __init__(self, spec: str):
        # hex (default)
        if spec == "":
            self.mode = 'x'
            self.sep = ","
            return
        if spec[0] == 'x':
            self.mode = 'x'
            if len(spec) > 1:
                self.sep = spec[1:]
            else:
                self.sep = ","
            return
        # text
        elif spec[0] == 't':
            self.mode = 't'
            self.string = string_formatter.parse(spec[1:])
            if self.string is None:
                self.raise_error(spec)
            return
        # unknown formatting specifier
        self.raise_error(spec)

    @staticmethod
    def raise_error(spec):
        raise ValueError(
            "Unknown format code '{}' for class binaryen".format(spec))


class file_reader:
    def __init__(self, path):
        self.path = path

    def read_hex(self, sep=",") -> str:
        if self.path is None:
            return ""
        f = open(self.path, "rb")
        buf = f.read()
        result = ""
        first = True
        for i in buf:
            if first:
                first = False
            else:
                result += sep
            result += "0x{:02x}".format(i)
        return result

    def read_text(self) -> str:
        if self.path is None:
            return ""
        f = open(self.path, "r", encoding="utf-8")
        return f.read()

    def __format__(self, spec: str) -> str:
        formatter = bin_format_spec(spec)
        if formatter.mode == 'x':
            return self.read_hex(formatter.sep)
        elif formatter.mode == 't':
            return formatter.string.format(self.read_text())


# output

file = file_reader(parsed.file)
txt = text(parsed.text)

print(parsed.format.format(text=txt, file=file))
