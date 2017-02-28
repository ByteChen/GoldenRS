# -*- coding:utf-8 -*-

import requests
import os
import time
import random
from lxml import etree
import urllib2
import re
import urllib
import cookielib
import sys
reload(sys)
sys.setdefaultencoding( "utf-8" )

def getTitleUrl(html):
    selector = etree.HTML(html)
    list = selector.xpath('//h3[@class="xs3"]')
    title_url = []
    for each in list:
        titlereg = each.xpath('a')[0]
        title = titlereg.xpath('string(.)')#[0]
        # print title
        url = each.xpath('a/@href')[0]
        url = 'http://rs.xidian.edu.cn/' + url
        title_url.append([title,url])
    return title_url

# def checkLog(list,logs):
#     new = []
#     for each in list:
#         flag = 0
#         for eachlog in logs:
#             if eachlog.find(each[0]) != -1 :
#                 flag = 1
#                 break
#         if flag == 0:
#             new.append(each)
#         else :
#             break
#     return new

def checkLog(list,logs):      # filter out the thread that had been replied
    new = []
    for each in list:
        if logs.find(each[0]) != -1:
            break
        new.append(each)
    return new

def isTradeTopic(url):
    html = urllib2.urlopen(url).read()
    selector = etree.HTML(html)
    topictype = selector.xpath('//*[@id="pt"]')[0]
    type = topictype.xpath('string(.)')
    # print type
    # log1 = '普通交易区'
    # log2 = '广告代理区'
    # if (log1.find(type) != -1) | (log2.find(type) != -1) :
    #     print 'found!!!!'
    #     return (False, html)
    if type.find('校园交易') != -1 :
        # print 'found!!!!'
        return (True, html)
    return (False, html)

def getParameter(html):
    # html = urllib2.urlopen(url).read()
    selector = etree.HTML(html)
    posttime = selector.xpath('//input[@id="posttime"]/@value')[0]
    formhash = selector.xpath('//*[@id="scbar_form"]/input[2]/@value')[0]
    # print 'formhash:' + formhash
    ids = selector.xpath('//*[@id="wp"]/script[1]/text()')[0]
    # print ids
    id = re.findall(r"\d+",ids)
    # print id
    fid = id [0]
    tid = id [1]
    # print fid,tid
    return (posttime,formhash,fid,tid)

def getGold_Point():
    html = urllib2.urlopen('http://rs.xidian.edu.cn/home.php?mod=spacecp&ac=credit').read()
    selector = etree.HTML(html)
    gold = selector.xpath('//*[@id="ct"]/div[1]/div/ul[2]/li[1]/text()')[0].replace('  &nbsp; ','')
    point = selector.xpath('//*[@id="ct"]/div[1]/div/ul[2]/li[8]/text()')[0].replace(' ','')
    return (int(gold), int(point))

if __name__ == "__main__":
    # 处理post请求的url
    posturl = 'http://rs.xidian.edu.cn/member.php?mod=logging&action=login&loginsubmit=yes&infloat=yes&lssubmit=yes&inajax=1'

    #设置一个cookie处理器，它负责从服务器下载cookie到本地，并且在发送请求时带上本地的cookie
    cj = cookielib.LWPCookieJar()
    cookie_support = urllib2.HTTPCookieProcessor(cj)
    opener = urllib2.build_opener(cookie_support, urllib2.HTTPHandler)
    urllib2.install_opener(opener)

    #构造header，一般header至少要包含一下两项。
    headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.11 Safari/537.36',
              'Referer' : 'http://rs.xidian.edu.cn/search.php?mod=forum&searchid=1677&orderby=dateline&ascdesc=desc&searchsubmit=yes&kw=%E9%87%91%E5%B8%81'}

    if os.path.exists('log.txt') != True:
        log = open('log.txt','w')
        log.close()

    setting = open('setting.txt')
    username = setting.readline().replace('\n','').decode('gbk')
    password = setting.readline().replace('\n','').decode('gbk')
    setting.close()

    # 构造postdata用于传输登陆
    postData = {
                'username':username,
                'cookietime':'2592000',
                'password':password,
                'quickforward':'yes',
                'handlekey':'ls'
               }
    #需要给Post数据编码
    postData = urllib.urlencode(postData)

    while True:
        try:
            #通过urllib2提供的request方法来向指定Url发送我们构造的数据，并完成登录过程
            request = urllib2.Request(posturl, postData, headers)
            response = urllib2.urlopen(request)
            # 获取搜索页面formhash
            searchpage = urllib2.urlopen('http://rs.xidian.edu.cn/search.php?mod=forum&adv=yes').read()
            # print searchpage
            selector = etree.HTML(searchpage)
            search_formhash = selector.xpath('//*[@id="ct"]/div/div/div[2]/form/input/@value')[0]
            # print search_formhash
            search_postdata = {
                'formhash':search_formhash,
                'srchtxt':'金币',
                'seltableid':'0',
                'srchuname':'',
                'srchfilter':'all',
                'srchfrom':'86400',
                'before':'',
                'orderby':'dateline',
                'ascdesc':'desc',
                'srchfid[]':'all',
                'searchsubmit':'yes'
            }
            # 使用post命令提交关键词经行搜索
            search_postdata = urllib.urlencode(search_postdata)
            search_posturl = 'http://rs.xidian.edu.cn/search.php?mod=forum'
            search_request = urllib2.Request(search_posturl, search_postdata, headers)
            search_response = urllib2.urlopen(search_request).read()
            searchresult = search_response
            title_url = getTitleUrl(searchresult)
            # print searchresult

            log = open('log.txt')
            logs = log.readline()
            # print logs
            log.close()

            new = checkLog(title_url,logs)
            # print len(new)

            if len(new)!=0:
                former_gold,former_point = getGold_Point()

            for i,each in enumerate(new):
                try:
                    (flag, html) = isTradeTopic(each[1])
                    # print flag
                    if flag:
                        continue
                    else:
                        # posttime,formhash,fid,tid = getParameter(each[1])
                        posttime, formhash, fid, tid = getParameter(html)
                        # print each[1]
                        # print 'posttime is:' + posttime
                        requestURL = 'http://rs.xidian.edu.cn/forum.php?mod=post&action=reply&fid=%s&tid=%s&extra=&replysubmit=yes&infloat=yes&handlekey=fastpost&inajax=1' % (fid, tid )
                        # print requestURL
                        reply_list = ['楼主好人~~~','我来了~~~~{:8_166:}','帮忙顶帖~~','多谢楼主金币！{:11_640:}','路过帮顶~~~{:16_998:}','顶帖拿金币','我来支持一下','帮顶帮顶~~~~~~~~','还有金币不~~{:16_1013:}','帮顶帮顶~~{:13_730:}','帮忙顶一下呢{:13_730:}']
                        reply_message = random.choice(reply_list)
                        reply_postdata = {
                            'message':reply_message,
                            'posttime':posttime,
                            'formhash':formhash,
                            'usesig':'1',
                            'subject':''
                        }
                        reply_header = {
                            'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.11 Safari/537.36',
                            'Referer' :  each[1]
                        }
                        reply_postdata = urllib.urlencode(reply_postdata)
                        reply_request = urllib2.Request(requestURL, reply_postdata, reply_header)
                        reply_response = urllib2.urlopen(reply_request).read()
                        # print reply_response
                        if i>12:              #防止一次回帖过多，引起管理员注意
                            break
                        time.sleep(random.randint(50,110))
                except:
                    pass

            if len(new)!=0:
                current_gold,current_point = getGold_Point()
                record = open('record.txt','a+')
                to_write = '恭喜你，本轮回帖：' + str(len(new)) + ' 获得金币：' + str(current_gold - former_gold) + ' 积分：' + str(current_point - former_point) + '\n'
                record.write(to_write)
                record.close()

            if len(new) != 0:
                log = open('log.txt','w')
                log.write(new[0][0])
                log.close()

            time.sleep(10*60+random.randint(0,300))  #15分钟左右扫描一次
        except:
            pass
