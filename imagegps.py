# coding=utf-8

import os
import exifread
import optparse
import requests
import json
from bs4 import BeautifulSoup





# 处理GPS信息
def gps_format(info):
	# 经度
	# print info
	jingdu = info[0]
	jingdu = str(jingdu)
	jingdu = jingdu.split(',')
	# print len(jingdu)
	if jingdu[0] == "\xe6\xb2\xa1\xe6\x9c\x89\xe6\x89\xbe\xe5\x88\xb0\xe7\xbb\x8f\xe5\xba\xa6\xe4\xbf\xa1\xe6\x81\xaf":
		return -1
	jingdu0 = jingdu[0]
	jingdu1 = jingdu[1]
	jingdu2 = jingdu[2]
	jingdu2 = jingdu2.split('/')
	jingdu2 = float(jingdu2[0]) / float(jingdu2[1])
	# print jingdu2
	val = 60.000
	# print jingdu
	jingdu0 = float(jingdu0)
	jingdu1 = float(jingdu1)
	# 106 + (19 + (527/50)/60)/60
	new_jingdu = jingdu0 + (jingdu1 + jingdu2 / val)/val

	# 纬度
	weidu = info[1]
	weidu = str(weidu)
	weidu = weidu.split(',')
	if weidu[0] == "\xe6\xb2\xa1\xe6\x9c\x89\xe6\x89\xbe\xe5\x88\xb0\xe7\xba\xac\xe5\xba\xa6\xe4\xbf\xa1\xe6\x81\xaf":
		return -1
	weidu0 = weidu[0]
	weidu1 = weidu[1]
	weidu2 = weidu[2]
	weidu2 = weidu2.split('/')
	weidu2 = float(weidu2[0]) / float(weidu2[1])
	weidu0 = float(weidu0)
	weidu1 = float(weidu1)

	new_weidu = weidu0 + (weidu1 + weidu2 / val)/val

	# print "经度: " + str(new_jingdu) + " 纬度: " + str(new_weidu)

	new_info =[
		new_weidu,
		new_jingdu
	]
	return new_info


def image_info(path):

	try:
		# 经度
		gpsjingdu = path ['GPS GPSLongitude']
	except:
		gpsjingdu = '没有找到经度信息'
	try:
		# 纬度
		gpsweidu = path ['GPS GPSLatitude']
	except:
		gpsweidu = '没有找到纬度信息'
	try:
		# 标识 N=北 S=南 W=西 E=东、
		flag = path['GPS GPSLatitudeRef']
	except:
		flag = '没有找到标识'
	try:
		# 时间
		time = path['Image DateTime']
	except:
		time = '没有找到时间信息'
	time = str(time)
	flag = str(flag)
	gpsjingdu = remove_k(gpsjingdu)
	gpsweidu = remove_k(gpsweidu)
	if (time == '没有找到时间信息') and (flag == '没有找到标识') and (gpsweidu == '没有找到纬度信息') and (gpsjingdu == '没有找到经度信息'):
		print '[-] 没有找到信息'
	else:
		print '拍摄时间：' + time + ' 经度：' + gpsjingdu + ' 纬度：' + gpsweidu + ' 标识：' + flag
	info = [
			gpsjingdu,
			gpsweidu,
			flag,
			time
		]
	return info

# 去括号
def remove_k(strz):
	strz = str(strz)
	strz = strz.replace(']','')
	strz = strz.replace('[','')
	return strz


# 爬取网站图片
def requeimage(url):
	try:
		ulist = []
		r = requests.get(url,headers = {'user-agent': 'Mozilla/5.0'})
		status = r.status_code
		if status != 200:
			print "无法访问"
			exit(0)
		soup = BeautifulSoup(r.text, 'html.parser')
		alist = soup.find_all('img')
		# print alist
		for i in alist:
			ulist.append(i.attrs['src'])   # 索引src 添加到ulist列表
		dir = '/home/python/gpsimage/'
		if not os.path.exists(dir):     # 创建路径
			os.mkdir(dir)
		for image in ulist:             # 取图名
			image_name = dir + image.split(r'/')[-1]    # 解析图片名称
			# print image
			# 判断绝对路径相对路径
			urls = url
			if (urls[0] == image[0]) and (urls[1] == image[1]) and (urls[2] == image[2]) and (urls[3] == image[3]):
				print "正在下载：" + str(image)
			else:
				print "正在下载：" + str(url) + str(image)
			# 判断是否已经下载
			if not os.path.exists(image_name):
				img = requests.get(url + image)
				with open(image_name,'wb') as f:
					f.write(img.content)
			else:
				print "图片已存在"
		print "已下载完成，开始提取信息"

		return dir
	except:
		print '网络错误或无法打开'
		exit(0)


# 百度map api
def get_gps(new_info):
	# print new_info
	jindu = new_info[1]
	weidu = new_info[0]

	key = 'MAsVGINLNyTGiM4UulcaeluCekGnAFxj'
	url = 'http://api.map.baidu.com/reverse_geocoding/v3/?ak=' + key + '&output=json&coordtype=wgs84ll&location={},{}'.format(weidu,jindu)
	r = requests.get(url)
	conn = r.content.decode('utf-8')
	status = r.status_code
	if status != 200:
		print 'key失效或网络不通'
		exit(0)
	else:
		info = conn.encode('unicode-escape').decode('string_escape')
		info = json.loads(info)
		# print info
		country = info['result']['addressComponent']['country'].decode("gb2312").encode("utf-8")
		# print country
		formatted_address = info['result']['formatted_address'].decode("gb2312").encode("utf-8")
		# print type(formatted_address)
		# print formatted_address
		gps_info = [
			country,
			formatted_address
		]
		return gps_info

def main():
	parser = optparse.OptionParser()
	parser.add_option('-p','--path',dest = 'path',help = '图片')
	parser.add_option('-u','--url',dest = 'url',help = 'url')
	parser.add_option('-d','--dir',dest = 'dir',help = '目录')
	(options,args) = parser.parse_args()
	if (options.path == None) and (options.url == None) and (options.dir == None):
		print '参数错误'
		exit(0)
	else:
		if (options.path != None):
			image = str(options.path)
			try:
				fp = open(image, 'rb')
				path = exifread.process_file(fp)
				print image
				info = image_info(path)
				new_info = gps_format(info)
				gps = get_gps(new_info)
				print '\033[0;31;40m [+] \033[0m' + '国家：' + gps[0] + ' 地区：' + gps[1]
			except:
				print "无法获取信息或者无法打开此文件"
		elif(options.url != None):
			urls = str(options.url)
			dir = requeimage(urls)
			list = os.listdir(dir)
			# print list
			for img in list:
				listdir = dir + img
				print img
				# print listdir
				try:
					fp = open(listdir,'rb')
					path = exifread.process_file(fp)
					if path != None:
						info = image_info(path)
						new_info = gps_format(info)
						# print new_info
						if new_info == -1:
							continue
						gps = get_gps(new_info)
						print '\033[0;31;40m [+] \033[0m' + '国家：' + gps[0] + ' 地区：' + gps[1]
					else:
						continue
				except:
					print "未知错误"
		elif(options.dir != None):
			dir = str(options.dir)
			list = os.listdir(dir)
			for img in list:
				listdir = dir + '/' + img
				print img
				fp = open(listdir,'rb')
				path = exifread.process_file(fp)
				if path != None:
					info = image_info(path)
					new_info = gps_format(info)
					# print new_info
					if new_info == -1:
						continue
					gps = get_gps(new_info)
					print '\033[0;31;40m [+] \033[0m' + '国家：' + gps[0] + ' 地区：' + gps[1]
				else:
					continue

if __name__ == '__main__':
	main()
