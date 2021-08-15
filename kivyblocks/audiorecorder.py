
import tempfile
import pyaudio
import wave
from kivy.event import EventDispatcher
from kivy.properties import NumericProperty
from kivyblocks.baseWidget import HBox
from kviyblocks.micphone import Micphone

class AudioRecorder(EventDispatcher):
	fs = NumericProperty(None)
	filename = StringProperty(None)
	voice_src = OjbectProperty(None)
	def __init__(self, **kw):
		super(AudioRecorder, self).__init__(**kw)
		self.saving = False
		if not self.filename:
			self.mk_temp_file()

	def mk_temp_file(self):
		self.filename = tempfile.mktemp(suffix='.wav')

	def on_filename(self, *args):
		self.wf = wave.open(self.filename, 'wb')

	def on_voice_src(self, *args):
		audio_profile = self.voice_src.audio_profile()
		self.wf.setnchannels(audio_profile['channels'])
		self.wf.setsamplewidth(audio_profile['sample_size'])
		self.wf.setframerate(audio_profiel['sample_rate'])
		self.voice_src.bind(on_fps=self.write)

	def write(self, o, d):	
		if self.saving:
			self.wf.write(''.join(d))

	def start(self):
		if not self.voice_src.recording:
			self.voice_src.start()
		self.saving = True

	def stop(self):
		self.saving = False
		wf.close()
