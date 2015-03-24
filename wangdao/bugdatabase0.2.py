__author__ = 'liruicheng'
# -*- coding: utf-8 -*-

import re
import time
import Queue
import MySQLdb
import urllib2
import threading

#----------SQL----------

db = MySQLdb.connect('localhost', 'root', 'liruicheng122*.', 'wangdao', charset = 'utf8')
cursor = db.cursor()

#----------THREAD POOL----------

class WorkManager(object):

    def __init__(self, threadNum, *forumId):

        self.workQueue = Queue.Queue()
        self.resultQueue = Queue.Queue()
        self.threads = []
        self.initThreadPool(threadNum)
        self.initWorkQueue(forumId)

    def initThreadPool(self, threadNum):

        for i in threadNum:
            self.threads.append(Work(self.workQueue, self.resultQueue))

    def initWorkQueue(self,forumId):

        self.workQueue.put(forumId)

    def checkQueue(self):

        return self.workQueue.qsize()

    def waitAllThreadComplete(self):

        for item in self.threads:
            if item.isAlive():
                item.join()



class Work(threading.Thread):

    def __init__(self, workQueue, resultQueue):

        threading.Thread.__init__(self)
        self.workQueue = workQueue
        self.resultQueue = resultQueue
        self.start()

    def run(self):

        while True:
            try:
                do, args = self.workQueue.get(block = False)
                do(args)
                self.workQueue.task_done()
            except Exception, e:
                break

#----------GET FORUMPAGE----------

class ForumSpider:

    def __init__(self):

        self.page = 1
        self.pages = []
        self.enable = False

    def getForumPage(self, forum, page):

        url = "http://www.cskaoyan.com/forum-" + forum + "-" + page + ".html"
        user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
        headers = { 'User-Agent' : user_agent }
        req = urllib2.Request(url, headers = headers)

        forumPage = urllib2.urlopen(req).read()
        gbkForumPage = forumPage.decode('gbk')

        #title_re = re.compile(r'<h1 style="">(.+?)</h1>')
        page_re = re.compile(r'<th class="subject (?:new|common)">.+?<a href="(.*?)(?:".*?|")>(.+?)</a>.+?<td class="author">.+?<a href="space-uid-(.+?).html">(.+?)</a>.+?<em>(.+?)</em>', re.DOTALL)

        #title = title_re.findall(gbkForumPage)
        items = page_re.findall(gbkForumPage)

        return items

    def loadForumPage(self, forum):

        while self.enable:
            try:
                forumPage, self.title = self.getForumPage(forum, str(self.page))
                if forumPage == []:
                    self.enable = False
                self.page += 1
                self.pages.append(forumPage)
            except:
                print '读取失败'



    def startSpider(self, forum):

        self.enable = True
        page = self.page

        print u'正在加载...'

        self.loadForumPage(forum)

        if not self.enable:
            return self.pages

#----------LOAD CONFIG----------

fConfig = open('config.txt', 'r')
forumId = []

for line in fConfig:

    forumId.append(int(line))

fConfig.close()

#----------EXECUTE----------

if __name__ == '__main__':
    main()

