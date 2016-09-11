# -*- coding: utf-8 -*-  
   
import urllib2  
import urllib  
import re  
import os  
import json
import requests  
#----------- 加载处理唱吧用户数据 -----------  
class Spider_Model:  
      
    def __init__(self,userid):  
        self.uid = userid
        self.List=[] 
        
        
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

    def http_request(self, method, action, query=None, urlencoded=None, callback=None, timeout=1):
        headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36"
                          " (KHTML, like Gecko) Chrome/33.0.1750.152 Safari/537.36"
        }
        cookies = dict(appver="1.2.1", os="osx")
        res = None
        if method == "GET":
            res = requests.get(action, headers=headers, cookies=cookies, timeout=timeout)
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
#         action = 'http://changba.com/member/personcenter/loadmore.php?ver=1&type=0&curuserid=-1&pageNum=1&userid='+uid
        res_data = self.http_request('GET', action)
        return res_data
    
    def getNewlist(self,uid):
        pageNo=0
        playlists=[]
        while(self.user_playlist(uid,pageNo) !=[]):
            playlist = self.user_playlist(uid,pageNo)
            for elem in playlist:
                playlists.append(elem)
            pageNo = pageNo+1
            print playlists
        items = [] 
        for item in playlists:  
            items.append([item['enworkid'],item['songname']]) 
        self.List = items
  
    # 通过用户主页编号，获取userid  
    def GetUserid(self,uid):  
        myUrl = "http://changba.com/u/" + uid
        user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36"\
                    " (KHTML, like Gecko) Chrome/33.0.1750.152 Safari/537.36" 
        headers = { 'User-Agent' : user_agent } 
        req = urllib2.Request(myUrl, headers = headers) 
        myResponse = urllib2.urlopen(req)
        myPage = myResponse.read()  
        #encode的作用是将unicode编码转换成其他编码的字符串  
        #decode的作用是将其他编码的字符串转换成unicode编码  
        unicodePage = myPage.decode("utf-8")  
  
        # 找出所有href以'/s/'开头，且其内部有div class="userPage-work-detail"的标记  
        #re.S是任意匹配模式，也就是.可以匹配换行符S  userid = '(\d+)';
        myItems = re.findall("var userid = '(\d+)'",unicodePage,re.S)  
        for Item in myItems:           
            if(Item!=None):
                return Item
            else:
                return
          
    #根据mp3url查找MP3链接并下载     
    def Download(self,mp3url,mp3nm,uid):
        rstr = r"[\/\\\:\*\?\"\<\>\|]"  # '/\:*?"<>|'
        mp3renm = re.sub(rstr, "", mp3nm) #剔除非法的文件名字符串
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
        #re.S是任意匹配模式，也就是.可以匹配换行符S '[^a="]http://(\w+).mp3  http://.*?.changba.com/.*?d+.mp3
        myItems = re.search("http://(\S+).changba.com/(\S+)(\d+).mp3",unicodePage)
        savePath = os.path.expanduser(r'~/Downloads/%s' % uid)#下载路径在用户文件夹下
        if not os.path.isdir(savePath):
            os.makedirs(savePath)
        if(myItems!=None):
            downurl=myItems.group()
            try:
                f = urllib2.urlopen(downurl) 
                data = f.read() 
                with open(savePath+"/"+ mp3renm+".mp3",'w+b') as code:     
                    code.write(data)
                print mp3renm, "下载成功"
                code.close()
            except IOError,e:
                print("open exception: %s: %s\n" %(e.errno, e.strerror)) 
                print mp3renm,"下载失败"
        else:
            print "未找到MP3文件" 
          
    def Start(self):  
        import thread  
        print u'正在下载请稍候......'  
        userid=self.GetUserid(self.uid)
        self.getNewlist(userid)  
        count = 1  
        for item in self.List:
            print u'正在下载第',count,"首歌"
            # 新建一个线程在后台下载歌曲
#             thread.start_new_thread(self.Download(item[0], item[1],self.uid),())  
            self.Download(item[0], item[1],self.uid)
            #print item
            count+=1

  
  
  
#----------- 程序的入口处 -----------  
print u""" 
--------------------------------------- 
   程序：唱吧爬虫 
   版本：0.1 
   作者：zhm 
   日期：2016-07-02 
   语言：Python 2.7 
   操作：输入用户主页编号并按下回车 
   说明：用户用户主页编号是指用户主页链接尾部的一串数字
   功能：依次下载该用户唱的歌曲 
--------------------------------------- 
"""
  
print u'请输入用户主页编号并按下回车：'  
userid=raw_input('')  
myModel = Spider_Model(userid)  
myModel.Start()  
