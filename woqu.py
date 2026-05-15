# -*- coding: utf-8 -*-
"""
我去不早说 - Claude Code 会话监控器
"""

import ctypes
import json
import os
import random
import time
import threading
import tkinter as tk

from pathlib import Path
import pystray
from PIL import Image

# 设置 DPI 感知，解决高 DPI 屏幕字体模糊问题
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)  # Per-Monitor DPI Aware
except:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except:
        pass

HISTORY_FILE = Path.home() / ".claude" / "history.jsonl"
ICON_FILE = Path(__file__).parent / "icon.ico"
CONFIG_FILE = Path(__file__).parent / "config.json"

DEFAULT_CONFIG = {
    "user_name": "",
    "app_name": "我去不早说",
    "fun_probability": 15,
}
config = dict(DEFAULT_CONFIG)

monitoring = True
paused = False
icon = None


def load_config():
    """从 config.json 加载配置，缺失则用默认值"""
    global config
    try:
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                saved = json.load(f)
            for key in DEFAULT_CONFIG:
                if key in saved:
                    config[key] = saved[key]
    except:
        pass


def save_config():
    """保存当前配置到 config.json"""
    global config
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    except:
        pass


def is_startup_enabled():
    startup_dir = Path(os.environ['APPDATA']) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
    return (startup_dir / "woqu.vbs").exists()


def toggle_startup(enable):
    startup_dir = Path(os.environ['APPDATA']) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
    vbs_path = startup_dir / "woqu.vbs"
    if enable:
        script_path = Path(__file__).resolve()
        startup_dir.mkdir(parents=True, exist_ok=True)
        with open(vbs_path, 'w', encoding='utf-8') as f:
            f.write(f'CreateObject("WScript.Shell").Run "pythonw ""{script_path}""", 0, False\n')
    else:
        if vbs_path.exists():
            vbs_path.unlink()


def get_line_count(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return sum(1 for _ in f)
    except:
        return 0


def read_lines(file_path, start):
    lines = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                if i >= start:
                    lines.append(line.strip())
    except:
        pass
    return lines


def parse_line(line):
    try:
        data = json.loads(line)
        return {
            'display': data.get('display', ''),
            'project': data.get('project', ''),
            'timestamp': data.get('timestamp', 0)
        }
    except:
        return None


# ---- 交互分类器 ----

def _pos_score(keywords, text, head, tail):
    """位置加权关键词匹配分：开头 2x，结尾 1.5x，中间 1x"""
    text_lower = text.lower()
    head_lower = head.lower()
    tail_lower = tail.lower()
    score = 0.0
    for kw in keywords:
        kw_l = kw.lower()
        count = text_lower.count(kw_l)
        if count == 0:
            continue
        score += count * 1.0
        if kw_l in head_lower:
            score += 1.0
        if kw_l in tail_lower:
            score += 0.5
    return score


def classify_interaction(display):
    """根据用户输入文本特征，归类为交互类型描述（中文）"""
    text = display.strip()
    if not text:
        return _random_fun()

    text_len = len(text)
    boundary = max(1, int(text_len * 0.2))
    head = text[:boundary]
    tail = text[-boundary:]
    text_lower = text.lower()
    head_lower = head.lower()
    tail_lower = tail.lower()

    scores = {}

    # 1. 询问了一个问题
    q_kw = ['怎么', '什么', '为什么', '如何', '哪', '是否', '能不能', '可以不可以',
            'how', 'what', 'why', 'which', 'where', 'when', 'who',
            '吗', '呢', '么', '能不能', '可不可以', '请问', '请教', '问一下', '问个']
    q_score = _pos_score(q_kw, text, head, tail)
    q_score += (text.count('?') + text.count('？')) * 5.0
    if tail.rstrip().endswith('?') or tail.rstrip().endswith('？'):
        q_score += 3.0
    q_starts = ['怎么', '什么', '为什么', '如何', '哪', '是否', '能不能',
                'how', 'what', 'why', 'which', 'where', 'when', 'who',
                'can', 'could', 'would', 'is', 'are', 'do', 'does', 'did']
    if any(head_lower.startswith(s) or text_lower.startswith(s) for s in q_starts):
        q_score += 3.0
    scores['asked_question'] = q_score

    # 2. 发了一个请求
    r_kw = ['帮', '请', '写', '改', '修', '加', '删', '创建', '生成', '实现',
            '优化', '重构', '翻译', '解释', '帮我', '给我', '来一个', '搞一个',
            'make', 'create', 'write', 'fix', 'add', 'remove', 'delete',
            'generate', 'implement', 'optimize', 'refactor', 'translate',
            'explain', 'help']
    r_score = _pos_score(r_kw, text, head, tail)
    r_starts = ['帮', '请', '写', '改', '修', '加', '删', '创建', '生成', '实现',
                '优化', '重构', '翻译', '解释', '帮我', '给我',
                'make', 'create', 'write', 'fix', 'add', 'remove', 'delete',
                'generate', 'implement', 'optimize', 'refactor', 'translate',
                'explain', 'please', 'help', 'can you', 'could you', 'would you']
    if any(head_lower.startswith(s) or text_lower.startswith(s) for s in r_starts):
        r_score += 3.0
    if tail.rstrip().endswith('吧') or tail.rstrip().endswith('呗'):
        r_score += 1.0
    scores['sent_request'] = r_score

    # 3. 发现了一个bug
    b_kw = ['bug', 'error', '报错', '错误', '异常', '不行', '有问题', '坏了',
            '崩溃', 'crash', 'fail', 'broken', '不工作', '不能用', 'issue',
            'problem', '出错', '故障', '没反应', '卡住', '闪退', '挂了',
            '报错了', '不好使', '不对', '不正常', 'exception', 'traceback']
    b_score = _pos_score(b_kw, text, head, tail)
    if (text.count('!') + text.count('！')) >= 2 and b_score > 0:
        b_score += 2.0
    scores['found_bug'] = b_score

    # 4. 想开一个新项目
    sp_kw = ['新项目', '新建项目', '创建项目', '开始项目', '初始化', 'init',
             'scaffold', 'new project', 'create project', 'start project',
             '从零', '从0', '从头开始', '搭一个', '新建一个', '开个项目', '开一个新项目']
    scores['start_project'] = _pos_score(sp_kw, text, head, tail)

    # 5. 想加一个新功能
    af_kw = ['新功能', '加功能', '添加功能', 'feature', 'new feature',
             'add feature', '增加一个', '加一个', '添加一个', '新增', '加个功能', '加个']
    scores['add_feature'] = _pos_score(af_kw, text, head, tail)

    # 6. 进行了一次压缩
    dc_kw = ['压缩', 'compact', '总结', 'summarize', '摘要', '概括', '精简',
             '缩短', '太长', '上下文太多', '整理一下', 'compress']
    scores['did_compaction'] = _pos_score(dc_kw, text, head, tail)

    # 7. 调用了一个插件
    cp_kw = ['插件', 'plugin', 'mcp', 'skill', 'skills', '工具调用', 'tool call',
             '用插件', '调插件', '装插件']
    scores['called_plugin'] = _pos_score(cp_kw, text, head, tail)

    # 8. 想修改一个方案
    mp_kw = ['修改方案', '改方案', '调整', '变更', 'modify plan', 'change plan',
             'adjust', 'revise', '重新规划', '重新设计', '改一下', '换一个',
             '换个方案', '改主意', '换方案']
    scores['modify_plan'] = _pos_score(mp_kw, text, head, tail)

    # 9. 清除了一次会话
    cs_kw = ['清除', '清空', '重置', '重新开始', 'clear', 'reset', 'clean',
             '新会话', 'new session', 'fresh start', '从头', '忘掉', '忘记之前',
             '刷新', '重来', '翻篇']
    scores['cleared_session'] = _pos_score(cs_kw, text, head, tail)

    # 10. 进行了一次规划
    dp_kw = ['规划', '计划', '方案', '设计', 'plan', 'design', 'architecture',
             '架构', '步骤', '流程', '方案设计', '怎么实现', '实现方案',
             '技术方案', '系统设计']
    dp_score = _pos_score(dp_kw, text, head, tail)
    if text_len > 200:
        dp_score *= 1.5
    scores['did_planning'] = dp_score

    # 11. 彻底怒了
    f_kw = ['妈的', '操', '垃圾', '傻逼', '废物', '气死', '烦死了', '滚',
            'fuck', 'shit', 'damn', 'stupid', 'useless', '什么鬼', '有毒',
            '恶心', '辣鸡', '垃圾东西', '废物东西', '蠢', '坑爹', '真是服了',
            '受不了', '忍不了', '无语', '简直了']
    f_score = _pos_score(f_kw, text, head, tail)
    alpha_chars = [c for c in text if c.isalpha()]
    if alpha_chars:
        caps_ratio = sum(1 for c in alpha_chars if c.isupper()) / len(alpha_chars)
        if caps_ratio > 0.5 and len(text) > 10:
            f_score += 2.0
    excl = text.count('!') + text.count('！')
    if excl >= 3:
        f_score += excl * 0.5
    scores['furious'] = f_score

    # 12. 粘贴了一段文本
    paste_score = 0.0
    if '\n' in text:
        paste_score += 3.0
        if '\n    ' in text or '\n\t' in text:
            paste_score += 2.0
    if text_len > 200:
        paste_score += 1.0
    if text_len > 500:
        paste_score += 2.0
    if text_len > 1000:
        paste_score += 3.0
    if text_len > 2000:
        paste_score += 4.0
    code_indicators = ['def ', 'function ', 'class ', 'import ', 'from ', 'const ', 'let ', 'var ',
                       '```', 'public ', 'private ', 'static ', 'void ', 'return ',
                       'print(', 'console.log', 'System.out', '#include', 'package ',
                       '{', '};', '=>', 'async ', 'await ', 'export ', '<html', '<div',
                       'SELECT ', 'INSERT ', 'UPDATE ', 'DELETE ', 'CREATE TABLE']
    code_count = sum(text_lower.count(c) for c in code_indicators)
    paste_score += code_count * 0.8
    scores['pasted_text'] = paste_score

    # 13. 找不到问题在哪
    nf_kw = ['找不到', '不知道哪里', '不知道问题', '没找到', "can't find", 'dont know',
             '不知道怎么回事', '莫名其妙', '哪里有问题', '问题在哪', '不知道在哪',
             '不知道什么原因', '找不到原因', '不知哪里', '看不出', '看不到问题',
             '没发现问题', '不知道哪里错', '找不到错误', '不知问题', '不晓得哪里',
             '不知道是哪', '找不着', '查不到', '定位不到']
    scores['cant_find_issue'] = _pos_score(nf_kw, text, head, tail)

    # 14. 想提交一个版本
    cm_kw = ['commit', '提交', '保存版本', 'push', '上传', '推送',
             'git add', '打个版本', '发布版本', '提交代码', '上传代码',
             '提交一下', 'commit一下', '打个commit', 'stage', 'git stage',
             'pr', 'pull request', 'merge', '合并', '打个包', '发版', 'release']
    scores['want_commit'] = _pos_score(cm_kw, text, head, tail)

    # 15. 想回退版本
    rb_kw = ['回退', '回滚', 'revert', 'rollback', 'reset', '撤销', '退回',
             '回到之前', '恢复版本', '退回去', 'checkout', 'undo', '撤销修改',
             '回到上一个', '退回到', '还原', '恢复回去', '倒退', '恢复到',
             '撤回去', '取消修改', '丢弃修改', '放弃修改', 'stash']
    scores['want_rollback'] = _pos_score(rb_kw, text, head, tail)

    # 16. 配置环境ing
    env_kw = ['安装', 'install', 'pip install', 'npm install', '配置环境', '环境配置',
              'setup', '部署', 'deploy', 'environment', '搭建环境', '装环境',
              'requirements', 'poetry', 'conda', '虚拟环境', 'venv', '环境变量',
              'path', '依赖', 'dependency', 'package', '下载', 'download',
              'brew install', 'apt install', 'apt-get', 'choco install',
              'yarn add', 'pnpm add', 'gem install', 'cargo install', 'go get',
              '装一下', '配一下', '搭环境', '编译环境', '开发环境']
    scores['configuring_env'] = _pos_score(env_kw, text, head, tail)

    # 17. 做作业ing
    hw_kw = ['作业', 'homework', '考试', '习题', '练习', '上课', '学习', '课程',
             'assignment', 'exercise', '刷题', 'leetcode', '算法题', '编程题',
             '题目', '做题', 'oj', 'acm', '竞赛', '比赛', '试题', '试卷',
             '期末', '考试题', '课后', '编程作业', '大作业', '课设', '课程设计',
             '数据结构', '算法导论', 'lab', '实验报告', '毕设', '毕业论文']
    scores['doing_homework'] = _pos_score(hw_kw, text, head, tail)

    # 18. 娱乐池（长聊/扯淡类）
    lc_kw = ['聊天', 'chat', '讨论', 'discuss', '聊聊', 'talk', '说说', '讲讲',
             '讲一下', '解释一下', '说明一下', '介绍一下', '科普', '讲讲看',
             '聊', '扯', '侃']
    lc_score = _pos_score(lc_kw, text, head, tail)
    if text_len > 500:
        lc_score += 2.0
    if text_len > 1000:
        lc_score += 3.0
    if text_len > 2000:
        lc_score += 5.0
    scores['had_long_chat'] = lc_score

    # 全局随机娱乐消息概率（从配置读取）
    if random.random() < config.get('fun_probability', 15) / 100.0:
        return _random_fun()

    best = max(scores, key=scores.get)
    best_score = scores[best]

    # 信号太弱 → 娱乐池兜底
    if best_score < 1.0:
        return _random_fun()

    CATEGORY_MAP = {
        'asked_question': '询问了一个问题',
        'sent_request': '发了一个请求',
        'found_bug': '发现了一个bug',
        'start_project': '想开一个新项目',
        'add_feature': '想加一个新功能',
        'did_compaction': '进行了一次压缩',
        'called_plugin': '调用了一个插件',
        'modify_plan': '想修改一个方案',
        'cleared_session': '清除了一次会话',
        'did_planning': '进行了一次规划',
        'furious': '彻底怒了',
        'pasted_text': '粘贴了一段文本',
        'cant_find_issue': '找不到问题在哪',
        'want_commit': '想提交一个版本',
        'want_rollback': '想回退版本',
        'configuring_env': '配置环境ing',
        'doing_homework': '做作业ing',
    }

    if best == 'had_long_chat':
        return _random_fun()

    return CATEGORY_MAP.get(best, _random_fun())


def _random_fun():
    """从娱乐消息池中随机选一条"""
    return random.choice([
        '进行一个天的聊',
        '抽claudeCode鞭子',
        '叽里咕噜的说什么呢',
        '打怪兽ing',
        '迈出了成为大佬的一步',
    ])


def _draw_rounded_rect(canvas, x1, y1, x2, y2, r, **kwargs):
    """在 canvas 上绘制圆角矩形"""
    # 主体（上下两个矩形拼成十字，覆盖四个角弧之外的区域）
    canvas.create_rectangle(x1 + r, y1, x2 - r, y2, **kwargs)
    canvas.create_rectangle(x1, y1 + r, x2, y2 - r, **kwargs)
    # 四个圆角
    canvas.create_arc(x1, y1, x1 + 2 * r, y1 + 2 * r,
                      start=90, extent=90, style=tk.PIESLICE, **kwargs)
    canvas.create_arc(x2 - 2 * r, y1, x2, y1 + 2 * r,
                      start=0, extent=90, style=tk.PIESLICE, **kwargs)
    canvas.create_arc(x2 - 2 * r, y2 - 2 * r, x2, y2,
                      start=270, extent=90, style=tk.PIESLICE, **kwargs)
    canvas.create_arc(x1, y2 - 2 * r, x1 + 2 * r, y2,
                      start=180, extent=90, style=tk.PIESLICE, **kwargs)


def show_notification(user, project, action):
    def _run():
        root = tk.Tk()
        root.withdraw()
        root.overrideredirect(True)
        root.attributes('-topmost', True)
        root.attributes('-alpha', 0.0)

        TRANSPARENT = '#010101'
        BG = '#ffffff'
        CORNER_R = 14
        TEXT_WIDTH = 340
        PAD_X = 28
        PAD_Y = 26
        MAX_ALPHA = 0.88

        root.configure(bg=TRANSPARENT)
        root.attributes('-transparentcolor', TRANSPARENT)

        canvas = tk.Canvas(
            root,
            width=100,
            height=100,
            bg=TRANSPARENT,
            highlightthickness=0,
            bd=0,
        )
        canvas.pack()

        # 内容 frame
        frame = tk.Frame(canvas, bg=BG)

        # 第一行：水平排列 Label 实现混排
        row1 = tk.Frame(frame, bg=BG)
        tk.Label(row1, text='3秒前  ',
                 font=('Microsoft YaHei UI', 11), fg='#777777', bg=BG).pack(side='left')
        tk.Label(row1, text=user,
                 font=('Microsoft YaHei UI', 12, 'bold'), fg='#2c2c2c', bg=BG).pack(side='left')
        tk.Label(row1, text='  在  ',
                 font=('Microsoft YaHei UI', 11), fg='#777777', bg=BG).pack(side='left')
        tk.Label(row1, text=project,
                 font=('Microsoft YaHei UI', 12, 'bold'), fg='#2c2c2c', bg=BG).pack(side='left')
        row1.pack()

        # 间距
        tk.Frame(frame, height=3, bg=BG).pack()

        # 第二行：动作
        tk.Label(frame, text=action,
                 font=('Microsoft YaHei UI', 14, 'bold'), fg='#b8753e', bg=BG,
                 wraplength=TEXT_WIDTH, justify='center').pack()

        # 根据实际内容尺寸调整 canvas
        root.update_idletasks()
        frame_w = frame.winfo_reqwidth()
        frame_h = frame.winfo_reqheight()

        canvas_w = max(frame_w + 2 * PAD_X, 200)
        canvas_h = frame_h + 2 * PAD_Y
        canvas.configure(width=canvas_w, height=canvas_h)

        _draw_rounded_rect(canvas, 2, 2, canvas_w - 2, canvas_h - 2,
                           CORNER_R, fill=BG, outline='')
        canvas.create_window(canvas_w // 2, canvas_h // 2,
                             window=frame, anchor='center')

        root.update_idletasks()
        w = root.winfo_reqwidth()
        h = root.winfo_reqheight()
        sw = root.winfo_screenwidth()
        sh = root.winfo_screenheight()
        root.geometry(f'{w}x{h}+{sw - w - 30}+{sh - h - 60}')
        root.deiconify()

        def fade_in(alpha=0.0):
            alpha = min(alpha + 0.06, MAX_ALPHA)
            root.attributes('-alpha', alpha)
            if alpha < MAX_ALPHA:
                root.after(25, lambda: fade_in(alpha))

        def fade_out(alpha=MAX_ALPHA):
            alpha = max(alpha - 0.06, 0.0)
            root.attributes('-alpha', alpha)
            if alpha > 0:
                root.after(25, lambda: fade_out(alpha))
            else:
                root.destroy()

        fade_in()
        root.after(3500, fade_out)
        root.mainloop()

    threading.Thread(target=_run, daemon=True).start()


def show_settings():
    def _run():
        global config

        BG = '#ffffff'
        ACCENT = '#b8753e'
        TEXT = '#2c2c2c'
        META = '#777777'

        win = tk.Tk()
        win.title(f"设置 - {config['app_name']}")
        win.resizable(False, False)

        # 窗口居中
        win.update_idletasks()
        w = 380
        h = 310
        sw = win.winfo_screenwidth()
        sh = win.winfo_screenheight()
        win.geometry(f'{w}x{h}+{(sw - w) // 2}+{(sh - h) // 2}')

        win.configure(bg=BG)

        # 标题栏
        title_frame = tk.Frame(win, bg=BG)
        title_frame.pack(fill='x', padx=24, pady=(22, 10))
        tk.Label(title_frame, text=f"设置 - {config['app_name']}",
                 font=('Microsoft YaHei UI', 14, 'bold'), fg=TEXT, bg=BG).pack(anchor='w')

        # 分隔线
        tk.Frame(win, height=1, bg='#e8e8e8').pack(fill='x', padx=24)

        content = tk.Frame(win, bg=BG)
        content.pack(fill='x', padx=28, pady=(14, 0))

        # 用户名称行
        row1 = tk.Frame(content, bg=BG)
        tk.Label(row1, text='用户名称', font=('Microsoft YaHei UI', 12), fg=TEXT, bg=BG,
                 width=10, anchor='w').pack(side='left')
        name_var = tk.StringVar(value=config['user_name'])
        name_entry = tk.Entry(row1, textvariable=name_var,
                              font=('Microsoft YaHei UI', 12), fg=TEXT, bg='#f5f5f5',
                              relief='flat', width=22)
        name_entry.pack(side='left', ipady=4)
        row1.pack(fill='x')

        # 开机启动行
        row2 = tk.Frame(content, bg=BG)
        tk.Label(row2, text='开机启动', font=('Microsoft YaHei UI', 12), fg=TEXT, bg=BG,
                 width=10, anchor='w').pack(side='left')
        startup_var = tk.BooleanVar(value=is_startup_enabled())
        cb = tk.Checkbutton(row2, variable=startup_var, bg=BG,
                            activebackground=BG, selectcolor=BG,
                            fg=META)
        cb.pack(side='left')
        row2.pack(fill='x', pady=(14, 0))

        # 娱乐概率行
        row3 = tk.Frame(content, bg=BG)
        tk.Label(row3, text='娱乐概率', font=('Microsoft YaHei UI', 12), fg=TEXT, bg=BG,
                 width=10, anchor='w').pack(side='left')
        prob_var = tk.IntVar(value=config.get('fun_probability', 15))
        prob_label = tk.Label(row3, text=f'{prob_var.get()}%',
                              font=('Microsoft YaHei UI', 11), fg=META, bg=BG, width=4)
        def _on_prob_change(*args):
            prob_label.config(text=f'{prob_var.get()}%')
        prob_var.trace_add('write', _on_prob_change)
        prob_scale = tk.Scale(row3, from_=0, to=100, orient=tk.HORIZONTAL,
                              variable=prob_var, bg=BG, fg=TEXT,
                              highlightthickness=0, bd=0, length=160)
        prob_scale.pack(side='left', padx=(0, 8))
        prob_label.pack(side='left')
        row3.pack(fill='x', pady=(14, 0))

        # 底部按钮
        btn_frame = tk.Frame(win, bg=BG)
        btn_frame.pack(side='bottom', fill='x', padx=24, pady=(14, 22))

        def on_save():
            config['user_name'] = name_var.get().strip()
            config['fun_probability'] = prob_var.get()
            save_config()
            toggle_startup(startup_var.get())
            win.destroy()

        cancel_btn = tk.Button(btn_frame, text='取消',
                               font=('Microsoft YaHei UI', 11), fg=META, bg='#f0f0f0',
                               relief='flat', bd=0, padx=20, pady=6,
                               activebackground='#e0e0e0', activeforeground=META,
                               command=win.destroy)
        cancel_btn.pack(side='right', padx=(8, 0))

        save_btn = tk.Button(btn_frame, text='保存',
                             font=('Microsoft YaHei UI', 11, 'bold'), fg='white', bg=ACCENT,
                             relief='flat', bd=0, padx=24, pady=6,
                             activebackground='#a3642e', activeforeground='white',
                             command=on_save)
        save_btn.pack(side='right')

        win.mainloop()

    threading.Thread(target=_run, daemon=True).start()


def monitor_loop():
    global monitoring, paused

    if not HISTORY_FILE.exists():
        return

    last_count = get_line_count(HISTORY_FILE)

    while monitoring:
        if paused:
            time.sleep(1)
            continue

        time.sleep(1)
        current_count = get_line_count(HISTORY_FILE)

        if current_count > last_count:
            new_lines = read_lines(HISTORY_FILE, last_count)

            for line in new_lines:
                record = parse_line(line)
                if record and record['display'] and not record['display'].startswith('/'):
                    project = Path(record['project']).name if record['project'] else "Unknown"

                    time.sleep(3)

                    if not paused:
                        user = config.get('user_name') or os.environ.get("USERNAME", "用户")
                        action = classify_interaction(record['display'])
                        show_notification(user, project, action)

            last_count = current_count


def on_pause(icon, item):
    global paused
    paused = not paused
    update_icon()


def on_exit(icon, item):
    global monitoring
    monitoring = False
    icon.stop()


def update_icon():
    global icon
    if icon:
        icon.icon = load_icon()
        icon.title = f"{config['app_name']} - {'已暂停' if paused else '监控中'}"


def load_icon():
    if ICON_FILE.exists():
        return Image.open(ICON_FILE)
    img = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
    from PIL import ImageDraw
    draw = ImageDraw.Draw(img)
    draw.ellipse([4, 4, 60, 60], fill=(204, 119, 34))
    draw.text((18, 12), 'C', fill='white')
    return img


def setup_icon():
    global icon

    menu = pystray.Menu(
        pystray.MenuItem(
            lambda item: "已暂停" if paused else "监控中",
            None,
            enabled=False
        ),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("设置", lambda icon, item: show_settings()),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem(
            lambda item: "恢复" if paused else "暂停",
            on_pause
        ),
        pystray.MenuItem("退出", on_exit)
    )

    icon = pystray.Icon(
        config['app_name'],
        load_icon(),
        f"{config['app_name']} - 监控中",
        menu
    )

    return icon


def main():
    load_config()

    monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
    monitor_thread.start()

    icon = setup_icon()
    icon.run()


if __name__ == "__main__":
    main()
