---
name: kivyblocks-repo
version: 1.0.0
description: KivyBlocks
trigger_conditions:
  - 需要理解、修改或排障 kivyblocks 的代码
  - 在 kivyblocks 里定位入口、数据表、对外契约或构建方式
---

# kivyblocks 仓库技能

> 由仓库实际内容生成的骨架（README/目录/模型定义/契约/构建脚本逐项取证）。新增判断与坑位请直接在下面对应小节补充。

## 定位

**KivyBlocks**

Can you ever image build a gui application like play Lego blocks? kivyblocks just try to provide programmer a tool to build a application like play lego blocks kivyblocks base on the python package 'kivy', which is a cross platform GUI package and can play on window, linux, mac OS x, android and iph

- 远端：`https://github.com/yumoqing/kivyblocks.git`
- 默认分支：`master`（共 573 个提交）
- 最近提交：2023-10-26 `9e2b5db` bugfix
- 规模：253 个文件；Python 127，JSON 3

## 目录结构

- `kivyblocks/` — Python 包源码（模块本体）（215 个文件）
- `test/` — 测试（25 个文件）
- `docs/` — 文档（8 个文件）
- `readme/` — 1 个文件
- 根文件：`README.md`、`github-speed-up.md`、`requirements.txt`、`setup.py`

## 构建与运行

- `setup.py`：`kivyblocks` v?，依赖 3 项
- `requirements.txt`：10 项（jinja2、kivy、ffpyplayer、qrcode、pillow、requests）
- Python 包 `kivyblocks/`：`__init__.py`、`android_rotation.py`、`aplayer.py`、`backendfunction.py`、`baseWidget.py`、`bgcolorbehavior.py`、`block_test.py`、`blocks.py`

## README 要点与注意（摘自 `README.md`）

- 章节：Requirement、Principle、installation、How to use、BlocksApp、Blocks、Registered class、Documents、references、Changelog

## 建议阅读顺序

1. `README.md`
2. `docs/`

