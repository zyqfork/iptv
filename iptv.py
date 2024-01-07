import json
import sys
import requests
from bs4 import BeautifulSoup

# 定义变量hwurl和获取参数prefix、输出文件名
hwurl = "hwurl"  # 定义hwurl变量
prefix = sys.argv[2] if len(sys.argv) > 3 else ""

# 读取JSON文件
with open(sys.argv[1], 'r') as file:
    json_data = file.read()

# 解析JSON数据
data = json.loads(json_data)

# 存储结果的列表
results = []

# 遍历channels
for channel in data["channels"]:
    channel_title = channel["title"]
    hwurl_value = ""

    # 如果phychannels存在且不为空
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
        hwurl_value = hwurl_value.replace("rtp:/", "udp")
        #result = f"{channel_title},{prefix}{hwurl_value}"
        result = f"#EXTINF:-1 ,{channel_title}\n{prefix}{hwurl_value}"
        results.append(result)

with open("local.m3u", 'w') as file:
    for result in results:
        file.write(result + '\n')

# Making a POST request to upload the file
url = "http://epg.51zmt.top:8000/api/upload/"
#files = {'file': open('result.m3u', 'rb')}
#headers = {'Content-Type': 'multipart/form-data'}

files = {'myfile': ('local.m3u', open('local.m3u', 'rb'), 'audio/x-mpegurl')}

response = requests.post(url, files=files)


decoded_response = response.content.decode('utf-8')

# 解析响应内容
soup = BeautifulSoup(decoded_response, 'html.parser')
download_link = soup.find('a')['href']

# 下载文件
downloaded_file = requests.get(download_link)

with open('iptv.m3u', 'r') as file:
    iptv_content = file.read()

# 保存文件
with open('iptv-epg.m3u', 'wb') as file:
    file.write(downloaded_file.content)
    file.write('\n' + iptv_content)
