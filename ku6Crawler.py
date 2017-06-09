#!/usr/bin/python
# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import urllib,urllib2,re,os
import json
import pymysql.cursors
import hashlib
import sys

reload(sys)
sys.setdefaultencoding('utf8')
#windows信息的保存路径
targetPathVedio = "D:\\resources\\crawler\\vedios"
targetPathImg = "D:\\resources\\crawler\\images"
targetPathFile = "D:\\resources\\crawler\\files"
#科学实验路径
# targetPathVedio = "/server/python/video"
# targetPathImg = "/server/python/images"
# targetPathFile = "/server/python/files"

#搞笑视频路径，修改的地方包括文件类型fileclass
#targetPathVedio = "/server/jokeResource/video"
#targetPathImg = "/server/jokeResource/images"
#targetPathFile = "/server/jokeResource/files"

#分页信息
page = 1;
# 科学网址  
baseurl = "http://so.ku6.com/search?q=%E7%A7%91%E5%AD%A6%E5%AE%9E%E9%AA%8C" 
#搞笑视频网址
#baseurl = "http://so.ku6.com/search?q=%E5%A8%B1%E4%B9%90"
#伪装浏览器访问，避免某些站点的反爬虫
headers={'Connection': 'Keep-Alive',  
         'Accept': 'text/html, application/xhtml+xml, */*',  
         'Accept-Language': 'en-US,en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',  
         'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko'  
         }
count=1; 

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
    
#保存页面内容
def savePage(soup,title):
    page = soup.prettify()   
    f = open(targetPathFile+"\\"+title+".text", "w",encoding='utf-8')
    f.write(page)
    #关闭打开的文件
    f.close()      

#md5加密
def md5(string):    
    m = hashlib.md5(string.encode("utf8"))
    return m.hexdigest()

#保存信息到mysql
def saveReSourceInfoToMySql(vidInfo):
    # 了解mysql数据库
    connection = pymysql.connect(host='127.0.0.1',
                            user='huanfeng',
                            password='huanfeng',
                            db='pay',
                            charset='utf8',
                            cursorclass=pymysql.cursors.DictCursor)
    
    try:      
        with connection.cursor() as cursor:
            #根据filename查重，filename是filetitle的md5值
            filetitle=vidInfo.get("data").get("t")
            filename = md5(filetitle)
            #{'data': {'vid': 'cQrZjv4qIT4NFKWkNi0irg..', 's': 0, 't': '此生必看的科学实验_【高清版】11', 'tag': '视频:此生必看的科学实验_【高清版】11', 'desc': '视频:此生必看的科学实验_【高清版】11', 'uploadtime': 1326434569, 'srctype': 0, 'flag': '', 'u': 7282810, 'ad': 1, 'ad_pic': 'http://vi2.ku6img.com/data1/p13/cms/2016/12/22/pic_1482386239930.jpg', 'ad_pic_link': 'http://v.ku6.com/show/cPiWsUApVrG6YeKbF9b41A...html', 'ad_audio': 1, 'comm': 0, 'fav': 0, 'c': 127000, 'picpath': 'http://vi1.ku6img.com/data1/p5/ku6video/2012/1/13/14/1329644212729_14482882_14482882/5.jpg', 'bigpicpath': 'http://vi1.ku6img.com/data1/p5/ku6video/2012/1/13/14/1329644212729_14482882_14482882/105.jpg', 'commvid': '', 'hd': 0, 'logocoors': '', 'profitAddr': '', 'sndap2p': '1', 'r': 99, 'mediasrc': 0, 'aid': 0, 'vtype': 1, 'vtime': 172, 'vtimems': 172000, 'videosize': '299@8398593', 'f': 'http://main.gslb.ku6.com/s1/LQ0_Bp80oaHOXhW-/1326434764653/5e576599f9f6f64f5bc80d158545a9c6/1495506125287/v599/55/92/b194a065d5ffa95005108d5365ccb8c4-f4v-h264-aac-329-32-172663.0-7927092-1326434666834-9596659525ec7b22311dfb889ece260a-1-00-00-00.f4v'}, 'status': 1}
            titleMD5=md5(filetitle)
            imgUrl=vidInfo.get("data").get("picpath")  
            suffix = imgUrl.rindex('.')
            fileimg = titleMD5+imgUrl[suffix:]            
            vedioUrl=vidInfo.get("data").get("f") 
            startName = vedioUrl.rindex('.')
            try:
                endName = vedioUrl.rindex('?')    
                filepath = titleMD5+vedioUrl[startName:endName]                
                filetype = vedioUrl[startName:endName]
            except Exception :
                filepath = titleMD5+vedioUrl[startName:]
                filetype = vedioUrl[startName:]
            fileurl = vedioUrl
            filesrc = 'ku6'
            fileSize = vidInfo.get("data").get("videosize")
            fileclass=''
            sql = "SELECT `id` FROM `t_file_info` WHERE `filename`=%s"
            cursor.execute(sql, (titleMD5))
            result = cursor.fetchone()
            if result==None:                
                with connection.cursor() as cursor:
                    # Create a new record
                    sql = "INSERT INTO t_file_info (\
                    filename,filetitle,filepath,filetype,fileurl,filesrc,fileclass,fileimg,fileSize)\
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
                    cursor.execute(sql, (filename,filetitle,filepath,filetype,fileurl,filesrc,fileclass,fileimg,fileSize))
                    # connection is not autocommit by default. So you must commit to save
                    # your changes.
                    connection.commit()
                    return True;
            else:
                return False;
    
    finally:
        connection.close()
        

#解析内容
def parseAndSaveCon(aHref):

    try:
        req = urllib2.Request(url=aHref, headers=headers)
        res = urllib2.urlopen(req)
        data = res.read().decode('gbk')
        flashVars = re.findall(r'\'flashVars\':.*?;',data)
        vid=flashVars[0].split('&')[5][4:]
        print('解析的vid：'+vid)
        urlDiv='http://v.ku6.com/fetchVideo4Player/'+vid+'.html'
        print('即将请求数据URL：'+urlDiv)
        reqVid = urllib2.Request(url=urlDiv, headers=headers)
        resVid = urllib2.urlopen(reqVid)
        dataVid = resVid.read().decode('gbk')
        vidInfo = json.loads(dataVid)
        print(vidInfo)
        #'picpath': 'http://i99.ku6.com/20094/25/21/1243538633756/2.jpg',        
        vedioUrl=vidInfo.get("data").get("f")        
        #print("解析的视频地址："+vedioUrl)
        vedioTitle=vidInfo.get("data").get("t")
        titleMD5=md5(vedioTitle)
        #查询且保存视频图片
        imgUrl=vidInfo.get("data").get("picpath")  
        suffix = imgUrl.rindex('.')
        imgSaveName = titleMD5+imgUrl[suffix:]
        imgAllPath = os.path.join(targetPathImg,imgSaveName)
        
        startName = vedioUrl.rindex('.')
        try:
            endName = vedioUrl.rindex('?')    
            VedioSaveName = titleMD5+vedioUrl[startName:endName]                
                        
        except Exception :
            VedioSaveName = titleMD5+vedioUrl[startName:]
        
        vedioAllPath = os.path.join(targetPathVedio,VedioSaveName)
        if not saveReSourceInfoToMySql(vidInfo):
            print("资源已经存在，即将结束："+vedioAllPath)
            return;

        #下载保存视频
        print("准备下载视频："+vedioAllPath)
        downAndSave(vedioUrl,vedioAllPath)
        #下载保存视频图片
        print("准备下载图片："+imgAllPath)
        downAndSave(imgUrl,imgAllPath)
        print("》》》》》》》》》》》》》》》》《《《《《《《《《《《《《《《")
    except Exception as e:
        print(e)
        
def saveContets(imgTaglist):
    if imgTaglist==None:
        return
    
    for img in imgTaglist:
        #获取此img的视频播放地址
        aHref = img.parent.get('href')
        print("即将解析页面："+ aHref)
        parseAndSaveCon(aHref)

if __name__ == '__main__':
    print('》》》》》》》》》》》将要执行酷6网资源爬取操作，预备工作已经完成。《《《《《《《《《《《《《')
    while True:
        url = baseurl+"&start="+str(page)
        print('进行分页查询，当前分页：'+str(page)+'。当前url格式:'+url)
        req = urllib2.Request(url=url, headers=headers)
        res = urllib2.urlopen(req)
        data = res.read().decode('utf-8')
        soup = BeautifulSoup(data)
        #img的数据比较准确，如果直接获取a的数量进行操作是不准确及难处理的。
        imgTaglist=soup.find_all(name='div',attrs={'class':'ckl_cotcent'})[0].find_all(name='img')
        #计算集合的个数
        imglistLength = len(imgTaglist)
        #资源的数量
        print('size：'+str(imglistLength))
        if imglistLength<=0 and page>90:
            print('此url查询内容为NULL，将结束查询:'+url)
            break
        saveContets(imgTaglist)
        page+=1
