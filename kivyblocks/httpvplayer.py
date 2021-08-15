import requests

headers = {
   'User-Agent': "Mozilla/5.0 (Windows NT 6.1; Win64; x64) "
                 "AppleWebKit/537.36 (KHTML, like Gecko) "
                 "Chrome/72.0.3626.109 Safari/537.36",
}

def read_m3u8(m3u8Url):
	baseurl = '/'.join(m3u8Url.split('/')[:-1])
	m3u8_res = requests.get(m3u8Url,headers)
	if m3u8_res.status_code != 200:
		print('URL不能正常访问', m3u8_res.status_code)
	m3u8_content = m3u8_res.content.decode('utf8')
	print(m3u8_content)
	'''获取m3u8中的下载连接'''
	media_url_list = []
	lines_list = m3u8_content.strip().split('\r\n')
	if len(lines_list) < 3:
		lines_list = m3u8_content.strip().split('\n')
	if '#EXTM3U' not in m3u8_content:
		raise BaseException('非M3U8连接')
	for index,line in enumerate(lines_list):
		# print(index,line)
		if '#EXTINF' in line:
			media_url_list.append('%s/%s' %(baseurl,lines_list[index+1]))
	return media_url_list

if __name__ == '__main__':
	vfile = read_m3u8("http://pili-live-hdl.qhmywl.com/dsdtv/6d735caeaf70f8901aa00f86aefc4dde.m3u8")
	print(vfile)
