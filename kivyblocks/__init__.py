import os
from kivy.logger import logging
__version_info__ = "0.5.0"
from .version import __version__

path = os.path.dirname(__file__)
fonts_path = os.path.join(path,"ttf/")
images_path = os.path.join(path,'imgs/')
logging.info("kivyblocks:kivblocks version:{}".format(__version__))
