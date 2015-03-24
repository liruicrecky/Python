__author__ = 'Reacky'
# -*- coding: utf-8 -*-

import urllib2
import thread
import re
import time
import MySQLdb

#--------------SQL---------------------

db = MySQLdb.connect('localhost', 'root', 'liruicheng122*.', 'wangdao', charset = 'utf8')
cursor = db.cursor()
db.select_db('wangdao')

#-------------SQL----------------------

#----------------CLASS SPIDER----------------------------
class ForumSpider:

    def __init__(self):

        self.page = 1
        self.pages = []
        self.title = ''
        self.enable = False

    def getForumPage(self, forum, page):

        url = "http://www.cskaoyan.com/forum-" + forum + "-" + page + ".html"
        user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
        headers = { 'User-Agent' : user_agent }
        req = urllib2.Request(url, headers = headers)

        forumPage = urllib2.urlopen(req).read()
        gbkForumPage = forumPage.decode('gbk')

        title_re = re.compile(r'<h1 style="">(.+?)</h1>')
        page_re = re.compile(r'<th class="subject (?:new|common)">.+?<a href="(.*?)(?:".*?|")>(.+?)</a>.+?<td class="author">.+?<a href="space-uid-(.+?).html">(.+?)</a>.+?<em>(.+?)</em>', re.DOTALL)

        title = title_re.findall(gbkForumPage)
        items = page_re.findall(gbkForumPage)

        return items, title

    def saveForumPage(self, nowForumPage, forum):

        for items in nowForumPage:

            postId = re.split(r'thread-(.+?)-', items[0])
            #--------------------SQL--------------------------------------
            sql_search = cursor.execute('SELECT POST_ID FROM `forum` WHERE `POST_ID` = ' + postId[1])
            if sql_search:
                continue

           # itmes 构造
           # items[0] = URL items[1] = TITLE items[2] = UID items[3] = AUTHOR items[4] = time
            value = [forum, postId[1], items[3], items[2], items[4], items[0], items[1]]
            cursor.execute("INSERT INTO forum (FORUM_ID, POST_ID, AUTHOR, UID, DATE, URL, TITLE) VALUES(%s ,%s ,%s, %s, %s, %s, %s)", value)

        db.commit()

        del self.pages[0]




    def loadForumPage(self, forum):

        while self.enable:

            if len(self.pages) < 5:
                try:
                    forumPage, self.title = self.getForumPage(forum, str(self.page))
                    if forumPage == []:
                        self.enable = False
                    self.page += 1
                    self.pages.append(forumPage)
                except:
                    print '读取失败'
            else:
                time.sleep(1)


    def startSpider(self, forum):

        self.enable = True
        page = self.page

        print u'正在加载...'

        threadTuple = (forum, )
        thread.start_new_thread(self.loadForumPage, threadTuple)

        while self.enable:

            if self.pages:
                nowPage = self.pages[0]
                self.saveForumPage(nowPage,forum)
                page += 1




#程序入口
print """
----------------------
83 : 中国科学与技术大学
thread-246522-1-1.html


---------------------
"""

#handle confing file

fconfig = open('config.txt', 'r')
forum_id = []

for line in fconfig:
    if line:
        forum_id.append(int(line))

fconfig.close()

for id in forum_id:
    print id
    myModel = ForumSpider()
    myModel.startSpider(str(id))

cursor.close()
db.close()

