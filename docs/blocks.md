# Blocks
Blocks是kivyblocks的核心类，负责将字典类型的数据转化为GUI的Widget。
Blocks也注册到了kivy.factory.Factory中，可以使用
```
blocks = Factory.Blocks()
```
初始化实例

## 方法
### widgetBuild(desc)
#### 参数
* desc 	1) 字典类型， Widget描述的字典数据
		2) 字符串，可通过json导入的字符串

#### 返回值
成功返回创建的widget实例 
失败返回空

#### 事件
如果创建widget成功，触发”on_built"事件，
如果创建widget失败，将触发“on_failed”事件

事件处理函数的例子如下：
创建成功：
```
def on_built(o, w):
	pass
```
其中，o为Blocks实例， w为新建widget的实例
创建失败
```
def on_failed(o,e):
	pass
```
其中， o为Blocks实例， e为例外实例

#### 功能描述
此方法按照desc字典数据构建一个Widget，首先按照desc['options']中的参数初始化“widgettype”属性指定的类，并将“subwidgets”中的子Widget创建，并添加到Widget中，并且将非“options”，“subwidgets“和”binds“的其他属性也创建完成，并作为Widget的属性变量，最后创建”binds“中的事件处理。

widgetBuild按照执行结果的状态，会触发两个事件中的一个，如果创建成功，会触发"on_built"

### getWidgetById(id, from_widget=None)
查找指定id的widget，可以指定从整个widget树上的哪个节点开始查找。
#### 参数
id：字符串，其中‘.'用于分割，节点id，如果id中存在‘.'，那么
## 使用用例

