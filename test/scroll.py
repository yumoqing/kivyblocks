from kivy.app import App
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

text="""
The Widget class is the base class required for creating Widgets. This widget class was designed with a couple of principles in mind:

    Event Driven

    Widget interaction is built on top of events that occur. If a property changes, the widget can respond to the change in the ‘on_<propname>’ callback. If nothing changes, nothing will be done. That’s the main goal of the Property class.

    Separation Of Concerns (the widget and its graphical representation)

    Widgets don’t have a draw() method. This is done on purpose: The idea is to allow you to create your own graphical representation outside the widget class. Obviously you can still use all the available properties to do that, so that your representation properly reflects the widget’s current state. Every widget has its own Canvas that you can use to draw. This separation allows Kivy to run your application in a very efficient manner.

    Bounding Box / Collision

    Often you want to know if a certain point is within the bounds of your widget. An example would be a button widget where you only want to trigger an action when the button itself is actually touched. For this, you can use the collide_point() method, which will return True if the point you pass to it is inside the axis-aligned bounding box defined by the widget’s position and size. If a simple AABB is not sufficient, you can override the method to perform the collision checks with more complex shapes, e.g. a polygon. You can also check if a widget collides with another widget with collide_widget().

We also have some default values and behaviors that you should be aware of:

    A Widget is not a Layout: it will not change the position or the size of its children. If you want control over positioning or sizing, use a Layout.
    The default size of a widget is (100, 100). This is only changed if the parent is a Layout. For example, if you add a Label inside a Button, the label will not inherit the button’s size or position because the button is not a Layout: it’s just another Widget.
    The default size_hint is (1, 1). If the parent is a Layout, then the widget size will be the parent layout’s size.
    on_touch_down(), on_touch_move(), on_touch_up() don’t do any sort of collisions. If you want to know if the touch is inside your widget, use collide_point().

"""
class MyApp(App):
	def build(self):
		x = ScrollView()
		b = BoxLayout(orientation="vertical",
			size_hint=(None,None)
		)
		b.bind(minimum_height=b.setter('height'))
		b.bind(minimum_width=b.setter('width'))
		self.textout(b)
		x.do_scroll_x = True
		x.do_scroll_y = True
		x.scroll_x = 1
		x.scroll_y = 1
		print(b.size,x.size)
		x.add_widget(b)
		return x

	def textout(self,b):
		txt = text * 50
		maxwidth = 0
		for l in txt.split('\n'):
			l = Label(text=l,text_size=(None,40),size_hint=(None,None),height=40)
			l.width = l.texture_size[0]
			l.valign = "middle"
			l.align = "left"
			print(l.width)
			if maxwidth < l.width:
				maxwidth = l.width
			b.add_widget(l)
		b.width = 4500
		 

MyApp().run()
