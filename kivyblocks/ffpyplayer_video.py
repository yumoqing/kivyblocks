
from traceback import print_exc
import time
import numpy as np
from ffpyplayer.player import MediaPlayer
from ffpyplayer.tools import set_log_callback

from kivy.factory import Factory
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.properties import StringProperty, BooleanProperty, \
			OptionProperty, NumericProperty
from kivy.graphics.texture import Texture
from kivy.graphics import Color, Line
from kivyblocks.ready import WidgetReady
from kivyblocks.baseWidget import Running
from kivyblocks.videobehavior import VideoBehavior

vhks = ['v_src', 
		'play_mode', 
		'header_callback',
		'audio_id',
		'duration',
		'position',
		'volume',
		'timeout',
		'in_center_focus',
		'renderto',
		'auto_play',
		'repeat'
]

class FFVideo(WidgetReady, VideoBehavior, BoxLayout):
	def __init__(self, **kw):
		kw1 = {k:v for k,v in kw.items() if k in vhks}
		kw1['renderto'] = 'background'
		kw2 = {k:v for k,v in kw.items() if k not in vhks}
		kw2['orientation'] = 'vertical'
		BoxLayout.__init__(self, **kw2)
		VideoBehavior.__init__(self, **kw1)
		WidgetReady.__init__(self)

	def show_info(self, o, d):
		txt = f"size={d['size']}, vpos={d['pos']}, vsize={d['texture_size']}"
		self.msg_w.text = txt

