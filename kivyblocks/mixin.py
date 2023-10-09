from kivy.factory import Factory
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.behaviors import CodeNavigationBehavior
from kivy.uix.behaviors import CompoundSelectionBehavior
from kivy.uix.behaviors import CoverBehavior
from kivy.uix.behaviors import DragBehavior
from kivy.uix.behaviors import EmacsBehavior
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.behaviors import ToggleButtonBehavior
from kivy.uix.behaviors import TouchRippleBehavior
from kivy.uix.behaviors import TouchRippleButtonBehavior

from kivy.factory import Factory

_mix_ins = {}

# def on_press(inst, *args):
# 	pass

# ButtonBehavior.on_press = on_press

def filter_mixin(kwargs):
	return {k:v for k, v in kwargs.items() if not k.endswith('Behavior')}

def get_mixins(kwargs):
	return {k:v for k, v in kwargs.items() if k.endswith('Behavior')}

def register_mixin(name, klass):
	_mix_ins[name] = klass
	Factory.register(name, klass)

def mix_other(inst, other):
	excluded = ['__class__', '__dict__', '__weakref__']
	keys = [ k for k in dir(other) if k not in excluded ]
	for k in keys:
		if not hasattr(inst, k):
			setattr(inst, k, getattr(other, k))

def mixin_behaviors(inst, kwargs):
	behaviors_kw = get_mixins(kwargs)
	for name, dic in behaviors_kw.items():
		klass = _mix_ins.get(name)
		if klass:
			mix_other(klass, inst.__class__)
			desc = {
				"widgettype":name,
				"options":dic
			}
			other = Factory.Blocks().widgetBuild(desc)
			if other:
				mix_other(inst, other)

register_mixin('ButtonBehavior', ButtonBehavior)
register_mixin('CodeNavigationBehavior', CodeNavigationBehavior)
register_mixin('CompoundSelectionBehavior', CompoundSelectionBehavior)
register_mixin('CoverBehavior', CoverBehavior)
register_mixin('DragBehavior', DragBehavior)
register_mixin('EmacsBehavior', EmacsBehavior)
register_mixin('FocusBehavior', FocusBehavior)
register_mixin('ToggleButtonBehavior', ToggleButtonBehavior)
register_mixin('TouchRippleBehavior', TouchRippleBehavior)
register_mixin('TouchRippleButtonBehavior', TouchRippleButtonBehavior)
