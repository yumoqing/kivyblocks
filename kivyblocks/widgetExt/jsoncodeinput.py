from pygments.lexers.data import JsonLexer
from kivy.uix.codeinput import CodeInput

class JsonCodeInput(CodeInput):
	def __init__(self,**kw):
		super(JsonCodeInput,self).__init__(lexer = JsonLexer())