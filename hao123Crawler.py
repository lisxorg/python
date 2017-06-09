#!/usr/bin/python
# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import urllib,urllib2,re
import json
import pymysql.cursors
import hashlib
import sys
import fileInfo2MysqlUtil,fileInfo
reload(sys)
sys.setdefaultencoding('utf8')

#分页信息,
page = 0;
# 网址  
baseurl = "http://v.baidu.com/v?fid=2000&word=%E7%A7%91%E5%AD%A6%E5%AE%9E%E9%AA%8C&rn=40&ct=905969664&ie=utf-8&du=0&pd=0&sc=0&" 
#伪装浏览器访问，避免某些站点的反爬虫
headers={'Connection': 'Keep-Alive',  
         'Accept': 'text/html, application/xhtml+xml, */*',  
         'Accept-Language': 'en-US,en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',  
         'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko'  
         }

#由于hao123的视频没有尾页，所以只能按照查询的个数来结束内容。预设的数量会大于实际数量。如果按照重复数来结束查询，由于hao123的视频跟
#其他来源的视频会存在很多重复，所以此方法效果不明显
vedioCount=0

#下载资源并保存  
def downAndSave(src,allPath):
    
    print('开始下载文件：'+allPath)
    try:
        print('正在下载文件：......')
        if src.startswith('http://'):
            urllib.urlretrieve(src,allPath)
        else:
            urllib.urlretrieve('http:'+src,allPath)
    except Exception as e:
        print("文件下载发生错误："+str(e)) 
    
    print("文件下载完成："+allPath)
    
#md5加密
def md5(string):    
    m = hashlib.md5(string.encode("utf8"))
    return m.hexdigest()

#保存信息到mysql
def saveReSourceInfoToMySql(vidInfo,filetype,fileurl,fileimg,fileclass):

    filetitle=vidInfo.get("ti")
    filename = md5(filetitle)
    filesrc = 'hao123'
    fileSize = vidInfo.get("rweight")
    #生成文件信息对象
    vedioFile=fileInfo.FileInfo(filename,filetitle,'',filetype,fileurl,filesrc,fileclass,fileimg,fileSize)
    #根据文件名查重
    if fileInfo2MysqlUtil.hasFileByFileName(filename):
        return False
    #保存文件对象
    fileInfo2MysqlUtil.saveFile2Mysql(vedioFile)
    return True


def parseVedio(info,aHref,titleMD5,imgUrl):
    global vedioCount
    try:
        #计算当前已经遍历的视频数量
        vedioCount=vedioCount+1       
        req = urllib2.Request(url=aHref, headers=headers)
        res = urllib2.urlopen(req)
        data = res.read().decode('utf-8')
        flashUrl = re.findall(r'var flashUrl =.*;',data)
        if len(flashUrl)<1:
            soup = BeautifulSoup(data)
            iframeSrc=soup.find_all(name='iframe')[0]['src']
            req = urllib2.Request(url=iframeSrc, headers=headers)
            res = urllib2.urlopen(req)
            data = res.read().decode('utf-8')
            flashUrl = re.findall(r'var flashUrl =.*;',data)
        
        vedioUrl = flashUrl[0][16:-2]
        print("解析出的视频地址："+vedioUrl)
#         if '?' in vedioUrl:
#             endName = vedioUrl.index('?')
#             vedioType = vedioUrl[0:endName]
#         else:
#             vedioType = vedioUrl
#         
#         start = vedioType.rindex('.')
#         vedioType=vedioType[start+1:]
#         vedioSaveName = titleMD5+"."+vedioType
#         vedioAllPath = os.path.join(targetPathVedio,vedioSaveName)
        if not saveReSourceInfoToMySql(info,"swf",vedioUrl,imgUrl,''):
            print("资源已经存在，即将结束："+titleMD5)
        else:
            print("已保存资源："+vedioUrl)
        print("当前已经爬取的视频数量："+str(vedioCount))
        #downAndSave(vedioUrl,vedioAllPath)    
    except Exception as e:
        print(e)
    
#解析内容
def parseAndSaveCon(info):
        global vedioCount
        #标题的MD5用作资源的链接和判重
        vedioTitle = info['ti']   
        imgUrl = info['pic']
        aHref = info['url']
        if not aHref.startswith('http://'):
            origin_url=info['origin_url']
            aHref=origin_url+aHref
               
            if not saveReSourceInfoToMySql(info,"swf",aHref,imgUrl,'link'):
                filename = md5(vedioTitle)
                print("资源已经存在，即将结束："+filename)
            else:
                print("已保存资源："+aHref)
                
            vedioCount=vedioCount+1  
            print("当前已经爬取的视频数量："+str(vedioCount))     
            return
            
        print("标题："+vedioTitle)
        print("图片："+imgUrl)    
        print("视频播放页面："+aHref)
        titleMD5=md5(vedioTitle)   
        #解析视频且保存
        parseVedio(info,aHref,titleMD5,imgUrl)
        print("》》》》》》》》》》》》》》》》《《《《《《《《《《《《《《《")

        
def saveContets(datas):
    if datas==None:
        return
    jo = json.loads(datas) 
    ves = jo['data']
    for info in ves:
        parseAndSaveCon(info)

if __name__ == '__main__':
    print('》》》》》》》》》》》将要执hao123影视网资源爬取操作，预备工作已经完成。《《《《《《《《《《《《《')
    global page
    while True:
        url = baseurl+"pn="+str(page)
        print('进行分页查询，当前分页：'+str(page)+'。当前url格式:'+url)
        req = urllib2.Request(url=url, headers=headers)
        res = urllib2.urlopen(req)
        data = res.read().decode('utf-8')
        soup = BeautifulSoup(data)
        if vedioCount >=45000:
            break;
        
        if soup==None :
            continue

        print("获取的列表信息："+data)
        datas = re.findall(r'{.*}\)',data)
        saveContets(datas[0][0:-1])
        page+=40
