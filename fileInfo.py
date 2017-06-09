#! /usr/bin/python
# -*- coding: utf-8 -*-
#这是文件信息类
class FileInfo:
    def __init__(self,fileName,fileTitle,filePath,fileType,fileUrl,fileSrc,fileClass,fileImg,fileSize):
        self.fileName = fileName
        self.fileTitle = fileTitle
        self.filePath = filePath
        self.fileType = fileType
        self.fileUrl = fileUrl
        self.fileSrc = fileSrc
        self.fileClass = fileClass
        self.fileImg = fileImg
        self.fileSize = fileSize
        
    def __str__(self):
        msg='fileName:'+self.fileName+",fileTitle:" + self.fileTitle + ",filePath:"+self.filePath\
        +',fileType:'+self.fileType+ ",fileUrl:" + self.fileUrl +",fileSrc:" +self.fileSrc\
        +',fileClass:'+self.fileClass+ ",fileImg:" + self.fileImg+ ",fileSize:" +self.fileSize
        return msg

if __name__ == '__main__':
    shanghai=FileInfo('shanghai','23','man','1','2','3','4','5','6')
    print(shanghai)