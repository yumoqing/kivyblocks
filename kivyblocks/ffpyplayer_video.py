
import time
import numpy as np
from ffpyplayer.player import MediaPlayer
from ffpyplayer.tools import set_log_callback

from kivy.factory import Factory
from kivy.app import App
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.properties import StringProperty, BooleanProperty, \
			OptionProperty, NumericProperty
from kivy.graphics.texture import Texture
from kivy.graphics import Color, Line
from kivyblocks.ready import WidgetReady


class FFVideo(WidgetReady, Image):
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
	framerate = NumericProperty(180)
	in_center_focus = BooleanProperty(False)

	def __init__(self, **kwargs):
		self._player = None
		self._volume = 0
		self._position = 0
		self._update_task = None
		self._texture = None
		self.is_black = False
		self.videosize = None
		self.timeperiod = 1.0 / self.framerate
		self.ff_opts = {}
		self.lib_opts = {}
		self.headers_pattern = {}
		super(FFVideo, self).__init__(**kwargs)
		self.set_black()
		self.register_event_type('on_frame')
		self.register_event_type('on_open_failed')
		self.register_event_type('on_leave_focus')
		self.register_event_type('on_enter_focus')
		self.register_event_type('on_load_success')
		self.register_event_type('on_startplay')

	def on_open_failed(self, *args):
		pass

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
		self._volume = self.volume
		
	def on_status(self, *args):
		print('on_status called, ', self.status)
		if self._player is None:
			return

		if self.status == 'play':
			self._player.set_pause(False)
		elif self.status == 'pause':
			self._player.set_pause(True)
		elif self.status == 'stop':
			self._play_stop()
		else:
			pass

	def on_parent(self, *args):
		if self.parent:
			return
		self._play_stop()
		del self

	def on_startplay(self, *args):
		pass

	def on_frame(self, *args):
		if self._player is None:
			return
		if not self.playing:
			self.dispatch('on_startplay')
			self._player.request_channel( \
								'audio', 'open', self.audio_id)
			self.seek(self.position)
			self.playing = True
		if self.duration > 0:
			p = self._position / self.duration * self.width
			self.canvas.after.clear()
			with self.canvas.after:
				Color(1,1,1,1)
				Line()
				Line(points=[0, 0, self.width, 0], width=1)
				Color(1,0,0,1)
				Line(points=[0,1,p,1], width=1)
		self.position = self._position

	def __del__(self):
		if self._update_task:
			self._update_task.cancel()
			self._update_task = None
		if self._player:
			self._player.close_player()
			self._player = None

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
		if self.play_mode == 'preview':
			return
		if self._player is None:
			return
		if self.status != 'play':
			return
		self._player.seek(pts, relative=False)
		self.last_frame, self.timepass = self._player.get_frame()
		self._position = self._player.get_pts()

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
		self._play_stop()
		self.playing = False

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
			ff_opts.update({'headers':heads})

		print('ff_opts=', ff_opts)
		print('lib_opts=', lib_opts)
		# self._player = MediaPlayer(self.v_src) 
		self._player = MediaPlayer(self.v_src, ff_opts=ff_opts, \
						lib_opts=lib_opts) 
		self._play_start()

	def file_opened(self, files):
		self.v_src = files[0]

	def play(self):
		if self._player is None:
			return
		# self._player.set_pause(False)
		self.status = 'play'

	def pause(self):
		if self._player is None:
			return
		# self._player.set_pause(True)
		self.status = 'pause'

	def _play_start(self):
		self.timepass = 0.0
		self.last_frame = None
		self.is_black = False
		self._update_task = Clock.schedule_interval(self._update, self.timeperiod)

	def _get_video_info(self):
		if not self.playing:
			meta = self._player.get_metadata()
			self.duration = meta['duration']
			self._out_fmt = meta['src_pix_fmt']
			self.frame_rate = meta['frame_rate']
			self.videosize = meta['src_vid_size']

	def _play_stop(self):
		if self._player is None:
			return
		self._update_task.cancel()
		self._update_task = None
		self._player.close_player()
		self._player = None
		self.timepass = 0
		self.next_frame = None
		self.duration = -1
		self.position = 0
		self.frame_rate = None
		self.videosize = None
		
	def on_size(self, *args):
		if self._player is None:
			return
		if self.videosize == None:
			return
		w, h = self.videosize
		r = w / h
		r1 = self.width / self.height
		if r1 >= r:
			self._player.set_size(-1, self.height)
		else:
			self._player.set_size(self.width, -1)

	def set_black(self):
		if self.is_black:
			return
		image_texture = Texture.create(
            size=self.size, colorfmt='rgb')
		buf = b'\x00' * int(self.width * self.height * 3)
		image_texture.blit_buffer(buf, colorfmt='rgb', bufferfmt='ubyte')
		self.texture = image_texture
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
		self._texture = fbo.texture
		dy, du, dv, _ = img.to_memoryview()
		if dy and du and dv:
			self._tex_y.blit_buffer(dy, colorfmt='luminance')
			self._tex_u.blit_buffer(du, colorfmt='luminance')
			self._tex_v.blit_buffer(dv, colorfmt='luminance')
			self._fbo.ask_update()
			self._fbo.draw()
		texture.flip_vertical()
		self.texture = texture

	def show_others(self, img):
		w, h = img.get_size()
		texture = Texture.create(size=(w, h), colorfmt='rgb')
		texture.blit_buffer(
				img.to_memoryview()[0], colorfmt='rgb',
				bufferfmt='ubyte')
		texture.flip_vertical()
		self.texture = texture
		# print('img_size=', w, h, 'window size=', self.size)

	def _update(self, dt):
		if self.last_frame is None:
			frame, val = self._player.get_frame()
			if val == 'eof':
				self.status = 'stop'
				self.set_black()
				return
			if val == 'pause':
				self.status = 'pause'
				return
			if frame is None:
				self.set_black()
				return
			self.last_frame = frame
			self.video_ts = val
			self._get_video_info()
			
		self.timepass += self.timeperiod
		self._position = self._player.get_pts()
		self._volume = self._player.get_volume()
		if self.timepass < self.video_ts:
			return

		if self.timepass > self.video_ts +0.2:
			self.last_frame = None
			return

		self.status = 'play'
		img, t = self.last_frame
		if self._out_fmt == 'yuv420p':
			self.show_yuv420(img)
		else:
			self.show_others(img)
		self.dispatch('on_frame', self.last_frame)
		self.last_frame = None

