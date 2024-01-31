import json
import sys
import requests
from bs4 import BeautifulSoup
import re

hwurl = "hwurl"  # 定义hwurl变量
prefix = sys.argv[2] if len(sys.argv) > 2 else ""

# 打印prefix
print(f"prefix: {prefix}")

# 读取JSON文件
with open(sys.argv[1], 'r', encoding='utf-8') as file:
    json_data = file.read()

# 解析JSON数据
data = json.loads(json_data)

# 存储结果的列表
results = []

# 遍历channels
for channel in data["channels"]:
    channel_title = channel["title"]

    if re.match(r'^(?!.*高清).*cctv', channel_title, re.IGNORECASE):
        continue

    hwurl_value = ""

    if "phychannels" in channel and len(channel["phychannels"]) > 0:
        phychannel = channel["phychannels"][0]
        if "params" in phychannel and hwurl in phychannel["params"]:
            hwurl_value = phychannel["params"][hwurl]

    # 如果hwurl_value为空，则从params中获取
    if not hwurl_value:
        if hwurl in channel["params"]:
            hwurl_value = channel["params"][hwurl]

    # 添加结果到列表
    if hwurl_value:
        # 替换 "rtp:/" 为 "udp://"
        hwurl_value = hwurl_value.replace("rtp:/", "/udp")
        #result = f"{channel_title},{prefix}{hwurl_value}"
        result = f"#EXTINF:-1 ,{channel_title}\n{prefix}{hwurl_value}"
        results.append(result)

with open("local.m3u", 'w', encoding='utf-8') as file:
    for result in results:
        file.write(result + '\n')


