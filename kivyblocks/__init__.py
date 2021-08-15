import os
from kivy.logger import logging
__version_info__ = "0.5.0"
__version__ = '0.5.0'

path = os.path.dirname(__file__)
fonts_path = os.path.join(path,"ttf/")
images_path = os.path.join(path,'imgs/')
logging.info("kivyblocks:kivblocks version:{}".format(__version__))
