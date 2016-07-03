# -*- coding: utf-8 -*-  
   
import urllib2  
import urllib  
import re  
import os  
  
#----------- 加载处理唱吧用户主页 -----------  
class Spider_Model:  
      
    def __init__(self,userid):  
        self.uid = userid
        self.List=[]  
  
    # 将所有的作品都抠出来，添加到列表中并且返回列表  
    def GetList(self,uid):  
        myUrl = "http://changba.com/u/" + uid  
        user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)' 
        headers = { 'User-Agent' : user_agent } 
        req = urllib2.Request(myUrl, headers = headers) 
        myResponse = urllib2.urlopen(req)
        myPage = myResponse.read()  
        #encode的作用是将unicode编码转换成其他编码的字符串  
        #decode的作用是将其他编码的字符串转换成unicode编码  
        unicodePage = myPage.decode("utf-8")  
  
        # 找出所有href以'/s/'开头，且其内部有div class="userPage-work-detail"的标记  
        #re.S是任意匹配模式，也就是.可以匹配换行符S
        myItems = re.findall('<a href="/s/(.*?)".*?>(.*?)<div class="userPage-work-detail">.*?</a>',unicodePage,re.S)  
        items = [] 
        for item in myItems:  
            # item 中第一项是href中'/s/'后面的内容，也就是歌曲  
            # item 中第二项是<a>标签之后，<div>标签之前的内容，也就是歌曲名称  
            items.append([item[0].replace("\n",""),item[1].replace("\n","").replace("\t","").replace("\r","")]) 
        self.List = items
  
          
    #根据mp3url查找MP3链接并下载     
    def Download(self,mp3url,mp3nm):
        myUrl = "http://changba.com/s/" + mp3url  
        user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)' 
        headers = { 'User-Agent' : user_agent } 
        req = urllib2.Request(myUrl, headers = headers) 
        myResponse = urllib2.urlopen(req)
        myPage = myResponse.read()  
        #encode的作用是将unicode编码转换成其他编码的字符串  
        #decode的作用是将其他编码的字符串转换成unicode编码  
        unicodePage = myPage.decode("utf-8")  
  
        #找出其中的mp3文件的链接地址，
        #re.S是任意匹配模式，也就是.可以匹配换行符S '[^a="]http://(\w+).mp3
        myItems = re.search("http://(\w+).changba.com/(\S+)(\d+).mp3",unicodePage)
        if(myItems!=None):
            downurl=myItems.group()
            #文件存储在用户文件夹下
            urllib.urlretrieve(downurl,os.path.expanduser('~/Downloads/%s.mp3' % mp3nm))
            print "mp3文件下载完成"
        else:
            print "未找到MP3文件" 
          
    def Start(self):  
  
        print u'正在下载请稍候......'  
          
        self.GetList(self.uid)  
        count = 1  
        for item in self.List:
            print u'正在下载第',count,"首歌"
            self.Download(item[0], item[1])
            print item
            count+=1

  
  
#----------- 程序的入口处 -----------  
print u""" 
--------------------------------------- 
   程序：唱吧爬虫 
   版本：0.1 
   作者：zhm 
   日期：2016-07-02 
   语言：Python 2.7 
   操作：输入用户id并按下回车 
   说明：用户id是指用户主页链接尾部的一串数字，例如http://changba.com/u/90092393
   功能：依次下载该用户唱的歌曲 
--------------------------------------- 
"""
  
print u'请输入用户id并按下回车：'  
userid=raw_input('')  
myModel = Spider_Model(userid)  
myModel.Start()  
