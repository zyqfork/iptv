import json
import sys
import requests
from bs4 import BeautifulSoup
import re
from collections import OrderedDict

def tryint(s):
    try:
        return int(s)
    except ValueError:
        return s
    # 也可以使用
    # return int(s) if s.isdigit() else s

# 将字母和数字分开
def alphanum_key(s):
    """ Turn a string into a list of string and number chunks.
        "z23a" -> ["z", 23, "a"]
    """
    return [ tryint(c) for c in re.split('([0-9]+)', s) ]

def sort_nicely(l):
    """ Sort the given list in the way that humans expect.
    """
    # 使用alphanum_key作为key进行排序
    l.sort(key=alphanum_key)

hwurl = "hwurl"  # 定义hwurl变量
prefix = sys.argv[2] if len(sys.argv) > 2 else ""

# 打印prefix
print(f"prefix: {prefix}")

# 读取JSON文件
with open(sys.argv[1], 'r', encoding='utf-8') as file:
    json_data = file.read()

# 解析JSON数据
data = json.loads(json_data)

# 存储结果的有序字典
results = OrderedDict()

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

    # 添加结果到有序字典
    if hwurl_value:
        # 替换 "rtp:/" 为 "udp://"
        hwurl_value = hwurl_value.replace("rtp:/", "/udp")
        #result = f"{channel_title},{prefix}{hwurl_value}"
        result = f"#EXTINF:-1, IPTV-{channel_title}, group-title=\"IPTV\" \n{prefix}{hwurl_value}"
        results[channel_title] = result

# 将有序字典的值按照键排序并写入文件
with open("local.m3u", 'w', encoding='utf-8') as file:
    sorted_keys = sorted(results.keys(), key=alphanum_key)
    sort_nicely(sorted_keys)
    for key in sorted_keys:
        file.write(results[key] + '\n')



