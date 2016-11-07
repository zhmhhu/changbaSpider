# -*- coding: utf-8 -*-  
   
import urllib2  
import re  
import os  
import json
import requests
import time 
#----------- 加载处理唱吧用户数据 -----------  
class Spider_Model:  
      
    def __init__(self,userid):
        self.headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36"
            " (KHTML, like Gecko) Chrome/33.0.1750.152 Safari/537.36"}
        self.cookies = dict(appver="1.2.1", os="osx")  
        self.uid = userid
        self.threadnum=15
        self.threadpool=[]
        
        
    def show_progress(self, response):
        content = bytes()
        total_size = response.headers.get('content-length')
        if total_size is None:
            content = response.content
            return content
        else:
            total_size = int(total_size)
            bytes_so_far = 0
            for chunk in response.iter_content():
                content += chunk
                bytes_so_far += len(chunk)
                progress = round(bytes_so_far * 1.0 / total_size * 100)
                self.signal_load_progress.emit(progress)
            return content

    def http_request(self, method, action, query=None, urlencoded=None, callback=None, timeout=60):
        res = None
        if method == "GET":
            res = requests.get(action, headers=self.headers, cookies=self.cookies, timeout=timeout)
        elif method == "POST":
            res = requests.post(action, query, headers=self.headers, cookies=self.cookies, timeout=timeout)
        elif method == "POST_UPDATE":
            res = requests.post(action, query, headers=self.headers, cookies=self.cookies, timeout=timeout)
            self.cookies.update(res.cookies.get_dict())
            self.save_cookies()
        content = self.show_progress(res)
        content_str = content.decode('utf-8')
        content_dict = json.loads(content_str)
        return content_dict     
  
    def user_playlist(self, uid,pageNum):
        action = 'http://changba.com/member/personcenter/loadmore.php?ver=1&type=0&curuserid=-1&pageNum='+str(pageNum)+'&userid='+uid
        #action = 'http://changba.com/member/personcenter/loadmore.php?ver=1&type=0&curuserid=-1&pageNum=1&userid='+uid
        res_data = self.http_request('GET', action)
        return res_data
    # 获取所有歌曲信息，songname表示歌名，ismv表示是否mv,workid用于获取mv地址或者歌曲mp3文件 ,enworkid用于获取作品首页
    def getNewlist(self,uid):
        pageNo=0
        playlists=[]
        while(self.user_playlist(uid,pageNo) !=[]):
            playlist = self.user_playlist(uid,pageNo)
            for elem in playlist:
                playlists.append(elem)
            pageNo = pageNo+1
            #print playlists
        items = [] 
        for item in playlists:  
            items.append([item['songname'],item['ismv'],item['workid'],item['enworkid']]) 
        return items
  
    # 通过用户主页编号，获取userid  
    def getUserid(self,uid):  
        myUrl = "http://changba.com/u/" + uid
        myPage = requests.get(myUrl, headers=self.headers)
        myPage.encoding = "utf-8"  #将其他编码的字符串转换成unicode编码  
        unicodePage = myPage.content
  
        # 找出所有href以'/s/'开头，且其内部有div class="userPage-work-detail"的标记  
        #re.S是任意匹配模式，也就是.可以匹配换行符S  userid = '(\d+)';
        myItems = re.findall("var userid = '(\d+)'",unicodePage,re.S)  
        for Item in myItems:           
            if(Item!=None):
                return Item
            else:
                return
    #通过id号下载歌曲及mv，下载链接不全面，已弃用       
    def DownloadNew(self,songNm,ismv,songID,uid):
        rstr = r"[\/\\\:\*\?\"\<\>\|]"  # '/\:*?"<>|'
        mp3renm = re.sub(rstr, "", songNm) #剔除非法的文件名字符串
        mp3UrlEx = 'http://qiniuuwmp3.changba.com/'
        mvUrlEx = 'http://letv.cdn.changba.com/userdata/video/'
        savePath = os.path.dirname(r'D:/Downloads/%s' % uid)#下载路径在用户文件夹下
        if not os.path.isdir(savePath):
            os.makedirs(savePath)
        if(ismv.find('none') !=-1):
            try:
                f = urllib2.urlopen(mp3UrlEx+songID+'.mp3') 
                data = f.read() 
                with open(savePath+"/"+ mp3renm+".mp3",'w+b') as code:     
                    code.write(data)
                print u'歌曲',mp3renm,u"下载成功"
                code.close()
            except IOError,e:
                print("open exception: %s: %s\n" %(e.errno, e.strerror)) 
                print u'歌曲',mp3renm,u"下载失败"
        elif(ismv.find('inline') != -1):
            try:
                f = urllib2.urlopen(mvUrlEx+songID+'.mp4') 
                data = f.read() 
                with open(savePath+"/"+ mp3renm+".mp4",'w+b') as code:     
                    code.write(data)
                print u'视频',mp3renm,u"下载成功"
                code.close()
            except IOError,e:
                print("open exception: %s: %s\n" %(e.errno, e.strerror)) 
                print u'视频',mp3renm,u"下载失败"         
          
    def Start(self):  
        #import thread  
        print u'正在下载请稍候......'  
        userid=self.getUserid(self.uid)
        List =self.getNewlist(userid)  
        i=0
        while i<len(List):            
            j=0
            while j<self.threadnum and i+j < len(List):
                time.sleep(1)
                downloadThread = DownloadThread(List[i+j][0],List[i+j][1],List[i+j][2],List[i+j][3],self.uid,j)
                downloadThread.start()
                self.threadpool.append(downloadThread)
                j+=1
            i+=j
            for thread in self.threadpool:
                thread.join(60)  #设置超时参数，60秒之后释放主线程

import threading
#多线程下载歌曲或MV
class DownloadThread(threading.Thread):
    def __init__(self,songNm,ismv,songID,songUrl,uid,threadnm):
        threading.Thread.__init__(self)
        self.songNm = songNm
        self.ismv = ismv
        self.songID = songID
        self.songUrl = songUrl
        self.uid = uid
        self.threadnm='Thread-'+str(threadnm)
    def run(self):
        try:
            rstr = r"[\/\\\:\*\?\"\<\>\|]"  # '/\:*?"<>|'
            mp3renm = re.sub(rstr, "", self.songNm) #剔除非法的文件名字符串
            #mp3UrlEx = 'http://qiniuuwmp3.changba.com/'
            mvUrlEx = 'http://letv.cdn.changba.com/userdata/video/'
            savePath = os.path.dirname(r'D:/Downloads/%s' % self.uid)#下载路径在用户文件夹下
            if not os.path.isdir(savePath):
                os.makedirs(savePath)
            if(self.ismv.find('none') !=-1):
                myUrl = "http://changba.com/s/" + self.songUrl  
                headers = { "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36"
                            " (KHTML, like Gecko) Chrome/33.0.1750.152 Safari/537.36"}
                myPage = requests.get(myUrl, headers=headers)
                myPage.encoding = "utf-8"  #将其他编码的字符串转换成unicode编码
                unicodePage = myPage.content
                #找出其中的mp3文件的链接地址，
                #re.S是任意匹配模式，也就是.可以匹配换行符S '[^a="]http://(\w+).mp3  http://.*?.changba.com/.*?d+.mp3
                myItems = re.search("http://(\S+).changba.com/(\S+)(\d+).mp3",unicodePage)
                if(myItems!=None):
                    downurl=myItems.group()
                    try:
                        f = urllib2.urlopen(downurl,timeout=10) 
                        data = f.read() 
                        with open(savePath+"/"+ mp3renm+".mp3",'w+b') as code:     
                            code.write(data)
                        print self.threadnm,u'歌曲',mp3renm, u"下载成功"
                        code.close()
                    except IOError,e:
                        print self.threadnm,u'歌曲',mp3renm, u"下载失败"
                        print("open exception: %s: %s\n" %(e, e.strerror)) 
                else:
                    print self.threadnm,u'歌曲未找到'
            elif(self.ismv.find('inline') != -1):
                    try:
                        f = urllib2.urlopen(mvUrlEx+self.songID+'.mp4',timeout=20) 
                        data = f.read() 
                        with open(savePath+"/"+ mp3renm+".mp4",'w+b') as code:     
                            code.write(data)
                        print self.threadnm,u'视频',mp3renm,u"下载成功"
                        code.close()
                    except IOError,e:
                        print self.threadnm,u'视频',mp3renm,u"下载失败"
                        print("open exception: %s: %s\n" %(e, IOError)) 
        except Exception,e:
            print u'下载失败,',self.threadnm,'退出'
            print ("exception: %s: %s\n" %(e, Exception)) 
            return None  
  
  
#----------- 程序的入口处 -----------  
print u""" 
--------------------------------------- 
   程序：唱吧爬虫 
   版本：0.2 
   作者：zhm 
   日期：2016-11-07 
   语言：Python 2.7 
   操作：输入用户主页编号并按下回车 
   说明：用户用户主页编号是指用户主页链接尾部的一串数字,例如33085747
   功能：依次下载该用户唱的歌曲 
--------------------------------------- 
"""
  
print u'请输入用户主页编号并按下回车：'
userid=raw_input('')  
myModel = Spider_Model(userid)  
myModel.Start()  
