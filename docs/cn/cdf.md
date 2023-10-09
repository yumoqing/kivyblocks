# 构件数据格式说明
一个构件数据格式必须是一个符合python的字典数据类型，需要至少包含以下属性

## id
	定义一个构件的名称，含有此属性的构件为命名构件，命名构件可以通过Blocks.getWidgetById获得。
	名称规则：名称由字母数字构成，理论上可以包含汉字，绝对不能包含”."（英文句号）

## widgettype
	定义构件的名称，大部分常用的kivy的widget的类名都可以用，以及kivyblocks扩展的部件

## options
	类构建时的参数，字典数据类型

## subwidgets
	子构件数组，数组中的每个元素也必须是一个符合构件数据格式要求的数据字典，用于定义一个子构件。

## binds
	构件的事件绑定列表，每个构件（和其命名子构件）的任和事件都可以绑定一道多个处理,详细事件绑定请看[事件绑定](./binds.md)

## 其他属性
	非上述属性的其他的字典属性，blocks会试图用此属性值来创建构件，如果成功，则将此构件在当前构件中保存为此属性名称，并可用使用属性名称当变量来调用 Blocks.getWidgetById()函数来获取
	
## 例子

### HELLO
```
		{
			"widgettype":"VBox",
			"options":{},
			"subwidgets":[
				{
					"widgettype":"Title1",
					"options":{
						"text":"Say Hello",
						"i18n":True,
						"size_hint_y":None,
						"height":"py::CSize(2)"
					}
				},
				{
					"widgettype":"Text",
					"options":{
						"text":"Hello KivyBlocks"
					}
				}
			]
		}
```
##### 说明
创建一个VBox类型的构件，VBox创建一个子构件垂直排列的容器，子构件按照顺序从上而下排列，在这个例子中，本VBox容器中放了两个子构件，一个是“title1”的标题1构件，另一个是Text构件，VBox不带参数是表示占满父构件的全部空间。

##### 显示效果
[Hello](../imgs/hello_window.png)

### 服务器来的构件字典数据
```
		{
            "widgettype":"urlwidget",
            "options":{
				"params":{},
                "url":"{{entire_url('ctrl.ui')}}"
            }
		}
```
#### 说明
urlwidget的一个特殊的构件类型
