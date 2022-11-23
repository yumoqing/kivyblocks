
from traceback import print_exc
import time
import numpy as np
from ffpyplayer.player import MediaPlayer
from ffpyplayer.tools import set_log_callback

from kivy.factory import Factory
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.properties import StringProperty, BooleanProperty, \
			OptionProperty, NumericProperty
from kivy.graphics.texture import Texture
from kivy.graphics import Color, Line, Rectangle
from kivyblocks.ready import WidgetReady
from kivyblocks.baseWidget import Running

class VideoBehavior(object):
	v_src = StringProperty(None)
	status = OptionProperty('stop', \
			options=['stop', 'play', 'pause'])
	play_mode = OptionProperty('normal', \
			options=['normal', 'preview', 'audioonly'])
	header_callback = StringProperty(None)
	audio_id = NumericProperty(None)
	duration = NumericProperty(-1)
	position = NumericProperty(-1)
	volume = NumericProperty(-1)
	timeout = NumericProperty(5)
	auto_play=BooleanProperty(True)
	repeat=BooleanProperty(False)
	in_center_focus = BooleanProperty(False)
	renderto = OptionProperty('foreground', options=['background', 'foreground', 'cover'])

	def __init__(self, **kwargs):
		self._player = None
		self.change_size_task = None
		self._update_task = None
		self.running = None
		self.vh_task = None
		self.is_black = False
		self.videosize = None
		self.ff_opts = {
			"framedrop":True
		}
		self.lib_opts = {}
		self.headers_pattern = {}
		# self.set_black()
		self.start_task = None
		self.block_task = None
		self.register_event_type('on_frame')
		self.register_event_type('on_open_failed')
		self.register_event_type('on_leave_focus')
		self.register_event_type('on_enter_focus')
		self.register_event_type('on_load_success')
		self.register_event_type('on_startplay')
		self.bind(size=self.set_video_size)
		# self.bind(parent=self.stop_when_remove)
		for k, v in kwargs.items():
			setattr(self, k, v)

	def video_blocked(self, *args):
		self._play_stop()
		self.on_v_src(None, None)

	def on_open_failed(self, source):
		print(f'{source} open failed')

	def on_load_success(self, *args):
		pass

	def on_enter_focus(self, *args):
		pass

	def on_leave_focus(self, *args):
		pass

	def check_focus(self,*args):
		if not self.parent:
			self.in_center_screen = False
			return
		if not self.get_root_window():
			self.in_center_screen = False

		w = self.parent
		pos = w.to_widget(*Window.center)
		if self.collide_point(*pos):
			self.in_center_screen = True
		else:
			self.in_center_screen = False

	def set_ff_opt(self, k,v):
		self.ff_opts.update({k:v})

	def set_lib_opt(self, k, v):
		self.lib_opts.update({k:v})

	def set_pattern_header(self, pattern, k,v):
		dic = self.headers_pattern.get(pattern,{})
		dic.update({k:v})
		self.headers_pattern[pattern] = dic

	def _get_spec_headers(self, filename):
		for p in self.headers_pattern.keys():
			if filename.startswith(p):
				headers = self.headers_pattern[p]
				headers_str = ''.join([f'{k}:{v}\r\n' for k,v in headers.items()])
				return headers_str
		return None

	def on_volume(self, *args):
		if self._player is None:
			return

		self._player.set_volume(self.volume)
		
	def on_status(self, *args):
		print('on_status called, ', self.status)
		if self._player is None:
			print('no _player, do nothing')
			return

		Window.allow_screensaver = True
		if self.status == 'play':
			Window.allow_screensaver = False
			self._player.set_pause(False)
			self.video_handle()
		elif self.status == 'pause':
			self._player.set_pause(True)
		elif self.status == 'stop':
			self._play_stop()
		else:
			pass

	def stop_when_remove(self, *args):
		if self.parent:
			return
		self._play_stop()

	def on_startplay(self, *args):
		pass

	def on_frame(self, *args):
		return

	def __del__(self):
		self._play_stop()

	def set_volume(self, v):
		if self.play_mode == 'preview':
			return
		if self._player is None:
			return
		if self.status != 'play':
			return
		if v > 1.0:
			v = 1.0
		if v < 0.0:
			v = 0.0
		self.volume = v

	def seek(self, pts):
		self.vsync = False
		if self.play_mode == 'preview':
			return
		if self._player is None:
			return
		if self.status != 'play':
			return
		self._player.seek(pts, relative=False)
		self.position = self._player.get_pts()
		self.last_val = None

	def mute(self, flag=None):
		if self.play_mode == 'preview':
			return
		if self._player is None:
			return
		if self.status != 'play':
			return
		x = self._player.get_mute()
		print('Video(), mute=', x)
		self._player.set_mute(not x)
		
	def switch_audio(self):
		if self.play_mode == 'preview':
			return
		if self._player is None:
			return
		if self.status != 'play':
			return
		self._player.request_channel('audio', action='cycle')

	def on_v_src(self, o, src):
		self.status = 'stop'
		ff_opts = {
			'pause':False
		}
		if self.play_mode == 'preview':
			ff_opts['lowres'] = 2 # 1/4 size
			ff_opts['an'] = True
		elif self.play_mode == 'audioonly':
			ff_opts['vn'] = True
		ff_opts.update(self.ff_opts)
		lib_opts = {
		}
		lib_opts.update(self.lib_opts)
		heads = self._get_spec_headers(self.v_src)
		if heads:
			lib_opts.update({'headers':heads})
			# ff_opts.update({'headers':heads})

		self._player = MediaPlayer(self.v_src, ff_opts=ff_opts, \
						lib_opts=lib_opts) 
		self.playing = False
		if self.auto_play:
			self.play()

	def open_failed(self, *args):
		self.dispatch('on_open_failed', self.v_src)

	def on_open_failed(self, source):
		print(f'{source} open failed')

	def file_opened(self, files):
		self.v_src = files[0]

	def play(self):
		if self._player is None:
			return
		self.status = 'play'
		self.start_task = Clock.schedule_once(self.open_failed, self.timeout)

	def pause(self):
		if self._player is None:
			return
		self.status = 'pause'

	def _get_video_info(self):
		meta = self._player.get_metadata()
		self.duration = meta['duration']
		self._out_fmt = meta['src_pix_fmt']
		self.frame_rate = meta['frame_rate']
		self.videosize = meta['src_vid_size']

	def _play_stop(self):
		if self._player:
			self._player.close_player()
			self._player = None
		if self._update_task:
			self._update_task.cancel()
			self._update_task = None
		if self.vh_task:
			self.vh_task.cancel()
			self.vh_task = None
		if self.start_task:
			self.start_task.cancel()
			self.start_task = None
		if self.block_task:
			self.block_task.cancel()
			self.block_task = None
		self.next_frame = None
		self.duration = -1
		self.position = 0
		self.videosize = None
		
	def set_video_size(self, *args):
		if self.change_size_task:
			self.change_size_task.cancel()
		self.change_size_task = Clock.schedule_once(self._set_video_size, 0.1)
	def _set_video_size(self, *args):
		if self._player is None:
			return
		if self.videosize == None:
			return
		w, h = self.videosize
		r = w / h
		r1 = self.width / self.height
		# position = self.position
		if r1 >= r:
			self._player.set_size(-1, self.height)
		else:
			self._player.set_size(self.width, -1)
		# self.seek(position)
		# print('_set_video_size():position=', position)

	def set_black(self):
		if self.is_black:
			return
		image_texture = Texture.create(
            size=self.size, colorfmt='rgb')
		buf = b'\x33' * int(self.width * self.height * 3)
		image_texture.blit_buffer(buf, colorfmt='rgb', bufferfmt='ubyte')
		self._my_show_texture(image_texture, *self.size)
		self.is_black = True

	def show_yuv420(self, img):
		w, h = img.get_size()
		w2 = int(w / 2)
		h2 = int(h / 2)
		self._tex_y = Texture.create(
			size=(w, h), colorfmt='luminance')
		self._tex_u = Texture.create(
			size=(w2, h2), colorfmt='luminance')
		self._tex_v = Texture.create(
			size=(w2, h2), colorfmt='luminance')
		self._fbo = fbo = Fbo(size=(w, h))
		with fbo:
			BindTexture(texture=self._tex_u, index=1)
			BindTexture(texture=self._tex_v, index=2)
			Rectangle(size=fbo.size, texture=self._tex_y)
		fbo.shader.fs = VideoFFPy.YUV_RGB_FS
		fbo['tex_y'] = 0
		fbo['tex_u'] = 1
		fbo['tex_v'] = 2
		dy, du, dv, _ = img.to_memoryview()
		if dy and du and dv:
			self._tex_y.blit_buffer(dy, colorfmt='luminance')
			self._tex_u.blit_buffer(du, colorfmt='luminance')
			self._tex_v.blit_buffer(dv, colorfmt='luminance')
			self._fbo.ask_update()
			self._fbo.draw()
		texture.flip_vertical()
		self.my_show_texture(texture, w, h)
		# self.texture = texture

	def show_others(self, img):
		w, h = img.get_size()
		texture = Texture.create(size=(w, h), colorfmt='rgb')
		texture.blit_buffer(
				img.to_memoryview()[0], colorfmt='rgb',
				bufferfmt='ubyte')
		texture.flip_vertical()
		self.my_show_texture(texture, w, h)
		# self.texture = texture
		# print('img_size=', w, h, 'window size=', self.size)

	def my_show_texture(self, texture, w, h):
		d = self._my_show_texture(texture, w, h)
		if d:
			self.dispatch('on_frame', d)

	def _my_show_texture(self, texture, w, h):
		if self.width == 100 and self.height== 100:
			return
		if abs(self.width - w) > 1 and abs(self.height - h) > 1:
			self._set_video_size()
		if w > self.width:
			w = self.width
		if h > self.height:
			h = self.height
		canvas = self.canvas
		if self.renderto == 'background':
			canvas = self.canvas.before
		elif self.renderto == 'cover':
			canvas = self.canvas.after
		p = 0
		if self.duration > 0:
			p = self.position / self.duration * self.width
		pos = (self.width - w)/2, (self.height - h)/2
		canvas.clear()
		with canvas:
			Rectangle(texture=texture, pos=pos, size=(w, h))
			Color(1,1,1,1)
			Line(points=[0, 1, self.width, 1], width=2)
			Color(1,0,0,1)
			Line(points=[1,1,p,1], width=2)
			# Color(1,1,0,1)
			# Line(rectangle=[0,0, self.width, self.height], width=4)
		d = {
			'texture':texture,
			'position':self.position,
			'duration':self.duration,
			'pos':pos,
			'texture_size':(w, h),
			'size':self.size
		}
		return d

	def video_handle(self, *args):
		if self._update_task:
			self._update_task.cancel()
			self._update_task = None
		if self._player is None:
			return 
		frame, val = self._player.get_frame()
		if val == 'eof':
			if self.repeat:
				self.seek(0)
				self.play()
				return
			self.status = 'stop'
			# self.set_black()
			self.last_val = None
			return
		if val == 'pause':
			self.status = 'pause'
			self.last_val = None
			return
		if frame is None:
			# self.set_black()
			self.last_val = None
			self.vh_task = Clock.schedule_once(self.video_handle, 0.1)
			return

		self.last_frame = frame
		self.video_ts = val
		if self.last_val is None:
			self.last_val = val
			self._update_task = Clock.schedule_once(self.do_update, 0)
		else:
			t = val - self.last_val
			if t > 0:
				self._update_task = Clock.schedule_once(self.do_update, t)
			else:
				self._update_task = Clock.schedule_once(self.do_update, 0)

	def do_update(self, *args):
		if self.start_task:
			self.start_task.cancel()
			self.start_task = None
		if self.block_task:
			self.block_task.cancel()
		if not self.playing:
			self.playing = True
			self._get_video_info()
			self.dispatch('on_startplay')
		self.position = self._player.get_pts()
		self.volume = self._player.get_volume()
		img, t = self.last_frame
		if self._out_fmt == 'yuv420p':
			self.show_yuv420(img)
		else:
			self.show_others(img)
		self.last_frame = None
		self.vh_task = Clock.schedule_once(self.video_handle, 0)
		self.block_task = Clock.schedule_once(self.video_blocked, self.timeout)
		
