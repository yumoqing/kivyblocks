import os
import kivy
import kivyblocks
from kivy.config import Config
from kivy.resources import resource_add_path
resource_add_path(os.path.join(os.path.dirname(kivyblocks.__file__),'./ttf'))
Config.set('kivy', 'default_font', [
        'msgothic',
        'DroidSansFallback.ttf'])

config_set = True
