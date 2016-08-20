# -*- coding: utf-8 -*-
import hashlib
import web
import lxml
import time
import os
import sys
import urllib2
import json
import urllib
import re
import random
import hashlib
import cookielib
from urllib import urlencode
from lxml import etree
import pylibmc
from bs4 import BeautifulSoup
import requests
import random
import itertools

def get_html(url):
	send_headers = {
		'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36',
		'Accept':'*/*',
		'Connection':'keep-alive',
		'Host':'movie.douban.com'
	}

	req = urllib2.Request(url,headers = send_headers)
	response = urllib2.urlopen(req)
	html = response.read().decode('utf-8')

	return html
	
def analyse(html):
	soup = BeautifulSoup(html,'lxml')
	for i in soup.find_all('a'):
		try:
			content = i['href']
			if '/subject/' in content:
				#print (content)
				break
		except:
			pass
	return content

def tag(html):
	soup = BeautifulSoup(html,'lxml')
	tag = []
	for i in soup.find_all('a'):
		try:
			content = i['href']
			if '/tag/' in content:
				tag.append(i.string)
		except:
			pass
	return tag[1:6]

def tag_sort(tag,tag_all):
	for each in tag:
		if each not in tag_all.keys():
			tag_all[each] = 1
		else:
			tag_all[each]+=1
	return tag_all

def arrange(tag,url_pre):
	url_tag = "https://movie.douban.com/tag/"
	all = []

	for num in range(len(tag), 0, -1):
		s = (list(itertools.combinations(tag, num)))
		#print(s)
		for each in s:
			url = url_tag + urllib.quote(each)
			html = get_html(url)
			end = 0
			#print (url)
			for i in range(len(re.findall('a class="nbg" href="', html))):
					start = html.find('a class="nbg" href="', end) + len('a class="nbg" href="')
					end = html.find('"  title=', start)
					name_start = end + len('"  title="')
					name_end = html.find('">', name_start)

					if (html[start:end] not in url_pre) and not re.findall(html[start:end], ''.join(all)):
						all.append(html[name_start:name_end] + "\t" + html[start:end] + "\n")
						if len(all) == 10:
							return ''.join(all)
							
def robot(content):
    raw_TULINURL = "http://www.tuling123.com/openapi/api?key=672aa246ec6e6af6db7d32ce8ccd316d&info="
    if type(content).__name__ == "unicode":
        content = content.encode('UTF-8')
    queryStr = content
    TULINURL = "%s%s" % (raw_TULINURL,urllib2.quote(queryStr))
    req = urllib2.Request(url=TULINURL)
    result = urllib2.urlopen(req).read()
    hjson=json.loads(result)
    length=len(hjson.keys())
    content=hjson['text']
    if length==3:
        contents = content + hjson['url']
    elif length==2:
        contents = content
    return contents



class WeixinInterface:

    def __init__(self):
        self.app_root = os.path.dirname(__file__)
        self.templates_root = os.path.join(self.app_root, 'templates')
        self.render = web.template.render(self.templates_root)

    def GET(self):
        #获取输入参数
        data = web.input()
        signature=data.signature
        timestamp=data.timestamp
        nonce=data.nonce
        echostr=data.echostr
        #自己的token
        token="Belief0599" #这里改写你在微信公众平台里输入的token
        #字典序排序
        list=[token,timestamp,nonce]
        list.sort()
        sha1=hashlib.sha1()
        map(sha1.update,list)
        hashcode=sha1.hexdigest()
        #sha1加密算法        

        #如果是来自微信的请求，则回复echostr
        if hashcode == signature:
            return echostr
        
    def POST(self):        
            str_xml = web.data() #获得post来的数据
            xml = etree.fromstring(str_xml)#进行XML解析
            #content=xml.find("Content").text#获得用户所输入的内容
            mstype=xml.find("MsgType").text
            fromUser=xml.find("FromUserName").text
            toUser=xml.find("ToUserName").text
            userid = fromUser[0:15]
            mc = pylibmc.Client()

            if mstype == "event":
    			mscontent = xml.find("Event").text
    			if mscontent == "subscribe":
        			replayText = u'你好！这里是黄芋头小店^_^\n或许会有不定期推送，也许会分享一些种玉米心得，更有敏哥心情感悟，也会分享一些技术咨询。\n努力建成多功能工具型公众号：）有意见的赶快给我留言噢，都满足你！（输入“h”查看使用帮助）'
        			return self.render.reply_text(fromUser,toUser,int(time.time()),replayText)
    			if mscontent == "unsubscribe":
        			replayText = u'我现在功能还很简单，知道满足不了您的需求，但是我会慢慢改进，欢迎您以后再来'
        			return self.render.reply_text(fromUser,toUser,int(time.time()),replayText)
            if mstype == "image":
                try:
                    picurl = xml.find('PicUrl').text
                    s = requests.session()
                    url = 'http://how-old.net/Home/Analyze?isTest=False&source=&version=001'
                    header = {
                    'Accept-Encoding':'gzip, deflate',
                    'User-Agent': "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0",
                    'Host': "how-old.net",
                    'Referer': "http://how-old.net/",
                    'X-Requested-With': "XMLHttpRequest"
                        }
                
                
                    data = {'file':s.get(picurl).content}
                
                    r = s.post(url, files=data, headers=header)
                    h = r.content
                    i = h.replace('\\','')
                    gender = re.search(r'"gender": "(.*?)"rn', i)
                    age = re.search(r'"age": (.*?),rn', i)
                    if gender.group(1) == 'Male':
                        gender1 = '男'
                    else:
                        gender1 = '女'
                    datas = [gender1, age.group(1)]
                    return self.render.reply_text(fromUser, toUser, int(time.time()), '图中人物性别为'+datas[0]+'，'+'年龄为'+datas[1]+"。")
                except Exception , e:
                	return self.render.reply_text(fromUser, toUser, int(time.time()),  '对不起，图片无法识别。')
            if mstype == "voice":
                content = xml.find('Recognition').text
                contents = robot(content)
                return self.render.reply_text(fromUser,toUser,int(time.time()),contents)
            if mstype == "text":
                content=xml.find("Content").text
                '''
                if content.lower() == 'bye':
                	mc.delete(fromUser+'_xhj')
                	return self.render.reply_text(fromUser,toUser,int(time.time()),u'您已经跳出了和小黄鸡的交谈中，输入help来显示操作指令')
            	if content.lower() == 'xhj':
                	mc.set(fromUser+'_xhj','xhj')
                	return self.render.reply_text(fromUser,toUser,int(time.time()),u'您已经进入与小黄鸡的交谈中，请尽情的蹂躏它吧！输入bye跳出与小黄鸡的交谈')
                mcxhj = mc.get(fromUser+'_xhj')
                
                if (mcxhj =='xhj'):
                    
                    return self.render.reply_text(fromUser,toUser,int(time.time()),u"小黄鸡功能正在开发中...")
            	'''
            	
                '''
                if(content[0:2] == u"电影"):
                    if(u"+" in content):
                    	content = content.replace("+","")
                    if (u"\uff1a" in content):
                        content = content.replace(u"\uff1a","")
                    if(u":" in content):
                    	content = content.replace(":","")
                    name = content[2:]
                    name_list = name.split(',')
                    tag_all = {}
                    movie_url_all = ""
                    for name in name_list:
                        if type(name).__name__ == "unicode":
                    		name = name.encode('UTF-8')
                        url_pre = "https://movie.douban.com/subject_search?search_text=" + urllib.quote(name)
                    	html = get_html(url_pre)
                        movie_url = analyse(html)
                        html_movie = get_html(movie_url)
                        movie_tag = tag(html_movie)
                        tag_all = tag_sort(movie_tag,tag_all)
                        movie_url_all = movie_url_all + movie_url
                    tag_dict = sorted(tag_all.items(), key=lambda x:x[1], reverse=True)
                    movie_tag = []
                    for ta in tag_dict[:5]:
                        movie_tag.append(ta[0])
                    url_tag = "https://movie.douban.com/tag/"
                    all = []
                    return self.render.reply_text(fromUser,toUser,int(time.time()),url)
                  '''
                  
                elif(content[0:2] == u"维基"):
                    if(u"+" in content):
                    	content = content.replace("+","")
                    if (u"\uff1a" in content):
                        content = content.replace(u"\uff1a","")
                    if(u":" in content):
                    	content = content.replace(":","")
                    keyword = content[2:]
                    url = "https://en.wikipedia.org/wiki/" + keyword
                    headers = {
                        'Connection': 'Keep-Alive',
                        'Accept': '*/*',
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36'}
                    req = urllib2.Request(url, headers=headers)
                    response = urllib2.urlopen(req)
                    html = response.read().decode('utf-8')
                    soup = BeautifulSoup(html,'lxml')
                    short = str(soup.find_all('p')[0])
                    short = re.sub(r'<.*?>', '', short)
                    short = re.sub(r'\n', '', short)
                    return self.render.reply_text(fromUser,toUser,int(time.time()),short)
                
                elif(content == u"xueqiu1"):
                    send_headers = {
                        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36',
                        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Connection':'keep-alive',
                        'Host':'xueqiu.com',
                        'Cookie':'s=w9713t2fsq; bid=41db2909e9d630e225ada5dfceb199e9_iou6twpw; webp=0; xq_a_token=413c59ff783388c3d39ea09fa8cb9f9ea28fe1dd; xqat=413c59ff783388c3d39ea09fa8cb9f9ea28fe1dd; xq_r_token=efdf6fd284d34630d0146ff628021b47b13d3da0; xq_token_expire=Fri%20Aug%2019%202016%2013%3A14%3A15%20GMT%2B0800%20(CST); xq_is_login=1; u=6642285651; __utma=1.624231571.1464623177.1469435165.1469438670.10; __utmc=1; __utmz=1.1464623177.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); Hm_lvt_1db88642e346389874251b5a1eded6e3=1467609160,1469277371,1469423650; Hm_lpvt_1db88642e346389874251b5a1eded6e3=1469439295; snbim_minify=true'
}
                    
                    url = "https://xueqiu.com/stock/rank.json?size=20&type=10&_=1463117851729"
                    req = urllib2.Request(url,headers = send_headers)
                    response = urllib2.urlopen(req)
                    html = response.read().decode('utf-8')
                    html_hour = eval (html)
                    temp = ''
                    for i in html_hour['ranks']:
                        code = i['code']
                        name = i['name']
                        current = i['quote_current']
                        change = str(i['quote_percentage']) + "%"
                        url = "https://xueqiu.com/S/"
                        url = str(url) + str(code)
                        temp = temp + "\n" + code + " " + name + " " + "现价：" + current + " " + "涨跌：" + change + "\n" + url
                    return self.render.reply_text(fromUser,toUser,int(time.time()),"雪球1小时最热门股票：" + "\n" + temp)
                
                elif(content == u"xueqiu24"):
                    send_headers = {
                        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36',
                        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Connection':'keep-alive',
                        'Host':'xueqiu.com',
                        'Cookie':'s=w9713t2fsq; bid=41db2909e9d630e225ada5dfceb199e9_iou6twpw; webp=0; xq_a_token=413c59ff783388c3d39ea09fa8cb9f9ea28fe1dd; xqat=413c59ff783388c3d39ea09fa8cb9f9ea28fe1dd; xq_r_token=efdf6fd284d34630d0146ff628021b47b13d3da0; xq_token_expire=Fri%20Aug%2019%202016%2013%3A14%3A15%20GMT%2B0800%20(CST); xq_is_login=1; u=6642285651; __utma=1.624231571.1464623177.1469435165.1469438670.10; __utmc=1; __utmz=1.1464623177.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); Hm_lvt_1db88642e346389874251b5a1eded6e3=1467609160,1469277371,1469423650; Hm_lpvt_1db88642e346389874251b5a1eded6e3=1469439295; snbim_minify=true'
}
                    url = "https://xueqiu.com/stock/rank.json?size=20&_type=10&type=20"
                    req = urllib2.Request(url,headers = send_headers)
                    response = urllib2.urlopen(req)
                    html = response.read().decode('utf-8')
                    html_hour = eval (html)
                    temp = ''
                    for i in html_hour['ranks']:
                        code = i['code']
                        name = i['name']
                        current = i['quote_current']
                        change = str(i['quote_percentage']) + "%"
                        url = "https://xueqiu.com/S/"
                        url = str(url) + str(code)
                        temp = temp + "\n" + code + " " + name + " " + "现价：" + current + " " + "涨跌：" + change + "\n" + url
                    return self.render.reply_text(fromUser,toUser,int(time.time()),"雪球24小时最热门股票：" + "\n" + temp)
                
                elif(content == u"lhb"):
                    send_headers = {
                        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36',
                        'Accept':'application/json, text/javascript, */*; q=0.01',
                        'Connection':'keep-alive',
                        'Host':'xueqiu.com',
                        'Cookie':'s=w9713t2fsq; bid=41db2909e9d630e225ada5dfceb199e9_iou6twpw; webp=0; xq_a_token=413c59ff783388c3d39ea09fa8cb9f9ea28fe1dd; xqat=413c59ff783388c3d39ea09fa8cb9f9ea28fe1dd; xq_r_token=efdf6fd284d34630d0146ff628021b47b13d3da0; xq_token_expire=Fri%20Aug%2019%202016%2013%3A14%3A15%20GMT%2B0800%20(CST); xq_is_login=1; u=6642285651; __utma=1.624231571.1464623177.1469435165.1469438670.10; __utmc=1; __utmz=1.1464623177.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); Hm_lvt_1db88642e346389874251b5a1eded6e3=1467609160,1469277371,1469423650; Hm_lpvt_1db88642e346389874251b5a1eded6e3=1469439295; snbim_minify=true'
}
                    url = "https://xueqiu.com/stock/f10/bizunittrdinfo.json?"
                    req = urllib2.Request(url,headers = send_headers)
                    response = urllib2.urlopen(req)
                    html = response.read().decode('utf-8')
                    lhb = json.loads(html)
                    cd = ""
                    for i in lhb['list'][0:15]:
                        code = i['symbol']
                        biz = i['tqQtBizunittrdinfo']['bizsunitname']
                        typedesc = i['tqQtBizunittrdinfo']['typedesc']
                        name = i['name']
                        url = "https://xueqiu.com/S/" + str(code) + "/LHB"
                        cd = cd + code + " " + name + " ("  + typedesc + ")" + "\n" + url + "\n"
                        #break
                    return self.render.reply_text(fromUser,toUser,int(time.time()),u"今日龙虎榜：" + "\n" + cd)
                
                elif(content[0:2] == u"快递"):
                    if(u"+" in content):
                    	content = content.replace("+","")
                    if (u"\uff1a" in content):
                        content = content.replace(u"\uff1a","")
                    if(u":" in content):
                    	content = content.replace(":","")
                    keyword = content[2:]
                    url = "https://m.kuaidi100.com/autonumber/auto?num="+keyword
                    html = json.loads(get_html(url))
                    all = []
                    for i in html:
                        com = i['comCode']
                        url_pro = "https://m.kuaidi100.com/query?type=" + com + "&postid=" + keyword
                        ht = get_html(url_pro)
                        cd = json.loads(ht)
                        if u'data' in ht:
                            all.append(com + "\n")
                            for each in cd['data']:
                                all.append(each['time'] + "\n" + each['context'] + "\n")
                        break
                    if ''.join(all) == "":
                        all = ["对不起，您的输入有误"]
                                
                    return self.render.reply_text(fromUser,toUser,int(time.time()),''.join(all)) 
            	
            	elif(content == u"微博热点"):
                    url = "http://weibo.cn/pub/?tf=5_005"
                    headers = {
                                'Connection': 'Keep-Alive',
                                'Accept': 'text/html, application/xhtml+xml, */*',
                               'Accept-Language': 'en-US,en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
                                'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko'}
                    req = urllib2.Request(url, headers = headers)
                    opener = urllib2.urlopen(req)
                    html = opener.read().decode("utf-8")
                    rex = r'(?<=div class="c"><a href=").{60,79}(?=</a>)'
                    ss = re.findall(rex,html)
                    string = u""
                    for i in ss:
                        string = string + i.replace('>','\n')+"\n"
                    return self.render.reply_text(fromUser,toUser,int(time.time()),string.replace('"',''))
                
                elif((content[0:2] == u"翻译") and (re.findall(r"[a-zA-Z]",content))):
                    if(u"+" in content):
                    	content = content.replace("+","")
                    if (u"\uff1a" in content):
                        content = content.replace(u"\uff1a","")
                    if(u":" in content):
                    	content = content.replace(":","")
                    content = content[2:]
                    url = 'http://fanyi.baidu.com/v2transapi'
                    
                    head = {}
                    head['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36'
                    
                    data = {}
                	
                    data['to'] = 'zh'
                    data['from'] = 'en'
                    data['query'] = content
                    data['transtype'] = 'realtime'
                    data['simple_means_flag'] = '3'
                    data = urllib.urlencode(data)
                    req = urllib2.Request(url, data)
                    opener = urllib2.urlopen(req)
                    html = opener.read().decode("utf-8")
                    
                    temp = json.loads(html)
                    
                    translation = temp['trans_result']['data'][0]['dst']

                    return self.render.reply_text(fromUser,toUser,int(time.time()),translation)
                
                elif(content[0:2] == u"翻译"):
                    if(u"+" in content):
                    	content = content.replace("+","")
                    if (u"\uff1a" in content):
                        content = content.replace(u"\uff1a","")
                    if(u":" in content):
                    	content = content.replace(":","")
                    content = content[2:]
                    url = 'http://fanyi.baidu.com/v2transapi'
                    
                    head = {}
                    head['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36'
                    
                    data = {}
                	
                    if type(content).__name__ == "unicode":
                    	content = content.encode('UTF-8')
                    data['to'] = 'en'
                    data['from'] = 'zh'
                    data['query'] = content
                    data['transtype'] = 'realtime'
                    data['simple_means_flag'] = '3'
                    data = urllib.urlencode(data)
                    req = urllib2.Request(url, data)
                    opener = urllib2.urlopen(req)
                    html = opener.read().decode("utf-8")
                    
                    temp = json.loads(html)
                    
                    translation = temp['trans_result']['data'][0]['dst']

                    return self.render.reply_text(fromUser,toUser,int(time.time()),translation)
                
                elif(content == u"h"):
                    return self.render.reply_text(fromUser,toUser,int(time.time()),u"回复城市+天气，如“北京天气”，查询近期天气。\n回复电影+电影名称，如“电影爆裂鼓手”，获取电影下载链接（暂时无法使用）\n回复股票+股票代码，如“股票600000”获取实时股票信息。\n回复快递+号码，如“快递0123456789”，查询快递信息。\n回复“翻译+翻译内容”，如“翻译maize”，为您翻译文字（目前支持英汉互译）。\n回复“维基+搜索内容”，如“维基contig”，为您维基百科（仅支持英语）。\n回复“迅雷会员”获取每日免费迅雷会员。\n回复“微博热点”，获取微博热门话题。\n回复人像图片，可识别性别和年龄（图片小于1M）。\n我现在还在开发中，还没有什么功能，希望大家多提意见噢~")
            	
                elif((u"黄育敏" in content) or (u"黄芋头" in content)  or (u"黄玉米" in content)  or (u"芋头" in content)):
                    return self.render.reply_text(fromUser,toUser,int(time.time()),u"啊！你说的是那个帅气的男子吗^_^")
                
                elif(content == u"雪球" or content == u"xueqiu"):
                    return self.render.reply_text(fromUser,toUser,int(time.time()),u"回复“xueqiu1”获取雪球每小时热门股票，回复“xueqiu24”获取雪球24小时热门股票，回复“lhb”获取每日龙虎榜。")
                
                elif(content == u"迅雷会员"):
                        send_headers = {
                                'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36',
                                'Accept':'*/*',
                                'Connection':'keep-alive',
                                'Host':'521xunlei.com',
                                #'Cookie':'JSESSIONID=73FE9B632C8B67521EFB05EB92433D54'
                        }
                        url = "http://521xunlei.com/portal.php"
                        
                        req = urllib2.Request(url,headers = send_headers)
                        response = urllib2.urlopen(req)
                        html = response.read().decode('gbk')
                        soup = BeautifulSoup(html, "lxml")
                        for i in soup.find_all('li'):
                            i = i.contents
                            if str (i[0]) == "\n" and str (i[2]) == " ":
                                    temp = str (i[3])
                                    #print (type(temp))
                                    pos_start = temp.find('<a href="') + len ('<a href="')
                                    pos_end = temp.find('" target="_blank"')
                                    html = temp[pos_start:pos_end]
                                    temp_start = temp.find('title="') + len ('title="')
                                    temp_end = temp.find('>',temp_start) - 1
                                    cd = ("-"*80)
                                    out = ("时间:" + temp[temp_start:temp_end])
                                    send_headers = {
                                    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36',
                                    'Accept':'*/*',
                                    'Connection':'keep-alive',
                                    'Host':'521xunlei.com',
                                    #'Cookie':'JSESSIONID=73FE9B632C8B67521EFB05EB92433D54'
                                    }
                                    url = "http://521xunlei.com/"
                                    url = str (url) + str (html)
                                    '''
                                    req = urllib2.Request(url,headers = send_headers)
                                    response = urllib2.urlopen(req)
                                    html = response.read().decode('gbk')
                                    soup = BeautifulSoup(html,'lxml')
                                    count = 0
                                    for i in soup.find_all("br"):
                                        if (i.string):
                                            te = i.string
                                            out = out + "\n" + (''.join(te)).encode('utf-8')
                                    '''
                                    break
                        return self.render.reply_text(fromUser,toUser,int(time.time()),url)
                
                elif(content[0:2] == u"股票"):
                    if(u"+" in content):
                    	content = content.replace("+","")
                    if (u"\uff1a" in content):
                        content = content.replace(u"\uff1a","")
                    if(u":" in content):
                    	content = content.replace(":","")
                    number = content[2:]
                    if ((str (number)[0]) == "6"):
                        number = "SH" + str (number)
                    elif ((str (number)[0]) == "5"):
                        number = "SH" + str (number)
                    else:
                        number = "SZ" + str (number)
                    send_headers = {
                        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36',
                        'Accept':'application/json, text/javascript, */*; q=0.01',
                        'Connection':'keep-alive',
                        'Host':'xueqiu.com'
                    }
                    url = "https://xueqiu.com/S/"
                    url = str (url) + str (number)
                    req = urllib2.Request(url,headers = send_headers)
                    response = urllib2.urlopen(req)
                    html = response.read().decode('utf-8')
                    pos_start = html.find('SNB.data.quote = ') + len('SNB.data.quote = ')
                    pos_end = html.find('}',pos_start) + 1
                    data = html[pos_start:pos_end]
                    dic = eval(data)
                    out =  (str (dic['symbol']) + " " + str (dic['name']) + " " + str (dic['current']) + " " + str (dic['percentage']) + "% " + str (dic['change']) + " " + str (dic['parsedtime']) + "\n" + url)
                    soup = BeautifulSoup(html,"lxml")
                    for i in soup.find_all('td'):
                        con = i.contents[0]
                        cd = i.find('span').string
                        out = out + "\n" + (''.join(con)).encode('utf-8') + (''.join(cd)).encode('utf-8')
                    return self.render.reply_text(fromUser,toUser,int(time.time()),out)
                
                elif (u'歌' in content):
                    try:
                        musiclist = [
                                     		[r'https://mingo456.sinacloud.net/Hyukoh+-+%EC%9C%84%EC%9E%89%EC%9C%84%EC%9E%89.mp3',u'Hyukoh - 위잉위잉',''],
                                     		[r'https://mingo456.sinacloud.net/Lisa+Miskovsky+-+Still+Alive+%28Instrumental%29+-+instrumental.mp3',r'Still Alive',''],
                                            [r'https://mingo456.sinacloud.net/Maroon+5+-+Feelings.mp3',r'Maroon5 Feelings',''],
                                            [r'https://mingo456.sinacloud.net/Maroon+5+-+It+Was+Always+You.mp3',r'Maroon5 It Was Always You',''],
                                            [r'https://mingo456.sinacloud.net/Taylor+Swift+-+Blank+Space.mp3',r'Blank Space',''],
                                            [r'https://mingo456.sinacloud.net/Taylor+Swift+-+How+You+Get+The+Girl.mp3',r'How You Get The Girl',''],
                                            [r'https://mingo456.sinacloud.net/Taylor+Swift+-+Style.mp3',r'Style',''],
                                            [r'https://mingo456.sinacloud.net/Taylor+Swift+-+Wildest+Dreams.mp3',r'Wildest Dreams','']
                                     		]
                        music = random.choice(musiclist)
                        musicurl = music[0]
                        musictitle = music[1]
                        musicdes = music[2]
                        return self.render.reply_music(fromUser,toUser,int(time.time()),musictitle,musicdes,musicurl)
                    except Exception , e:
                        return self.render.reply_music(fromUser,toUser,int(time.time()),e)
                
                else:
                    	s = requests.session()
                    	url = 'http://www.tuling123.com/openapi/api'
                        da = {"key": "672aa246ec6e6af6db7d32ce8ccd316d", "info": content, "userid": userid}
                        data = json.dumps(da)
                        r = s.post(url, data=data)
                        j = eval(r.text)
                        code = j['code']
                        if code == 100000:
                            recontent = j['text']
                        elif code == 200000:
                            recontent = j['text']+j['url']
                        elif code == 302000:
                            recontent = j['text']+j['list'][0]['info']+j['list'][0]['detailurl']
                        elif code == 308000:
                            recontent = j['text']+j['list'][0]['info']+j['list'][0]['detailurl']
                        else:
                            recontent = '这货还没学会怎么回复这句话'
                        return self.render.reply_text(fromUser,toUser,int(time.time()),recontent)
