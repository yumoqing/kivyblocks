# -*- coding: utf-8 -*-


try:
	from setuptools import setup
except ImportError:
	from distutils.core import setup
from Cython.Build import cythonize

# usage:
# python setup.py bdist_wininst generate a window executable file
# python setup.py bdist_egg generate a egg file
# Release information about eway

version = "0.1.5"
description = "kivy blocks is a tool to build kivy ui with json format uidesc files"
author = "yumoqing"
email = "yumoqing@icloud.com"

package_data = {
	"kivyblocks":[
		'imgs/*.png', 
		'imgs/*.atlas', 
		'imgs/*.gif',
		'imgs/*.jpg',
		'ttf/*.ttf', 
		'ui/*.uidesc',
		'xcamera/xcamera.kv',
		'image_processing/cascades/haarcascade_frontalface_default.xml',
		'xcamera/data/*'
	],
}

setup(
    name="kivyblocks",
	# ext_modules= cythonize( [ ]),
	ext_modules= [],
    version=version,
    # uncomment the following lines if you fill them out in release.py
    description=description,
    author=author,
    author_email=email,
   
    install_requires=[
	"kivy",
	"appPublic",
	"sqlor"
    ],
    packages=[
		'kivyblocks',
		'kivyblocks.image_processing',
		'kivyblocks.mapview',
		'kivyblocks.uitype',
		'kivyblocks.widgetExt',
		'kivyblocks.xcamera'
	],
    package_data=package_data,
    keywords = [
    ],
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
	platforms= 'any'
)
