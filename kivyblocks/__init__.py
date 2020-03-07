import os
from kivy import logger
__version_info__ = (0.5.0)
__version__ = '0.5.0'

path = os.path.dirname(__file__)
fonts_path = os.path.join(path,"ttf/")
images_path = os.path.join(path,'imgs/')
logger.info("kivyblocks:kivblocks version:{}".format(__version__)
