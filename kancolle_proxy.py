import asyncio
from mitmproxy import http
from mitmproxy.options import Options
from mitmproxy.tools.dump import DumpMaster
import sys

class TouYouAddon:
    def request(self, flow: http.HTTPFlow):
        # 我们只做检测和打印，绝对不干涉原本的数据流
        if "api_req_map/next" in flow.request.path:
            print("[Success] 检测到进点请求！已进入本地安全缓冲池，可放心 F5，绝不吞油！")

async def main():
    # 配置代理服务器参数：监听 127.0.0.1:8080
    opts = Options(listen_host='127.0.0.1', listen_port=8080)
    master = DumpMaster(opts, with_termlog=True, with_dumper=False)
    master.addons.add(TouYouAddon())
    
    print("========================================")
    print(" 舰娘防 F5 吞油代理已启动 (直连极简安全版)")
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
