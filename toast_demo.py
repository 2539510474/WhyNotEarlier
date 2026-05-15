"""演示 HTML 弹窗 — 运行直接看效果"""
import subprocess
import os
import time

HTML = r"""<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8">
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  html, body {
    width: 100%; height: 100%;
    background: transparent;
    display: flex;
    justify-content: center;
    align-items: center;
    font-family: 'Microsoft YaHei UI', sans-serif;
    -webkit-font-smoothing: antialiased;
  }
  .toast {
    background: rgba(255, 255, 255, 0.72);
    backdrop-filter: blur(24px);
    -webkit-backdrop-filter: blur(24px);
    border-radius: 16px;
    padding: 20px 32px;
    max-width: 420px;
    box-shadow: 0 4px 24px rgba(0, 0, 0, 0.06), 0 1px 4px rgba(0, 0, 0, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.5);
    text-align: center;
    font-weight: 700;
    font-size: 13px;
    color: #1a1a1a;
    line-height: 1.9;
    letter-spacing: 0.3px;
    user-select: none;
  }
</style>
</head>
<body>
  <div class="toast">
    3秒前 [用户] 在 [项目] 问了 Claude Code 一个问题
  </div>
  <script>
    var w = 440, h = 140;
    window.resizeTo(w, h);
    window.moveTo((screen.availWidth - w) / 2, (screen.availHeight - h) / 2);
    setTimeout(() => { window.close(); }, 4000);
  </script>
</body>
</html>"""

# 写入临时文件
tmp_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_toast_demo.html")
with open(tmp_path, 'w', encoding='utf-8') as f:
    f.write(HTML)

# 找到 Edge
EDGE_PATHS = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
]
edge = None
for p in EDGE_PATHS:
    if os.path.exists(p):
        edge = p
        break

if not edge:
    print("未找到 Edge，改用默认浏览器打开（无 app 模式效果）")
    os.startfile(tmp_path)
else:
    url = "file:///" + tmp_path.replace("\\", "/")
    subprocess.Popen(
        [edge, "--app=" + url, "--window-size=440,140",
         "--no-first-run", "--no-default-browser-check"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    print("弹窗已弹出 → 看屏幕右下角")
    print("4 秒后自动消失")
