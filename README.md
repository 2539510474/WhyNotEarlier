# 我去不早说！

**非常实用的Claude Code小助手**

## 功能

- 实时预测 Claude Code 会话，弹出桌面通知
- 智能预测交互类型
- 右下角系统托盘图标
- 支持暂停/恢复监控
- 设置界面：自定义用户名、一键开关机启动

![功能预览](screenShot.png)
## 环境要求

- Windows 系统
- Python 3.10 及以上

## 快速开始

### 1. 下载项目

**Git Clone**

```bash
git clone https://github.com/2539510474/WhyNotEarlier.git
cd WhyNotEarlier
```


### 2. 安装 Python 环境

如果还没装 Python，去 [python.org](https://www.python.org/downloads/) 下载 Python 3.10 及以上版本。

安装时勾选底部的 **Add Python to PATH**，其余选项保持默认

> 如果你手动取消了 `tcl/tk and IDLE` 导致缺少 tkinter，重新运行安装器 → Modify → 勾选该选项即可恢复。

### 3. 安装依赖

打开终端（PowerShell 或 CMD），进入项目目录：

```bash
pip install -r requirements.txt
```

国内用户如果下载慢，可以换清华源：

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 4. 启动

```bash
pythonw woqu.py
```

或者直接双击 `start.bat`。

启动后右下角系统托盘出现橙色 C 图标即表示运行中。右键图标可以暂停/恢复监控、打开设置。

### 5. 开机自启（可选）

右键托盘图标 → 设置 → 勾选"开机启动"→ 保存。程序会自动在 Windows 启动目录创建启动脚本，下次开机自动运行。

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

## 目录结构

```
├── woqu.py          # 主程序
├── start.bat        # 一键启动脚本
├── requirements.txt # Python 依赖
├── config.example.json  # 配置模板
├── icon.ico             # 托盘图标
└── LICENSE
```

## 许可

MIT

## 我去不早说！
## 我去不早说！
## 我去不早说！
## 我去不早说！
## 我去不早说！
## 我去不早说！
## 我去不早说！
## 我去不早说！
## 我去不早说！
## 我去不早说！
## 我去不早说！
## 我去不早说！
## 我去不早说！
## 我去不早说！
## 我去不早说！
## 我去不早说！
## 我去不早说！
## 我去不早说！
## 我去不早说！
## 我去不早说！
## 我去不早说！
## 我去不早说！
## 我去不早说！
## 我去不早说！
## 我去不早说！
## 我去不早说！
## 我去不早说！
## 我去不早说！
## 我去不早说！
## 我去不早说！
## 我去不早说！
## 我去不早说！
## 我去不早说！
## 我去不早说！
## 我去不早说！
## 我去不早说！
## 我去不早说！
## 我去不早说！