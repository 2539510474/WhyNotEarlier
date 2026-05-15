# 我去不早说

Claude Code 会话监控器，常驻系统托盘，监控 `~/.claude/history.jsonl` 的变动，
当有新交互时在屏幕右下角弹出通知，智能分类用户行为。

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

信号太弱或长聊类输入会随机抽取娱乐消息：`进行一个天的聊` / `抽claudeCode鞭子` / `叽里咕噜的说什么呢`

同时有 5% 概率全局随机娱乐。

## 依赖

```
pip install pystray Pillow
```

tkinter 需从 Windows 安装 Python 时勾选。如运行报错，重新运行 Python 安装器 → Modify → 勾选 `tcl/tk and IDLE`。

## 使用

双击 `start.bat`，或：

```
pythonw woqu.py
```

右下角系统托盘出现橙色 C 图标，右键可暂停/恢复/退出。

## 开机自启

```bat
add_startup.bat    # 添加
remove_startup.bat # 移除
```

## 配置

编辑 `woqu.py` 顶部常量：

| 常量 | 说明 | 默认值 |
|------|------|--------|
| `USER_NAME` | 通知显示的用户名 | 空=Windows 用户名 |
| `APP_NAME` | 托盘图标标题 | 我去不早说 |
