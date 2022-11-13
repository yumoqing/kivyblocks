
from kivy.factory import Factory

_mix_ins = {}

def filter_mixin(kwargs):
	return {k:v for k, v in kwargs.items() if not k.endswith('behavior')}

def get_mixins(kwargs):
	return {k:v for k, v in kwargs.items() if k.endswith('behavior')}

def register_mixin(name, klass):
	_mix_ins[name] = klass

def mix_other(inst, other):
	for k,v in other.__dict__.items():
		setattr(inst, k, v)

def mixin_behaviors(inst, kwargs):
	behaviors_kw = get_mixins(kwargs)
	for name, dic in behaviors_kw.items():
		klass = _mix_ins.get(name)
		if klass:
			other = Factory.Blocks().widgetBuild(dic)
			if other:
				mix_other(inst, other)

