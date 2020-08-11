#!/usr/bin/env python
#-*- coding:utf-8 -*-

#############################################
# File Name: setup.py
# Author: liuzw
# Mail: helloliuzw@163.com
# Created Time:  2020-8-11 17:35:34
#############################################

from setuptools import setup, find_packages

setup(
    name = "SZlabeler",
    version = "0.0.5",
    keywords = ["pip", "shorttext","rule","career"],
    description = "A rule-based toolkit for resume classification",
    long_description = "A rule-based toolkit for resume classification, applied in ShenZhen",
    license = "MIT Licence",

    url = "https://github.com/helloliuzw/parser",
    author = "liuzw",
    author_email = "helloliuzw@163.com",

    packages = ['SZlabeler'],
    include_package_data = True,
    platforms = "any",
    install_requires = []
)

