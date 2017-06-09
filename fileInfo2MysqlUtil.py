# -*- coding: utf-8 -*-
import pymysql.cursors
import fileInfo

class mysqlConnection:
    
    def __init__(self):
        #生产主机链接
        # self.connection = pymysql.connect(host='rds6p6482p21s5lt5y80.mysql.rds.aliyuncs.com',
        #                         user='huanfeng',
        #                         password='huanfeng_2015',
        #                         db='pay',
        #                         charset='utf8',
        #                         cursorclass=pymysql.cursors.DictCursor)
        #本地链接
        self.connection = pymysql.connect(host='127.0.0.1',
                                user='huanfeng',
                                password='huanfeng',
                                db='hy_portal',
                                charset='utf8',
                                cursorclass=pymysql.cursors.DictCursor)
        
    #获取链接，需要关闭链接
    def getConnection(self):
        return self.connection
    
    #关闭链接
    def closeConnection(self,con):
        if con!=None:
            con.close()

#根据文件名判重，一般文件名是文件的标题MD5
def hasFileByFileName(fileName):
    if fileName==None:
        return True
    sql = "SELECT `id` FROM `t_file_info` WHERE `filename`=%s"
    try:
        myconne = mysqlConnection()
        conne=myconne.getConnection()
        with conne.cursor() as cursor:
            cursor.execute(sql, (fileName))
            result = cursor.fetchone()      
            if result!=None:      
                return True
            else:
                return False
    except Exception as e:
        print(e)
        
    finally:
        myconne.closeConnection(conne)
        
#保存文件信息      
def saveFile2Mysql(fileInfo):
    if fileInfo==None:
        return
   
    sql = "INSERT INTO t_file_info (filename,filetitle,filepath,filetype,\
        fileurl,filesrc,fileclass,fileimg,fileSize)\
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)" 
    try:

        myconne = mysqlConnection()
        conne=myconne.getConnection()
        with conne.cursor() as cursor:
            cursor.execute(sql, (fileInfo.fileName,fileInfo.fileTitle,
                                 fileInfo.filePath,fileInfo.fileType,
                                 fileInfo.fileUrl,fileInfo.fileSrc,
                                 fileInfo.fileClass,fileInfo.fileImg,fileInfo.fileSize))
            conne.commit()

    except Exception as e:
        print(e)
        
    finally:
        myconne.closeConnection(conne)
    
    
    
    