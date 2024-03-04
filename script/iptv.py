import json
import sys
import requests
from bs4 import BeautifulSoup
import re
import os
from collections import OrderedDict

def tryint(s):
    try:
        return int(s)
    except ValueError:
        return s

def alphanum_key(s):
    return [tryint(c) for c in re.split('([0-9]+)', s)]

def sort_nicely(l):
    l.sort(key=alphanum_key)

hwurl = "hwurl"
prefix = sys.argv[2] if len(sys.argv) > 2 else ""

output_file = sys.argv[3] if len(sys.argv) > 3 and sys.argv[3] else re.sub(r'http[s]?://([^:/]+).*', r'\1', sys.argv[2]).replace(".", "") + ".m3u"


print(f"output_file: {output_file}")

with open(sys.argv[1], 'r', encoding='utf-8') as file:
    json_data = file.read()

data = json.loads(json_data)
results = OrderedDict()

for channel in data["channels"]:
    channel_title = channel["title"]

    if re.match(r'^(?!.*高清).*cctv', channel_title, re.IGNORECASE):
        continue

    if channel_title.startswith(("咪咕", "精选频道", "精选4k频道", "百视通高清直播室", "移动")):
        continue

    if channel_title.startswith("CCTV") and channel_title[4].isdigit():
        channel_title = f"CCTV-{channel_title[4:]}"
        print(channel_title)

    hwurl_value = ""

    if "phychannels" in channel and len(channel["phychannels"]) > 0:
        phychannel = channel["phychannels"][0]
        if "params" in phychannel and hwurl in phychannel["params"]:
            hwurl_value = phychannel["params"][hwurl]

    if not hwurl_value:
        if hwurl in channel["params"]:
            hwurl_value = channel["params"][hwurl]

    if hwurl_value:
        hwurl_value = hwurl_value.replace("rtp:/", "/udp")
        result = f"#EXTINF:-1 group-title=\"IPTV\", {channel_title} \n{prefix}{hwurl_value}"
        results[channel_title] = result

keys_to_remove = set()

for key1 in results:
    if key1.endswith("高清"):
        new_key = key1.replace("高清", "超清")
        if new_key in results:
            keys_to_remove.add(key1)
    for key2 in results:
        if key1 != key2 and key1 in key2:
            keys_to_remove.add(key1)

#print(keys_to_remove)

for key in keys_to_remove:
    del results[key]

output_file = os.path.join('out', output_file)

with open(output_file, 'w', encoding='utf-8') as file:
    file.writelines("#EXTM3U" + '\n')
    sorted_keys = sorted(results.keys(), key=alphanum_key)
    sort_nicely(sorted_keys)
    for key in sorted_keys:
        modified_title = re.sub(r'(超清|高清)', '', results[key])
        file.write(modified_title + '\n')

with open("./IPTV.m3u", 'r', encoding='utf-8') as iptv_file:
    iptv_content = iptv_file.readlines()

iptv_content = iptv_content[1:]

with open(output_file, 'a', encoding='utf-8') as local_file:
    local_file.writelines(iptv_content)

with open("./Global.m3u", 'r', encoding='utf-8') as global_file:
    global_content = global_file.readlines()

global_content = global_content[1:]

with open(output_file, 'a', encoding='utf-8') as local_file:
    local_file.writelines(global_content)
