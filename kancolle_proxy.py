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
            requests.post(url, headers=headers, data=data, verify=False)
            print("[Success] 截获进点请求，后台强制发送成功！")
        except Exception as e:
            pass

    def request(self, flow: http.HTTPFlow):
        if "api_req_map/next" in flow.request.path:
            print("[Alert] 检测到进点请求，接管发送...")
            url = flow.request.pretty_url
            headers = dict(flow.request.headers)
            data = flow.request.content
            threading.Thread(target=self.force_send, args=(url, headers, data)).start()

async def main():
    opts = Options(listen_host='127.0.0.1', listen_port=8080)
    master = DumpMaster(opts, with_termlog=True, with_dumper=False)
    master.addons.add(TouYouAddon())
    
    print("========================================")
    print(" 舰娘防 F5 吞油代理已启动")
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
