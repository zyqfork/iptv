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

output_file = os.path.join('out', output_file)

with open(output_file, 'w', encoding='utf-8') as file:
    file.writelines("#EXTM3U" + '\n')
    sorted_keys = sorted(results.keys(), key=alphanum_key)
    sort_nicely(sorted_keys)
    for key in sorted_keys:
        file.write(results[key] + '\n')

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
