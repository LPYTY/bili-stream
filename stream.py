import httpx
import time
import json
import argparse

# disable warnings
import urllib
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import blivedll

class BiliLive:
    def __init__(self):
        self.base_url = 'https://api.live.bilibili.com'
        self.start_live_url = self.base_url + "/room/v1/Room/startLive"
        self.end_live_url = self.base_url + "/room/v1/Room/stopLive"
        self.get_area_url = self.base_url + "/room/v1/Area/getList?show_pinyin=1"
        self.session = httpx.Client(http2=True, verify=False, headers=self.create_headers())
        self.is_living = False
        self.blive_path = None
        self.blive_version = None
        self.blive_build = None
        self.sign_fn = None
        self.room_id = None
        self.cookies = None
        self.area = None
        self.area_info = {}
        self.live_data = {}

    def create_headers(self):
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive'
        }
    
    def set_blive_path(self, blive_path):
        self.blive_path = blive_path
        dll_info = blivedll.get_dll_info(blive_path)
        self.blive_version = dll_info['version']
        self.blive_build = dll_info['build']
        self.sign_fn = dll_info['sign']
    
    def set_cookies(self, cookies):
        self.cookies = {}
        self.session.cookies.clear()
        for cookie in cookies.split('; '):
            key, value = cookie.split('=')
            self.cookies[key] = value
            self.session.cookies.set(key, value)

    def set_room_id(self, room_id):
        self.room_id = room_id

    def set_area(self, area):
        self.area = area

    def start_live(self):
        if self.is_living:
            print("已有正在进行中的直播")
            #return
        if not self.room_id or not self.area:
            print("请设置直播间号和分区")
            return
        try:
            payload = {
                "access_key": "",
                "appkey": "aae92bc66f3edfab",
                "area_v2": self.area,
                "build": self.blive_build,
                'room_id': self.room_id,
                'platform': 'pc_link',
                'ts': int(time.time()),
                'type': 1,
                'version': self.blive_version
            }
            signature = self.sign_fn(urllib.parse.urlencode(payload))
            payload['sign'] = signature
            payload['csrf_token'] = self.cookies.get('bili_jct', '')
            payload['csrf'] = self.cookies.get('bili_jct', '')
            response = self.session.post(self.start_live_url, data=payload)
            response_data = response.json()
            if response_data['code'] == 0:
                self.is_living = True
                self.live_data = response_data['data']
                print("直播开始，请复制服务器地址和推流码到OBS中以开始推流")
                print("服务器：")
                print(response_data['data']['rtmp']['addr'])
                print("推流码：")
                print(response_data['data']['rtmp']['code'])
            else:
                print(f"直播未能开始: {response_data['message']}")
        except Exception as e:
            print(f"出错了: {e}")
            print(response.headers)
            print(response.content)
            #raise e
            self.is_living = False

    def end_live(self):
        if not self.is_living:
            print("没有正在进行的直播")
            #return
        try:
            payload = {
                'access_key': '',
                'appkey': 'aae92bc66f3edfab',
                'build': self.blive_build,
                'platform': 'pc_link',
                'room_id': self.room_id,
                'ts': int(time.time()),
                'version': self.blive_version,
            }
            signature = self.sign_fn(urllib.parse.urlencode(payload))
            payload['sign'] = signature
            payload['csrf_token'] = self.cookies.get('bili_jct', '')
            payload['csrf'] = self.cookies.get('bili_jct', '')
            response = self.session.post(self.end_live_url, data=payload)
            response_data = response.json()
            if response_data['code'] == 0:
                self.is_living = False
                print("直播结束")
            else:
                print(f"停止直播失败: {response_data['message']}")
        except Exception as e:
            print(f"出错了: {e}")
            print(response.headers)
            print(response.content)
            #raise e

    def get_area_list(self):
        try:
            response = self.session.get(self.get_area_url)
            response_data = response.json()
            if response_data['code'] == 0:
                area_list = response_data['data']
                print("分区名称-分区ID")
                for area_lv1 in area_list:
                    print(area_lv1['name'])
                    list_lv2 = area_lv1['list']
                    for area_lv2 in list_lv2:
                        self.area_info[str(area_lv2['id'])] = f"{area_lv1['name']} - {area_lv2['name']}"
                        print(f"\t{area_lv2['name']}\t{area_lv2['id']}")
            else:
                print(f"获取分区列表失败: {response_data['message']}")
        except Exception as e:
            print(f"出错了: {e}")

    def get_area_name(self, area_id):
        area_id = str(area_id)
        if area_id in self.area_info:
            return self.area_info[area_id]
        else:
            return "未知分区"

def main():
    parser = argparse.ArgumentParser(description="B站直播助手")
    parser.add_argument('--config', type=str, default='config.json', help='配置文件路径，默认为config.json')
    args = parser.parse_args()

    print("欢迎使用B站直播助手")
    config = {}
    if args.config:
        print(f"加载配置文件: {args.config}")
        try:
            with open(args.config, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except FileNotFoundError:
            print(f"配置文件 {args.config} 不存在，改为REPL模式")
    bili_live = BiliLive()
    if "blive_path" in config:
        blive_path = config["blive_path"]
        print(f"使用配置文件中的B站直播姬路径: {blive_path}")
    else:
        blive_path = input("请输入B站直播姬的安装路径（例如：C:/Programs Files/livehime）：")
    bili_live.set_blive_path(blive_path)
    if "user_cookies" in config:
        user_cookies = config["user_cookies"]
        print(f"使用配置文件中的cookie: {user_cookies}")
    else:
        user_cookies = input("请输入你的cookie字符串\n如果不知道如何获取cookie，请按下述步骤操作：\n1. 打开B站，按F12打开开发者工具\n2. 切换到Network选项卡\n3. 刷新页面，找到\"Name\"为www.bilibili.com的请求\n4. 点击，复制请求头中的cookie字符串，粘贴到这里\n")
    bili_live.set_cookies(user_cookies)
    if "room_id" in config:
        room_id = config["room_id"]
        print(f"使用配置文件中的直播间号: {room_id}")
    else:
        room_id = input("请输入直播间号：")
    bili_live.set_room_id(room_id)
    bili_live.get_area_list()
    if "area" in config:
        area = config["area"]
        print(f"使用配置文件中的分区ID: {area}")
    else:
        area = input("请输入分区ID：")
    bili_live.set_area(area)
    print(f"当前分区: {bili_live.get_area_name(area)}")
    while True:
        action = input("\n请输入操作[1, 2, 3]：1. 开始直播 2. 结束直播 3. 退出\n>")
        if action == '1':
            bili_live.start_live()
        elif action == '2':
            bili_live.end_live()
        elif action == '3':
            break
        else:
            print("无效的操作，请重新输入")

if __name__ == "__main__":
    main()