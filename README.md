# 我去不早说

Claude Code 会话监控器，常驻 Windows 系统托盘，实时监控 `~/.claude/history.jsonl` 的变动。当有新交互时在屏幕右下角弹出通知，智能分类用户行为。

## 功能

- 实时监控 Claude Code 会话，新交互弹出桌面通知
- 智能识别 11 种交互类型（提问、请求、bug、规划等）
- 右下角系统托盘图标，不占任务栏
- 支持暂停/恢复监控
- 设置界面：自定义用户名、一键开关机启动

## 环境要求

- Windows 系统
- Python 3.10 及以上
- 安装 Python 时需勾选 **tcl/tk and IDLE**（tkinter 为标准库，但需手动勾选安装）

如果已安装 Python 但运行报错缺少 tkinter，重新运行 Python 安装器 → Modify → 勾选 `tcl/tk and IDLE`。

## 快速开始

```bash
git clone https://github.com/your-username/WhyNotEarlier.git
cd WhyNotEarlier
pip install -r requirements.txt
pythonw woqu.py
```

或者直接双击 `start.bat`。

## 使用

- 右下角系统托盘出现橙色 C 图标
- 右键图标可暂停/恢复监控、打开设置、退出
- Claude Code 有新交互时，屏幕右下角弹出通知卡片，自动分类显示

## 设置

右键托盘图标 → 设置：

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| 用户名称 | 通知中显示的名称 | Windows 用户名 |
| 开机启动 | 开机自动启动程序 | 关闭 |

设置保存在 `config.json`，首次启动自动生成。

## 交互分类

根据用户输入文本自动识别 11 种交互类型：

| 类型 | 示例触发词 |
|------|-----------|
| 询问了一个问题 | 怎么、为什么、how、why、? |
| 发了一个请求 | 帮我、请、create、fix |
| 发现了一个 bug | 报错、崩溃、exception、不行 |
| 彻底怒了 | 妈的、垃圾、fuck、shit |
| 想开一个新项目 | 新项目、init、scaffold |
| 想加一个新功能 | 新功能、feature、新增 |
| 进行了一次压缩 | 压缩、compact、总结 |
| 调用了一个插件 | 插件、plugin、mcp、skill |
| 想修改一个方案 | 修改方案、调整、change plan |
| 清除了一次会话 | 清除、reset、new session |
| 进行了一次规划 | 规划、方案、design、架构 |

信号太弱或长聊类输入会随机抽取娱乐消息。同时有 5% 概率全局随机娱乐。

## 目录结构

```
├── woqu.py          # 主程序
├── start.bat        # 一键启动脚本
├── requirements.txt # Python 依赖
├── config.example.json  # 配置模板
├── config.json      # 用户配置（不提交到 git）
├── icon.ico         # 托盘图标
└── LICENSE
```

## 许可

MIT
