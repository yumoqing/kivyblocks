# -*- coding: utf-8 -*-

try:
	from setuptools import setup
except ImportError:
	from distutils.core import setup
# from Cython.Build import cythonize

with open('kivyblocks/version.py', 'r') as f:
	x = f.read()
	y = x[x.index("'")+1:]
	z = y[:y.index("'")]
	version = z
with open("README.md", "r") as fh:
    long_description = fh.read()


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
		# 'image_processing/cascades/haarcascade_frontalface_default.xml',
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
	long_description=long_description,
	long_description_content_type="text/markdown",
    author=author,
    author_email=email,
   
    install_requires=[
	"kivy",
	"appPublic",
	"sqlor"
    ],
    packages=[
		'kivyblocks',
		# 'kivyblocks.image_processing',
		'kivyblocks.mapview',
		'kivyblocks.uitype',
		'kivyblocks.widgetExt'
		# 'kivyblocks.xcamera'
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
