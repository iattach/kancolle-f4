import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading
import asyncio
import requests
from mitmproxy import http
from mitmproxy.options import Options
from mitmproxy.tools.dump import DumpMaster
import sys
import os

# 禁用 requests 的安全警告
requests.packages.urllib3.disable_warnings()

# ================= 代理核心逻辑 =================
class TouYouAddon:
    def __init__(self, target_node):
        self.node_count = 0
        self.target_node = target_node

    def request(self, flow: http.HTTPFlow):
        if "api_req_map/start" in flow.request.path:
            self.node_count = 0
            print("\n[Info] =================================")
            print("[Info] 舰队出击！节点计数器已重置为 0")
            print("[Info] =================================")
            return

        if "api_req_map/next" in flow.request.path:
            self.node_count += 1
            print(f"[Info] 舰队前进：到达第 {self.node_count} 个 next 节点")
            
            if self.node_count == self.target_node:
                print(f"[Alert] 锁定油点！启动 Python 强制接管...")
                
                url = flow.request.pretty_url
                headers = dict(flow.request.headers)
                data = flow.request.content
                
                safe_headers = dict(headers)
                safe_headers.pop('Host', None)
                safe_headers.pop('Accept-Encoding', None)
                
                try:
                    # 同步发送
                    resp = requests.post(url, headers=safe_headers, data=data, verify=False)
                    
                    resp_headers = dict(resp.headers)
                    resp_headers.pop('Content-Encoding', None)
                    resp_headers.pop('Content-Length', None)
                    
                    flow.response = http.Response.make(
                        resp.status_code,
                        resp.content,
                        resp_headers
                    )
                    print("[Success] 数据已强制写入！安全偷油完成！")
                except Exception as e:
                    print(f"[Error] 后台接管失败: {e}")
            else:
                print("[Info] 非目标节点，已安全放行。")

# ================= 代理线程启动器 =================
def run_proxy(target_node):
    async def main():
        opts = Options(listen_host='127.0.0.1', listen_port=8080)
        # 必须禁用 mitmproxy 自带的终端日志，否则在没黑框的 GUI 模式下会崩溃
        master = DumpMaster(opts, with_termlog=False, with_dumper=False)
        master.addons.add(TouYouAddon(target_node))
        
        print("========================================")
        print(" 舰娘防吞油代理 (面板完全体) 已启动")
        print(f" 监听地址: 127.0.0.1:8080")
        print(f" 当前设定: 在第 {target_node} 次 next 截杀")
        print("========================================")
        
        try:
            await master.run()
        except Exception as e:
            print(f"代理异常停止: {e}")

    # 为新线程创建独立的 asyncio 事件循环
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    loop.run_until_complete(main())

# ================= 软件 GUI 界面 =================
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("舰娘偷油安全代理")
        self.root.geometry("550x450")
        
        # 拦截右上角的“X”按钮，改为最小化
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # 界面布局：顶部控制区
        frame = tk.Frame(root)
        frame.pack(pady=10)
        
        tk.Label(frame, text="目标油点 (第几次next):").grid(row=0, column=0, padx=5)
        self.entry_node = tk.Entry(frame, width=5)
        self.entry_node.insert(0, "2")  # 默认填 2
        self.entry_node.grid(row=0, column=1, padx=5)
        
        self.btn_start = tk.Button(frame, text="▶ 启动代理", command=self.start_proxy, bg="#4CAF50", fg="white", width=12)
        self.btn_start.grid(row=0, column=2, padx=10)
        
        self.btn_quit = tk.Button(frame, text="完全退出", command=self.quit_app, bg="#f44336", fg="white", width=10)
        self.btn_quit.grid(row=0, column=3, padx=10)
        
        # 界面布局：下方日志区 (模拟原先的黑框框)
        self.text_log = scrolledtext.ScrolledText(root, state='normal', bg='#1e1e1e', fg='#00FF00', font=("Consolas", 10))
        self.text_log.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 将所有的 print() 输出重定向到咱们的文本框里
        sys.stdout = self.TextRedirector(self.text_log)
        sys.stderr = self.TextRedirector(self.text_log)
        
        print("欢迎使用！请确认油点节点数后，点击启动。")
        print("提示：点击右上角 X 会最小化到任务栏，代理不会中断。")

    class TextRedirector:
        def __init__(self, widget):
            self.widget = widget
        def write(self, str_data):
            self.widget.insert(tk.END, str_data)
            self.widget.see(tk.END) # 自动滚动到最底
        def flush(self):
            pass

    def start_proxy(self):
        try:
            target = int(self.entry_node.get())
        except ValueError:
            print("[Error] 节点必须是整数！")
            return
        
        # 启动后禁用按钮和输入框
        self.btn_start.config(state=tk.DISABLED, text="运行中...")
        self.entry_node.config(state=tk.DISABLED)
        
        # 开启后台守护线程跑 mitmproxy
        threading.Thread(target=run_proxy, args=(target,), daemon=True).start()

    def on_closing(self):
        # 核心功能：点击 X 时，仅仅是将窗口最小化 (iconify)
        self.root.iconify()

    def quit_app(self):
        # 使用 os._exit 强行杀掉进程，因为 asyncio 在后台跑，普通 exit 可能退不干净
        print("正在退出...")
        os._exit(0)

if __name__ == '__main__':
    root = tk.Tk()
    app = App(root)
    root.mainloop()
