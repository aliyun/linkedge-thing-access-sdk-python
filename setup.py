#!/usr/bin/env python

from setuptools import setup  

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
