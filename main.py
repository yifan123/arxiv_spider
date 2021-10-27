# -*- coding: utf-8 -*-

import requests
import re
import time
import pandas as pd
from bs4 import BeautifulSoup
import pymysql
from collections import Counter
import os
import random

import smtplib
from smtplib import SMTP
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header


def get_one_page(url):
    send_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36",
        "Connection": "keep-alive",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.8"}
    response = requests.get(url,headers=send_headers)
    print(response.status_code) 
    while response.status_code == 403:
        time.sleep(500 + random.uniform(0, 500))
        response = requests.get(url,headers=send_headers)
        print(response.status_code)
    print(response.status_code)
    if response.status_code == 200:
        return response.text

    return None


def send_email(title, content):

    #发送者邮箱
    sender = '1234567@qq.com'
    #发送者的登陆用户名和密码
    user = '1234567@qq.com'
    #邮箱需要开启pop3转发，qq邮箱一般会生成一段token
    password = 'iloveofflinerl'
    #发送者邮箱的SMTP服务器地址
    smtpserver = 'smtp.qq.com'
    #接收者的邮箱地址
    receiver = '1234567@qq.com' #receiver 可以是一个list

    msg = MIMEMultipart('alternative')  

    part1 = MIMEText(content, 'plain', 'utf-8')  
    #html = open('subject_file.html','r')
    #part2 = MIMEText(html.read(), 'html')

    msg.attach(part1)  
    #msg.attach(part2)

    #发送邮箱地址
    msg['From'] = sender
    #收件箱地址
    msg['To'] = receiver
    #主题
    msg['Subject'] = title

    smtp = smtplib.SMTP(smtpserver) #实例化SMTP对象
    smtp.connect(smtpserver, 587) #（缺省）默认端口是25 也可以根据服务器进行设定
    smtp.ehlo()
    smtp.starttls()
    smtp.ehlo()
    smtp.login(user, password) #登陆smtp服务器
    smtp.sendmail(sender, receiver, msg.as_string()) #发送邮件 ，这里有三个参数
    '''
    login()方法用来登录SMTP服务器，sendmail()方法就是发邮件，由于可以一次发给多个人，所以传入一个list，邮件正文
    是一个str，as_string()把MIMEText对象变成str。
    '''
    smtp.quit()


def main():

    # 创建必要的目录
    dir_list=['daily','sub_cnt','selected_key_word','selected_author','report']
    for dir in dir_list:
        if not os.path.exists('./'+dir):
            os.makedirs('./'+dir)
    domains=['cs.CV','cs.AI','stat.ML','cs.LG','cs.RO']
    list_subject_split = []
    list_ids = []
    list_title = []
    list_authors = []
    list_subjects = []
    for domain in domains:
        url = 'https://arxiv.org/list/'+domain+'/pastweek?show=1000'
        html = get_one_page(url)
        soup = BeautifulSoup(html, features='html.parser')
        content = soup.dl
        date = soup.find('h3')
        print(date)
        list_ids.extend(content.find_all('a', title = 'Abstract'))
        list_title.extend(content.find_all('div', class_ = 'list-title mathjax'))
        list_authors.extend(content.find_all('div', class_ = 'list-authors'))
        list_subjects.extend(content.find_all('div', class_ = 'list-subjects'))
    for subjects in list_subjects:
        subjects = subjects.text.split(': ', maxsplit=1)[1]
        subjects = subjects.replace('\n\n', '')
        subjects = subjects.replace('\n', '')
        subject_split = subjects.split('; ')
        list_subject_split.append(subject_split)

    items = []
    for i, paper in enumerate(zip(list_ids, list_title, list_authors, list_subjects, list_subject_split)):
        items.append([paper[0].text, paper[1].text, paper[2].text, paper[3].text, paper[4]])
    name = ['id', 'title', 'authors', 'subjects', 'subject_split']
    paper = pd.DataFrame(columns=name,data=items)
    paper = paper.drop_duplicates(subset='title',keep='first')
    paper.to_csv('./daily/'+time.strftime("%Y-%m-%d")+'_'+str(len(items))+'.csv')


    '''subject split'''
    subject_all = []
    for subject_split in paper['subject_split']:
        for subject in subject_split:
            subject_all.append(subject)
    subject_cnt = Counter(subject_all)
    subject_items = []
    for subject_name, times in subject_cnt.items():
        subject_items.append([subject_name, times])
    subject_items = sorted(subject_items, key=lambda subject_items: subject_items[1], reverse=True)
    name = ['name', 'times']
    subject_file = pd.DataFrame(columns=name,data=subject_items)
    subject_file.to_csv('./sub_cnt/'+time.strftime("%Y-%m-%d")+'_'+str(len(items))+'.csv')


    '''key_word selection'''
    # 我这里使用正则来做匹配
    key_words = [
        '(?i)offline.*(RL|reinforcement learning)',
        '(?i)(RL|reinforcement learning).*offline'
    ] 

    selected_papers = paper[paper['title'].str.contains(key_words[0], case=False, regex=True)]
    for key_word in key_words[1:]:
        selected_paper1 = paper[paper['title'].str.contains(key_word, case=False, regex=True)]
        selected_papers = pd.concat([selected_papers, selected_paper1], axis=0)
    selected_papers.to_csv('./selected_key_word/'+time.strftime("%Y-%m-%d")+'_'+str(len(selected_papers))+'.csv')
    
    '''author selection'''
    authors = ['Sergey Levine', 'Song Han']
    selected_papers2 = paper[paper['authors'].str.contains(authors[0], case=False)]
    for key_word in authors[1:]:
        selected_paper2 = paper[paper['authors'].str.contains(key_word, case=False)]
        selected_papers2 = pd.concat([selected_papers2, selected_paper2], axis=0)
    selected_papers2.to_csv('./selected_author/'+time.strftime("%Y-%m-%d")+'_'+str(len(selected_papers2))+'.csv')
    
    '''send email'''
    #selected_papers.to_html('email.html')
    content = 'Today arxiv has {} new papers in {} area, and {} of them is about CV, {}/{} of them contain your keywords.\n\n'.format(len(paper),domains, subject_cnt['Computer Vision and Pattern Recognition (cs.CV)'], len(selected_papers), len(selected_papers2))
    content += 'Ensure your keywords is ' + str(key_words) + '. \n\n'
    content += 'This is your paperlist.Enjoy! \n\n'
    for i, selected_paper in enumerate(zip(selected_papers['id'], selected_papers['title'], selected_papers['authors'], selected_papers['subject_split'])):
        #print(content1)
        content1, content2, content3, content4 = selected_paper
        content += '------------' + str(i+1) + '------------\n' + content1 + content2 + str(content4) + '\n'
        content1 = content1.split(':', maxsplit=1)[1]
        content += 'https://arxiv.org/abs/' + content1 + '\n\n'

    content += 'Ensure your authors is ' + str(authors) + '. \n\n'
    content += 'This is your paperlist.Enjoy! \n\n'
    for i, selected_paper2 in enumerate(zip(selected_papers2['id'], selected_papers2['title'], selected_papers2['authors'], selected_papers2['subject_split'])):

        #print(content1)
        content1, content2, content3, content4 = selected_paper2
        content += '------------' + str(i+1) + '------------\n' + content1 + content2 + str(content4) + '\n'
        content1 = content1.split(':', maxsplit=1)[1]
        content += 'https://arxiv.org/abs/' + content1 + '\n\n'


    content += 'Here is the Research Direction Distribution Report. \n\n'
    for subject_name, times in subject_items:
        content += subject_name + '   ' + str(times) +'\n'
    title = time.strftime("%Y-%m-%d") + ' you have {}+{} papers'.format(len(selected_papers), len(selected_papers2))
    send_email(title, content)
    freport = open('./report/'+title+'.txt', 'w')
    freport.write(content.encode().decode('utf-8', 'ignore'))
    freport.close()


if __name__ == '__main__':
    main()
