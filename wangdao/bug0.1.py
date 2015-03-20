__author__ = 'liruicheng'
# -*- coding: utf-8 -*-

import urllib2
import thread
import re
import time
import string


class PostSpider:

    def __init__(self):

        self.page = 1
        self.pages = []
        self.enable = False

    def getAllPostPage(self, forum, page):

        path = re.split(r'thread-(.+?)-', forum)

        url = "http://www.cskaoyan.com/" + "thread-" + path[1] + "-" + page + "-1.html"
        user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
        headers = { 'User-Agent' : user_agent }
        req = urllib2.Request(url, headers = headers)

        postPage = urllib2.urlopen(req).read()
        gbkPostPage = postPage.decode('gbk')

        post_re = re.compile(r'<div class="postinfo">.+?<a target=.+?>(.+?)</a>.+?<em id=".+?>(.+?)</em>.+?<td class="t_msgfont" id=".+?>(.+?)</td>', re.DOTALL)
        #context_re = re.compile(r'\t|\n|<a.*?>|<img.*?>|<strong.*?>|<br.*?>|<fontsize.*?>|</a>|</font>| |</strong>|&nbsp;')
        #context_space_re = re.compile(r'<i>|</i>')

        postItems = post_re.findall(gbkPostPage)

        return postItems


    def showPostPage(self, nowPostPage, postPage, path):

        context_re = re.compile(r'\t|\n|<a.*?>|<img.*?>|<strong.*?>|<br.*?>|<fontsize.*?>|<scripttype.*?>|<divclass.*?>|<emonclick.*?>|</script>|<ol>|</ol>|</div>|<li>|</a>|</font>|</em>| |</strong>|&nbsp;')
        context_space_re = re.compile(r'<i>|</i>')

        print u'        日期     发帖人        帖子'
        for items in nowPostPage:
            cont = context_re.sub("", items[2])
            cont = context_space_re.sub(" ", cont)

            print '第%d页' % postPage , items[1], items[0]
            print cont

        myInput = raw_input('保存到文件(y/n)? 退出(quit)：')
        if myInput == "quit":
            self.enable = False
        if myInput == "y":
            file = open(path, 'wb')
            for items in nowPostPage:
                cont = context_re.sub("", items[2])
                cont = context_space_re.sub(" ", cont)
                file.writelines('作者: %s' % items[0].decode('utf'), items[1]).decode('utf')
                file.writelines(cont.decode('utf'))
            file.close()
            self.enable = False

        del self.pages[0]

    def loadPostPage(self, forum):

        while self.enable:

            if len(self.pages) < 2:
                try:
                    postPage = self.getAllPostPage(forum, str(self.page))
                    self.page += 1
                    self.pages.append(postPage)
                except:
                    print '读取失败'
            else:
                time.sleep(1)

    def startPostPage(self, forum):

        self.enable = True
        page = self.page

        print u'正在读取post...'

        threadTuple = (forum, )
        thread.start_new_thread(self.loadPostPage, threadTuple)

        while self.enable:

            if self.pages:
                nowPage = self.pages[0]
                self.showPostPage(nowPage, page, forum)
                page += 1



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

        title_re = re.compile(r'<h1 style="">(.+?)</h1>')
        page_re = re.compile(r'<th class="subject (?:new|common)">.+?<a href="(.*?)(?:".*?|")>(.+?)</a>.+?<td class="author">.+?<a href=".+?\>(.+?)</a>.+?<em>(.+?)</em>', re.DOTALL)

        title = title_re.findall(gbkForumPage)
        items = page_re.findall(gbkForumPage)

        return items

    def showForum(self, nowForumPage, page):

        index = 1
        print u'        日期     发帖人        主题'
        for items in nowForumPage:
            print '%d: ' % index, '第%d页' % page , items[3], items[2], items[1].encode('utf')
            index += 1

        flag = 1

        while flag:

            myInput = raw_input('请选择需要打开的帖子(序号), 退出(quit), 继续(任意其他键):')
            if myInput == "quit":

                flag = 0
                self.enable = False

            if myInput.isdigit():

                postPage = PostSpider()
                postPage.startPostPage(nowForumPage[int(myInput)][0])
                index = 1
                print u'        日期     发帖人        主题'
                for items in nowForumPage:
                    print '%d: ' % index, '第%d页' % page , items[3], items[2], items[1].encode('utf')
                    index += 1
            else:
                del self.pages[0]
                flag = 0




    def loadForumPage(self, forum):

        while self.enable:

            if len(self.pages) < 2:
                try:
                    forumPage = self.getForumPage(forum, str(self.page))
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
                self.showForum(nowPage,page)
                page += 1




#程序入口
print """
----------------------
83 : 中国科学与技术大学
thread-246522-1-1.html


---------------------
"""

forum = str(raw_input('输入板块编号:'))
myModel = ForumSpider()
myModel.startSpider(forum)
