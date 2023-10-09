# KivyBlocks
Can you ever image build a gui application like play Lego blocks? kivyblocks just try to provide programmer a tool to build a application like play lego blocks

kivyblocks base on the python package 'kivy', which is a cross platform GUI package and can play on window, linux, mac OS x, android and iphone

## Requirement

[appPublic](https://github.com/yumoqing/appPublic)
[kivycalendar](https://github.com/yumoqing/kivycalendar)
[kivy](https://github.com/kivy/kivy)
...
see the [requirements.txt](./requirements.txt)

## Principle

There is a BlocksApp(inherited from App) in kivyblocks contains a all widgets can be created by Blocks, and the Blocks creates widgets according a customized json data, the data can download from application server or local filesystem. 
The Customized json data has it own format to descript the UI and it's interaction. please see the "Customized json data" section for further information.

## installation
```
pip install git+https://github.com/yumoqing/kivyblocks
```
Use above command to install the newest version of kivyblocks
## How to use
see the simple example below:
```
import sys
import os
from appPublic.folderUtils import ProgramPath
from appPublic.jsonConfig import getConfig

from kivyblocks.blocksapp import BlocksApp
from kivyblocks.blocks import Blocks

class TestApp(BlocksApp):
	def build(self):
		b = super(TestApp, self).build()
		widget_desc = {
			"widgettype":"VBox",
			"options":{},
			"subwidgets":[
				{
					"widgettype":"Title1",
					"options":{
						"otext":"Say Hello",
						"i18n":True,
						"size_hint_y":None,
						"height":"py::CSize(2)"
					}
				},
				{
					"widgettype":"Text",
					"options":{
						"i18n":True,
						"otext":"Hello KivyBlocks"
					}
				}
			]
		}
		blocks = Blocks()
		x = blocks.widgetBuild(widget_desc)
		return x

if __name__ == '__main__':
	pp = ProgramPath()
	workdir = pp
	if len(sys.argv) > 1:
		workdir = sys.argv[1]
	print('ProgramPath=',pp,'workdir=',workdir)

	config = getConfig(workdir,NS={'workdir':workdir,'ProgramPath':pp})
	myapp = TestApp()
	myapp.run()
```
if you running it on window, it will show the following:
![hello](./docs/imgs/hello_window.png)

## BlocksApp
inherited from kivy.app.App, for kivyblocks, it get root widget description dictionary from kivyblocks app's json configuration file, and uses Blocks to build the app's root widget.

## Blocks
A class to constructs all the GUI Widgets in kivyblocks from a widget description dictionary, 
The Blocks class is register in kivy.factory.Factory, so you can get Blocks class use following script:
```
from kivy.factory import Factory

Blocks = Factory.Blocks
```
### getWidgetById get widget by id
#### Syntax
getWidgetById(id:str, from_widget:Widget) -> Widget
#### Description
getWidgetById find the widget identified by "id", the widgets can be found, cause it have a "id" attribute in the widget description dictionary.
#### Use Case
get app
```
app = Factory.Blocks.getWidgetById('app')
```

get root widget
```
root = Factory.blocks.getWidgetById('root')
```
get Window 
```
w = Factory.Blocks.getWidgetById('Window')
```
find app.root descendant widget with widget_id is 'myid' 
```
Factory.Blocks.getWidgetById('root.myid')
```
find specified widget's descendant widget
```
from_w = Factory.Blocks.getWidgetById('root.one_id')
w = Factory.Blocks.getWidgetById('mychild', from_widget=from_w)
```
find a widget, widget_id is 'descendant' which has a ancester widget_id is 'myancester' and it is from_widget widget's ancester. 
```
from_w = Factory.Blocks.getWidgetById('root.one_id')
w = Factory.Blocks.getWidgetById('-myancester.descendant', from_widget=from_w)
```

getWidgetById(id:str, from_widget:Widget) -> Widget
#### Arguments:
* id a '.' splited string, each part must be a widget_id in the widget tree 
if id part is start with a '-', it mean to find widget upward, else it find widget downward

* from_widget, default is None, it mean find widget from app.root

#### Return
if widget found, return the found widget, else return None

### widgetBuild()
#### Syntax
x = widgetBuild(desc)

#### Use Case

#### Arguments
* desc
widget description dictionary(wdd), it has the following attributes:
** widgettype
A string, the name of widget class registered by kivyblocks into kviy.factory.Factory
** options
A dictionary, it is the **kwargs argument of __init__() method of the class
** subwidgets:
a list, contains one or more wdd or id, when wdd mean widget description dictionary, and string mean the id can be find with Factory.Blocks.getWidgetById()
** binds
a list of dictionary, each items bind a event to a action or actions
for further information, please read use case of this function

** any other attributes will be handle like a wdd, use to build a widget and the attributes key will be the attribute name of the class instance.

#### Return
if success, return the widget, else return None
## Registered class
### Hierarchy
### Menu
### DataGrid
### Toolbar
### PagePanel
### ToolPage
### Form
### Charts
### Video
### FFVideo
### CircleProgress
### BlocksTest
### DefaultImage
### CommandBox
### Text
### TinyText
### PriceView
### SingleCheckBox
### ClickableBox
### ClickableText
### ClickableIconText
### ToggleText
### ToggleIconText
### ClickableImage
### ToggleImage
### CircleProgress
### PyInterpreter
### UploadFile
### FFVideo
### AnchorBox
### FloatBox
### RelativeBox
### GridBox
### PageBox
### ScatterBox
### StackBox
### DateInput
### HTTPSeriesData
### HTTPDataHandler
### PageLoader
### UdpWidget
### ScrollPanel
### TextInput
### CameraWithMic
### CustomCamera
### QrReader
### Markdown
### PagePanel
### Conform
### Popup
### MapView
### DataGrid
### FileLoaderBrowser
### KivyCamera
### QRCodeWidget
### TabsPanel
### TwoSides
### PageContainer
### BoxViewer
### Form
### StrSearchForm
### VPlayer
### DataGrid
### Toolbar
### ToolPage
### HTTPDataHandler
### Text
### ScrollWidget
### BinStateImage
### JsonCodeInput
### FloatInput
### IntegerInput
### StrInput
### SelectInput
### BoolInput
### Messager
### LoginForm
### PressableImage
### PressableLabel
### Tree
### TextTree
### MenuTree
### PopupMenu
### HostImage
### APlayer
### WrapText
### PressableBox
### Title1
### Title2
### Title3
### Title4
### Title5
### Title6
### Modal
### TimedModal
### HBox
### VBox
### SwipeBox
### ToggleItems
### ExAccordion
### Slider
### PhoneButton
### AWebView
## Documents
[中文文档](./docs/cn/index.md)
[English](./docs/en/index.md)

## references

Build app for android please see [Buildozer](https://github.com/kivy/buildozer)
kivy introduct and API please see [kivy](https://kivy.org)

## Changelog
[changelog](docs/changelog.md)
