"""
Name: Spider_On_Zhihu_Platform
Author: ZhanshuoBai
Date: 2024-11-15
Version: Release_1.0.1
Description:
    You can import this module to get data on zhihu platform.
    What you can get?
        1. The source code of web page about search list page.
        2. The source code of web page about each page of search list items.
        3. The formal content about search list.
        4. The formal content about search list items.
    Useful features?
        1. You can set your e-mail and when the code finished, you will receive a message.
Attention:
    1. Please pay attention to reptile ethics in your use, legal use of this module,
    the use of this module caused by all violations of the law, and the author of the
    module has nothing to do with his own.
    2. As this module contains sensitive information about the author, distribution
    of this module without the author's authorization is prohibited.
    3. This module is for Zhejiang University of Technology data analysis python homework only.
Submit Issue:
    https://github.com/XiaoBaiBZS/Spider_On_Zhihu_Platform/issues/new
Demo Code:
    # Main Information
    # Must be instantiated one by one, if the object is not instantiated,
    # the function of the object can not be called properly, member variables can not be saved properly
    # You only need to give following information to let code work.
    Save_Info = Save_Info(save_path="./", file_type_info=File_Type_Info(search_list_page_source=File_Type.html,search_list_page_item_list=File_Type.json,search_list_page_item_page_source=File_Type.html,search_list_page_item_content=File_Type.json))
    Spider_Methods = Spider_Methods(list_page_scroll_by=[0, 5000],list_page_scroll_times=0,item_page_scroll_by=[0,5000],item_page_scroll_times=0,save_info=Save_Info)
    Zhihu_Spider_Tool_Info = Zhihu_Spider_Tool_Info(topic="华为",browser_type=Browser_Type.Edge,url="https://www.zhihu.com",spider_methods=Spider_Methods)
    Zhihu_Spider_Tool = Zhihu_Spider_Tool(Zhihu_Spider_Tool_Info = Zhihu_Spider_Tool_Info)
    user_email = "1298589907"
    # Main Methods
    Zhihu_Spider_Tool.new_browser()
    if Zhihu_Spider_Tool.wait_login():
        if Zhihu_Spider_Tool.search_topic():
            Zhihu_Spider_Tool.get_search_topic_list_page_source()
            Zhihu_Spider_Tool.Zhihu_Spider_Tool_Info.spider_methods.save_info.create_file_path()
            Zhihu_Spider_Tool.Zhihu_Spider_Tool_Info.spider_methods.save_info.save_search_list_page_source()
            Zhihu_Spider_Tool.analyze_search_topic_list()
            Zhihu_Spider_Tool.Zhihu_Spider_Tool_Info.spider_methods.save_info.save_search_list_page_item_list()
            Zhihu_Spider_Tool.get_and_write_search_list_item_content_page_source()
            Zhihu_Spider_Tool.analyze_and_write_search_topic_list_item()
            Tool.finish_e_mail(user_email)

"""

import json
import re
import string
import time
import os
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import smtplib
from email.mime.text import MIMEText
from email.header import Header

# Browser type, e.g. Microsoft Edge, Google Chrome, Firefox, etc.
class Browser_Type:
    Firefox = "Firefox"
    Chrome = "Chrome"
    Ie = "Ie"
    Edge = "Edge"
    Safari = "Safari"

# Browser information configuration, basic browser options, types, links
class Browser:
    # Default options, no additional settings or changes required
    options = Options()
    type = Browser_Type.Edge
    url = ""

    # Init browser
    def __init__(self, Browser_Type: Browser_Type, url: str):
        self.type = Browser_Type
        self.url = url
        self.driver = None

    # Set Chrome options
    def set_options(self):
        self.options = Options()
        self.options.add_experimental_option('excludeSwitches', ['enable-automation'])
        self.options.add_experimental_option('useAutomationExtension', False)

    # Add a method to execute a script to modify the navigator.webdriver property
    def set_navigator_webdriver(self):
        self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                        Object.defineProperty(navigator, 'webdriver', {
                            get: () => false
                        });
                    """
        })

    # Create a new broswer
    def new_browser(self):
        self.set_options()
        # Initialise the browser driver
        if self.type == Browser_Type.Firefox:
            self.driver = webdriver.Firefox(options=self.options)
        elif self.type == Browser_Type.Chrome:
            self.driver = webdriver.Chrome(options=self.options)
        elif self.type == Browser_Type.Ie:
            self.driver = webdriver.Ie(options=self.options)
        elif self.type == Browser_Type.Edge:
            self.driver = webdriver.Edge(options=self.options)
        elif self.type == Browser_Type.Safari:
            self.driver = webdriver.Safari(options=self.options)
        # Set navigator.webdriver
        self.set_navigator_webdriver()
        # Open website
        self.driver.get(self.url)
        # Return browser (You can not use variant receive this value.)
        return self.driver

# Sub-items of the searched listings page
class Search_List_Page_Item:
    # Title of sub-item
    title=""
    # Number of favourable views
    agree_num = 0
    # Volume of discussion
    discuss_num = 0
    # Release time
    release_datetime = ""
    # Links to jump to when clicked
    url = ""

    def __init__(self, title, agree_num,discuss_num, release_datetime, url):
        self.title = title
        self.agree_num = agree_num
        self.release_datetime = release_datetime
        self.url = url
        self.discuss_num = discuss_num

    # Show sub-items of the searched listings page (Debug)
    def print(self):
        print(self.title, self.agree_num, self.discuss_num, self.release_datetime, self.url)

# List subitem detail page information
class Search_List_Page_Item_Content:
    # Content of user responses
    content=""
    # Number in favour of this view
    agree_num = 0
    # Volume of discussion
    discuss_num = 0
    # Release time
    release_datetime = ""

    def __init__(self, content,agree_num,discuss_num, release_datetime):
        self.content = content
        self.agree_num = agree_num
        self.discuss_num = discuss_num
        self.release_datetime = release_datetime

    # Show sub-items of the searched listings page (Debug)
    def print(self):
        print(self.content, self.agree_num, self.discuss_num, self.release_datetime)

# All data you get on zhihu platform
class Zhihu_Spider_Data:
    # Search list page source code
    search_list_page_source = ""
    # Sub-items of the searched listings page
    search_list_page_item_list = []
    # List subitem detail page information
    search_list_page_item_content_list = []
    # Filenames of all documents
    search_list_item_page_source_file_name = []

# Type of file saved, e.g. txt text file, html hypertext markup language file, etc.
class File_Type:
    txt = "txt"
    html = "html"
    csv = "csv"
    json = "json"

# Type information of file saved, e.g. txt text file, html hypertext markup language file, etc.
class File_Type_Info:
    search_list_page_source = File_Type.html
    search_list_page_item_list = File_Type.json
    search_list_page_item_page_source = File_Type.html
    search_list_page_item_content = File_Type.json


    def __init__(self, search_list_page_source=File_Type.html, search_list_page_item_list=File_Type.json,search_list_page_item_page_source=File_Type.html,search_list_page_item_content=File_Type.json):
        self.search_list_page_source = search_list_page_source
        self.search_list_page_item_list = search_list_page_item_list
        self.search_list_page_item_page_source = search_list_page_item_page_source
        self.search_list_page_item_content = search_list_page_item_content

# Save files
class Save_Info:
    # Path where the file is kept, e.g. './' or 'D:\Documents\Python Project\pythonProject'  etc.
    save_path = "./"
    # Name of folder created
    file_path_name = ""
    # Type of file saved, e.g. txt text file, html hypertext markup language file, etc.
    file_type_info = File_Type_Info
    # Data obtained
    data = Zhihu_Spider_Data

    def __init__(self,  save_path="./", file_type_info=File_Type_Info):
        self.file_type_info = file_type_info
        self.save_path = save_path

    # Create folders to hold files
    def create_file_path(self):
        try:
            os.chdir(self.save_path)
        except:
            return False
        else:
            path = "SpiderData_On_Zhihu_Platform_" + str(time.strftime('%Y%m%d%H%M%S', time.localtime()))
            os.makedirs(path)
            self.file_path_name = path
            return path

    # Save the web page source code for the search listing page
    def save_search_list_page_source(self):
        try:
            with open(self.save_path + self.file_path_name + "/search_list_page_source." + self.file_type_info.search_list_page_source,'w',encoding='utf-8') as f:
                f.write(self.data.search_list_page_source)
        except:
            return False
        else:
            return True

    # Save the web page source code for the items of search listing page
    def save_search_list_item_page_source(self):
        try:
            with open(self.save_path + self.file_path_name + "/search_list_item_page_source." + self.file_type_info.search_list_page_source,'w',encoding='utf-8') as f:
                f.write(self.data.search_list_page_source)
        except:
            return False
        else:
            return True

    # Save the content for the items of search listing page
    def save_search_list_page_item_list(self):
        item_dicts = [item.__dict__ for item in self.data.search_list_page_item_list]
        json_str = json.dumps(item_dicts, indent=4, ensure_ascii=False)
        print(json_str)
        try:
            with open(self.save_path + self.file_path_name + "/search_list_page_item_list." + self.file_type_info.search_list_page_item_list,'a+',encoding='utf-8') as f:
                f.write(json_str)
        except:
            return False
        else:
            return True

    # Save the file for all the name of files
    def save_search_list_item_page_source_file_name(self):
        json_data = json.dumps(self.data.search_list_item_page_source_file_name, indent=4, ensure_ascii=False)
        with open(self.save_path+self.file_path_name+"/search_list_item_page_source_file_name.json", 'w', encoding='utf-8') as file:
            file.write(json_data)

# Tool
class Tool:
    def replace_special_characters(input_string, replacement_char):
        special_characters = string.punctuation + ' '
        trans_table = str.maketrans(special_characters, replacement_char * len(special_characters))
        result_string = input_string.translate(trans_table)
        return result_string

    def finish_e_mail(self,msg_to):
        E_Mail(subject="Your crawler has finished running",
               body="This email is sent automatically by the system, thank you for using it.\n\nZhanshuo Bai",
               msg_to=msg_to).send_mail()

# E_Mail
class E_Mail:
    subject = '邮件主题'
    body = '邮件正文'
    smtp_server = 'smtp.qq.com'
    smtp_port = 587
    sender_email = '1298589907@qq.com'

    password = 'Please write your owns.'
    def __init__(self,subject, body, msg_to):
        self.subject = subject
        self.body = body
        self.msg = MIMEText(body, 'plain', 'utf-8')
        self.msg['Subject'] = Header(subject, 'utf-8')
        self.msg['From'] = '1298589907@qq.com'
        self.msg['To'] = msg_to

    def send_mail(self):
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.password)
                server.sendmail(self.sender_email, [self.msg['To']], self.msg.as_string())
        except:
            pass

# Crawl method for setting the amount of data to crawl
class Spider_Methods:
    # Single screen movement distance, unit: pixel,
    # Such as: [0,500] for the upward slide 500 pixels, the same can be set to the left and right slide, but this project left and right slide meaningless
    # Lazy loading by changing the movement distance to achieve more data on the page, but too much data may cause the crawl time times rise and page sliding lag
    list_page_scroll_by = [0, 5000]
    list_page_scroll_times = 5
    item_page_scroll_by = [0, 5000]
    item_page_scroll_times = 10
    # Save files
    save_info = Save_Info

    def __init__(self, list_page_scroll_by=[0, 5000], list_page_scroll_times=5,item_page_scroll_by=[0,5000],item_page_scroll_times=10,save_info=Save_Info):
        self.list_page_scroll_by = list_page_scroll_by
        self.list_page_scroll_times = list_page_scroll_times
        self.item_page_scroll_by = item_page_scroll_by
        self.item_page_scroll_times = item_page_scroll_times
        self.save_info = Save_Info

# Main information
class Zhihu_Spider_Tool_Info:
    # Open the link
    # This project is Zhihu, when using this browser mode to open the web page, Zhihu must be logged in, so whether the link has the signin parameter is irrelevant
    url = 'https://www.zhihu.com/signin?next=%2F'
    # The topic code will search
    topic = ""
    # Browser information
    browser = Browser(Browser_Type.Firefox, url)
    spider_methods = Spider_Methods

    def __init__(self, url: str, topic: str, browser_type: Browser_Type, spider_methods: Spider_Methods):
        self.url = url
        self.topic = topic
        self.browser = Browser(browser_type, url)
        self.spider_methods = Spider_Methods

# Main
class Zhihu_Spider_Tool:
    # Main information
    Zhihu_Spider_Tool_Info = Zhihu_Spider_Tool_Info

    def __init__(self, Zhihu_Spider_Tool_Info: Zhihu_Spider_Tool_Info):
        self.Zhihu_Spider_Tool_Info = Zhihu_Spider_Tool_Info

    # Must
    def new_browser(self):
        self.Zhihu_Spider_Tool_Info.browser.new_browser()

    def wait_login(self):
        driver = self.Zhihu_Spider_Tool_Info.browser.driver
        # Wait for the search box whose id is Popover1-toggle visible, timeout 200 seconds
        try:
            element = WebDriverWait(driver, 200, ).until(
                EC.visibility_of_element_located((By.ID, "Popover1-toggle"))
            )
        except:
            # Timeout and return false
            return False
        else:
            # Login successfully
            return True

    def search_topic(self):
        driver = self.Zhihu_Spider_Tool_Info.browser.driver
        time.sleep(1)
        # Find input box
        inputTag = driver.find_element(By.ID, "Popover1-toggle")
        # Input topic
        inputTag.send_keys(self.Zhihu_Spider_Tool_Info.topic)
        # Find search button
        try:
            element = WebDriverWait(driver, 200, ).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, '[aria-label="搜索"]'))
            )
        except:
            # Timeout and return false
            return False
        else:
            # Search successfully
            ele = driver.find_element(By.CSS_SELECTOR, '[aria-label="搜索"]')
            ele.click()
            return True

    def get_search_topic_list_page_source(self):
        driver = self.Zhihu_Spider_Tool_Info.browser.driver
        scroll_by = self.Zhihu_Spider_Tool_Info.spider_methods.list_page_scroll_by
        scroll_times = self.Zhihu_Spider_Tool_Info.spider_methods.list_page_scroll_times
        time.sleep(5)
        i = 0
        while i < scroll_times:
            js = "window.scrollBy(" + str(scroll_by[0]) + "," + str(scroll_by[1]) + ")"
            driver.execute_script(js)
            time.sleep(2)
            i = i + 1
        time.sleep(3)
        page_source = driver.page_source.replace(u'\u200b', '')
        # page_source = page_source.encode("utf-8")

        self.Zhihu_Spider_Tool_Info.spider_methods.save_info.data.search_list_page_source = page_source
        return page_source

    def analyze_search_topic_list(self):
        driver = self.Zhihu_Spider_Tool_Info.browser.driver
        search_list_page_source = self.Zhihu_Spider_Tool_Info.spider_methods.save_info.data.search_list_page_source
        soup = BeautifulSoup(search_list_page_source, 'lxml')  # 创建 beautifulsoup 对象
        div = soup.find_all('div', class_='List-item')

        soup = BeautifulSoup(search_list_page_source, "lxml")  # 创建 beautifulsoup 对象
        div_list_item = soup.find_all('div', class_='List-item')
        for i in div_list_item:
            if (i.find('div', class_='HotLanding-contentListWithoutRelated')):
                continue
            elif (i.find('h2', class_='ContentItem-title')):
                h2_contentItem_title = i.find('h2', class_='ContentItem-title')
                title = h2_contentItem_title.find('span',class_="Highlight").text
                btn = i.find_all('button')
                href = h2_contentItem_title.find('a')['href']
                if (len(btn) == 4):
                    pattern = r'赞同\s+(\d+(\.\d+)?)'
                    match = re.search(pattern, str(btn[1]).replace('万', '0000'))
                    if match:
                        agree_num = eval(match.group(1))
                        if type(agree_num) != int:
                            agree_num = agree_num*10000
                    else:
                        agree_num = 0
                    pattern = r'(\d+)\s*条评论'
                    match = re.search(pattern, str(btn[3]).replace(',', ''))

                    if match:
                        discuss_num = eval(match.group(1))
                    else:
                        discuss_num = 0
                    release_datetime = i.find('span', class_='ContentItem-action SearchItem-time').text.strip()
                    # Search_List_Page_Item(title=title, agree_num = agree_num,discuss_num = discuss_num, release_datetime=release_datetime, url=href).print()
                    self.Zhihu_Spider_Tool_Info.spider_methods.save_info.data.search_list_page_item_list.append(Search_List_Page_Item(title=title, agree_num = agree_num,discuss_num = discuss_num, release_datetime=release_datetime, url=href))

    def get_and_write_search_list_item_content_page_source(self):
        driver = self.Zhihu_Spider_Tool_Info.browser.driver
        for item in self.Zhihu_Spider_Tool_Info.spider_methods.save_info.data.search_list_page_item_list:
            print(item.url)
            if "zhuanlan" in item.url:
                continue
            else:
                url = "https://www.zhihu.com"+item.url.rpartition("/answer/")[0]
            driver.get(url)
            time.sleep(1)
            scroll_by = self.Zhihu_Spider_Tool_Info.spider_methods.item_page_scroll_by
            scroll_times = self.Zhihu_Spider_Tool_Info.spider_methods.item_page_scroll_times
            time.sleep(1)
            i = 0
            while i < scroll_times:
                js = "window.scrollBy(" + str(scroll_by[0]) + "," + str(scroll_by[1]) + ")"
                driver.execute_script(js)
                time.sleep(2)
                i = i + 1
            time.sleep(3)
            page_source = driver.page_source.replace(u'\u200b', '')
            self.Zhihu_Spider_Tool_Info.spider_methods.save_info.data.search_list_item_page_source_file_name.append("search_list_item_page_source_"+Tool.replace_special_characters(item.title, '_')+"."+self.Zhihu_Spider_Tool_Info.spider_methods.save_info.file_type_info.search_list_page_item_page_source)
            with open(self.Zhihu_Spider_Tool_Info.spider_methods.save_info.save_path + self.Zhihu_Spider_Tool_Info.spider_methods.save_info.file_path_name + "/search_list_item_page_source_"+Tool.replace_special_characters(item.title, '_')+"."+self.Zhihu_Spider_Tool_Info.spider_methods.save_info.file_type_info.search_list_page_item_page_source,'w', encoding='utf-8') as f:
                f.write(page_source)
        self.Zhihu_Spider_Tool_Info.spider_methods.save_info.save_search_list_item_page_source_file_name()

    def analyze_and_write_search_topic_list_item(self):
        file_name_list = self.Zhihu_Spider_Tool_Info.spider_methods.save_info.data.search_list_item_page_source_file_name
        save_path = self.Zhihu_Spider_Tool_Info.spider_methods.save_info.save_path
        file_path_name = self.Zhihu_Spider_Tool_Info.spider_methods.save_info.file_path_name
        for file_name in file_name_list:
            try:
                with open(save_path+file_path_name+'/'+file_name, 'r', encoding='utf-8') as file:
                    page_source = file.read()
                soup = BeautifulSoup(page_source, 'lxml')  # 创建 beautifulsoup 对象
                item_list = soup.find_all('div', class_='RichContent RichContent--unescapable')
                for item in item_list:
                    content = item.find('div', class_="css-376mun").find_all('p')
                    content_data = ""
                    agree_num = 0
                    discuss_num = 0
                    release_time = ""
                    for i in content:
                        content_data += re.sub(r'<.*?>', '', i.text)
                    release_time = item.find('div', class_="ContentItem-time").find('span').text

                    agree = item.find('div', class_="ContentItem-actions").find_all('button')[0].text

                    pattern = r'赞同\s+(\d+(\.\d+)?)'
                    match = re.search(pattern, agree.replace('万', '0000'))
                    if match:
                        agree_num = eval(match.group(1))
                        if type(agree_num) != int:
                            agree_num = agree_num * 10000
                    else:
                        agree_num = 0
                    discuss = item.find('div', class_="ContentItem-actions").find_all('button')[2].text
                    pattern = r'(\d+)\s*条评论'
                    match = re.search(pattern, discuss.replace(',', ''))
                    if match:
                        discuss_num = eval(match.group(1))
                    else:
                        discuss_num = 0
                    self.Zhihu_Spider_Tool_Info.spider_methods.save_info.data.search_list_page_item_content_list.append(Search_List_Page_Item_Content(content=content_data,agree_num=agree_num,discuss_num=discuss_num, release_datetime=release_time))

                item_dicts = [item.__dict__ for item in self.Zhihu_Spider_Tool_Info.spider_methods.save_info.data.search_list_page_item_content_list]
                json_str = json.dumps(item_dicts, indent=4, ensure_ascii=False)
                with open(save_path+file_path_name+'/'+file_name + "."+self.Zhihu_Spider_Tool_Info.spider_methods.save_info.file_type_info.search_list_page_item_content,'w', encoding='utf-8') as f:
                    f.write(json_str)
            except:
                return False
