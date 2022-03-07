
from ffpyplayer.player import MediaPlayer
from threading import Thread
from kivy.core.video.video_ffpyplayer import VideoFFPy

headers_pattern = {
}

def set_headers_pattern(pattern, headers_str):
	headers_pattern[pattern] = headers_str

def get_spec_headers(filename):
	for p in headers_pattern.keys():
		if p in filename:
			return headers_pattern[p]
	return None

def hack_play(self):
	print('****************')
	print('****************')
	print('hack_play() called ...')
	if self._ffplayer and self._state == 'paused':
		self._ffplayer.toggle_pause()
		self._state = 'playing'
		return

	self.load()
	self._out_fmt = 'rgba'
	ff_opts = {
		'paused': True,
		'out_fmt': self._out_fmt,
		'sn': True,
		'volume': self._volume,
	}
	if self._filename.startswith('http://') or \
			self._filename.startswith('https://'):
		headers = get_spec_headers(self._filename)
		if headers is not None:
			ff_opts['headers'] = "$'%s'" % headers
			print('****************')
			print('*VideoFFPy():ff_opts=', ff_opts)
			print('****************')

	self._ffplayer = MediaPlayer(
			self._filename, callback=self._player_callback,
			thread_lib='SDL',
			loglevel='info', ff_opts=ff_opts)

	# Disabled as an attempt to fix kivy issue #6210
	# self._ffplayer.set_volume(self._volume)

	self._thread = Thread(target=self._next_frame_run, name='Next frame')
	self._thread.daemon = True
	self._thread.start()

# setattr(VideoFFPy, 'play', hack_play)
