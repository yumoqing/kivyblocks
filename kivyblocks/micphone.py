from threading import Thread, Lock
import pyaudio
from kivy.event import EventDispatcher
from kivy.properties import NumericProperty, ObjectProperty
from kivy.clock import Clock
import wave
CHUNK = 1024
CHANNELS = 2
FORMAT = pyaudio.paInt16
samplerate = 48000

class Micphone(EventDispatcher):
	channels = NumericProperty(2)
	samplerate = NumericProperty(48000)
	fps = NumericProperty(1/60)
	def __init__(self, **kw):
		super(Micphone, self).__init__(**kw)
		self.chunk = CHUNK
		self.format = pyaudio.Int16
		self.chunk_buffer = []
		self.lock = Lock()
		self.recoding = False
		self._audio = puaudio.PyAudio()
		self._mic = p.open(format=self.format,
					channels=self.channels,
					rate=self.samplerate,
					input=True,
					frames_per_buffer=self.chunk)
		self.sampe_size = self.audio.get_sample_size(self.format)
		self.register_event_type('on_fps')
		self.register_event_type('on_start')
		self.register_event_type('on_end')
		self.fps_task = None

	def on_fps(self, d):
		print('on_fps fired')

	def on_start(self):
		print('on_start fired')

	def on_end(self):
		print('on_end fired')

	def audio_profile(self):	
		return {
			'channels':self.channels,
			'sample_size':self.sample_size,
			'sample_rate':self.samplerate
		}

	def get_frames(self, *args):
		d = self.get_fps_data()
		self.dispatch('on_fps', d)

	def get_fps_data(self, *args):
		self.lock.acquire()
		d = self.chunk_buffer[:]
		self.chunk_buffer = []
		self.lock.release()
		return d

	def start(self, *args):
		self.recording = True
		Background(self._record)
		self.dispatch('on_start')
		self.fps_task = Clock.schedule_interval(self.get_frames, self.fps)

	def _record(self):
		self.recording = True
		while self.recording:
			data = self._mic.read(self.chunk)
			self.lock.acquire()
			self.hunk_buffer.append(data)
			self.lock.release()

	def stop(self, *args):
		self.recording = False
		self.fps_task.cancel()
		self.dispatch('on_end')

	def close(self):
		self._mic.stop_stream()
		self._mic.close()
		self._audio.close()
