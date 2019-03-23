#!/usr/bin/env python

from setuptools import setup  
import sys


if not (sys.version_info[0] == 3 and sys.version_info[1] == 5 and sys.version_info[2] == 2):
    sys.exit("Link IoT Edge only support Python 3.5.2")

setup(  
    name = "lethingaccesssdk",
    version = "1.0",
    description = "Link IoT Edge Thing Access SDK for Function Compute",
    license = "Apache 2.0",
  
    url = "https://help.aliyun.com/product/69083.html?spm=a2c4g.11186623.6.540.66bd71b80FSb2h",
    packages = ['lethingaccesssdk'],
    include_package_data = True,
    platforms = "any",
    install_requires = [
        'setuptools>=16.0',
    ],
  
    scripts = [],
    entry_points = {
        'console_scripts': [
        ]
    }
)
