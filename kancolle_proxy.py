import asyncio
import threading
import requests
from mitmproxy import http
from mitmproxy.options import Options
from mitmproxy.tools.dump import DumpMaster
import sys

requests.packages.urllib3.disable_warnings()

class TouYouAddon:
    def force_send(self, url, headers, data):
        try:
            # 清理可能引起冲突的请求头
            safe_headers = dict(headers)
            if 'Host' in safe_headers:
                del safe_headers['Host']
            if 'Accept-Encoding' in safe_headers:
                del safe_headers['Accept-Encoding']
            
            # 因为你游戏是直连，这里直接发送，不加代理参数
            requests.post(url, headers=safe_headers, data=data, verify=False)
            print("[Success] 狸猫换太子完成！后台强制发送成功，油已入账！")
        except Exception as e:
            print(f"[Error] 后台发送失败: {e}")

    def request(self, flow: http.HTTPFlow):
        # 拦截进点请求
        if "api_req_map/next" in flow.request.path:
            print("[Alert] 拦截到进点请求！开始截杀原请求...")
            
            # 1. 提取所有需要的数据
            url = flow.request.pretty_url
            headers = dict(flow.request.headers)
            data = flow.request.content
            
            # 2. 【核心操作】：直接杀掉浏览器发来的原请求！(防止双重发包导致猫)
            flow.kill()
            
            # 3. 开启不受 F5 影响的独立线程，替你把包发完
            threading.Thread(target=self.force_send, args=(url, headers, data)).start()

async def main():
    opts = Options(listen_host='127.0.0.1', listen_port=8080)
    master = DumpMaster(opts, with_termlog=True, with_dumper=False)
    master.addons.add(TouYouAddon())
    
    print("========================================")
    print(" 舰娘防 F5 吞油代理已启动 (终极截杀代发版)")
    print(" 代理地址: 127.0.0.1:8080")
    print(" 请保持此窗口运行，按 Ctrl+C 关闭")
    print("========================================")
    
    try:
        await master.run()
    except KeyboardInterrupt:
        print("代理已关闭。")

if __name__ == '__main__':
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
