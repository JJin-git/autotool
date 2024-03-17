import re
from unittest.mock import seal
from urllib.request import urlopen
import requests
from bs4 import BeautifulSoup
from furl import furl
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from urllib.parse import urlparse
from urllib.error import HTTPError, URLError


# GUI
import sys
from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QIcon

import time
import pandas as pd


# first_a=[]
# new_links=[]
class AAA(QWidget):
    #--- 리스트 모음

    global first_a               ## 최초 url 
    first_a=[]
    
    global new_path              ## url의 모든 경로
    new_path=[]     
    
    # global new_links ##중복 제거된 url
    # new_links=[]
    
    global val_x                ## 옵션 태그 내용 중복o
    val_x=[]    
    
    global val                  ## 옵션 태그 내용 중복x
    val=[]

    global url_result           # 모든 URL
    url_result = []

    global union_result         ## union sql 
    union_result = []

    global sql_result           ## sql 
    sql_result = []

    global xss_result           ## xss
    xss_result = []

    global down_result          ## file download
    down_result = []

    global dir_result           ## directory indexing 
    dir_result = []

    global browser_text         ## GUI 화면에 보여주기 위함
    browser_text = []

    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('Automation Tools')
        self.setWindowIcon(QIcon('C:\py code\icon.png'))
        self.setGeometry(100, 100, 500, 300)
        self.setFixedSize(500, 300)

        ## 레이아웃
        self.layout = QFormLayout()
        self.setLayout(self.layout)


        self.url_label = QLabel("URL을 입력해주세요 \n -> ex. http:// ")
        self.url_line = QLineEdit()
        #self.down_label = QLabel("보고서를 다운 받을 경로를 지정해주세요")
        #self.down_route = QPushButton("Load")
        self.down_textBrowser = QTextBrowser()
        self.submit_btn = QPushButton("Start")
        self.exit_btn = QPushButton("Quit")
        self.state_bar = QProgressBar()

        self.layout.addWidget(self.url_label)
        self.layout.addRow("⇨ ", self.url_line)
        #self.layout.addWidget(self.down_label)        
        #self.layout.addWidget(self.down_route)
        self.layout.addWidget(self.down_textBrowser)
        self.layout.addWidget(self.submit_btn)
        #self.layout.addWidget(self.state_bar)
        self.layout.addWidget(self.state_bar)
        self.layout.addWidget(self.exit_btn)

        #--- 버튼 클릭 시 발생되는 이벤트
        self.layout.setVerticalSpacing(10)
        #self.down_route.clicked.connect(self.fun_Folder_load)
        self.submit_btn.clicked.connect(self.fun_append_text)
        self.exit_btn.clicked.connect(QCoreApplication.instance().quit)
        
        self.show()


    def fun_append_text(self):      #--- csv 파일
        global targetUrl
        targetUrl = self.url_line.text()
        

        global url_link             #모든 접속 가능한 url
        url_link=[]
        
        self.total_url(targetUrl)

        
        for i in range(len(new_path)):              #하위 모든 경로 가져오기
            s = targetUrl + new_path[i]
            self.total_url(s)

        val=['c','n']
        for i in range(len(new_path)):              #경로에 targetUrl + 경로  문자열 합치기
            s = furl(new_path[i])
            if 'searchType' in new_path[i]:         #우리 서버 searchtype만 적용됨
                for j in range(len(val)):           
                    s.args['searchType'] = val[j]
                    url = targetUrl + s.url
                    url_link.append(url)
            else:
                url = targetUrl + new_path[i]
                url_link.append(url)

        #url_link.append(url)
 
        
        self.parsing(url_link)
        self.down()
        self.dir_indexing()
        self.AAA_result()
        
         
        
    def fun_Folder_load(self):      #--- 경로 지정
        global openFolder
        openFolder = QFileDialog.getExistingDirectory(self)
        self.down_textBrowser.setText(str(openFolder))
   
        df = pd.DataFrame.from_dict(url_link, union_result, sql_result, down_result, dir_result)
        df.to_csv(openFolder + '/hhhello.csv', encoding="utf-8")
 
        
   
 
    ###접속 가능한 url 가져오는 함수    
    def total_url(self, targetUrl):    

        first = requests.get(targetUrl)                                                               #최초 url requests
        soup = BeautifulSoup(first.text, 'html.parser')
        links = soup.select('a')   #a href 태그 가져오기

        for i in links:
            if 'http://' in i.attrs['href'] or 'https://' in i.attrs['href']:                                               #다른 도메인 제외
                continue
            
            elif "/" not in i.attrs['href']:
                fi =  "/" + i.attrs['href']
                first_a.append(fi)
                
            else:
                fii = i.attrs['href']
                first_a.append(fii)

        
        for i in first_a:
            if i not in new_path:
                new_path.append(i)
            
        return new_path
    
 
    ###파라미터 파싱 과정
    def parsing(self, url_link):
        
        global par
        global f_url                                                                #furl 설정
  
        try: 
            for i in range(len(url_link)):
                p = urlparse(url_link[i])
                par = re.split('\=|\&',p.query)
                par = list(filter(None, par))

                for j in range(len(par)):     
                    f_url = furl(url_link[i])
                    self.xss(j,i)                                                   #j는 파리미터 개수 전달해줌 
                    self.sql(j,i)

        except ValueError :
            return
        
        
    ###XSS 취약점 함수
    def xss(self,j,i):
        
        xss_url=[]
        xss = [
            '<script>alert(\'AAA\')</script>',
            '\"><script>alert(\'AAA\')</script>'   
            ]

        for k in range(len(xss)):                                                              #파라미터 값에 스크립트 문을 넣을 때
            f_url.args[par[j]] = xss[k]
            xss_url.append(f_url.url)
        
        # for k in range(len(xss)):
        #     baro = url_link[i] + xss[k]                                                       #바로 뒤에 스크립트 문을 넣을 때
 
        #     xss_url.append(baro)

        for i in range(len(xss_url)):
            global res_xss
            res_xss = requests.get(xss_url[i])
            soup = BeautifulSoup(res_xss.text, 'html.parser')
            
            if res_xss.status_code == 200 :
                if re.search('AAA', str(soup.find_all('script'))):
                    xss_result.append(res_xss.url)
                    print("※ Reflected XSS 취약점 탐지: ", res_xss.url)
         
      
    
    ###SQL 인젝션
    def sql(self, j,i):
        
        sql_url=[]
        union_sql=[
                    'AAA\') union ALL select null-- ', 
                    'union All select null-- '
                    ]  
      
        for k in range(len(union_sql)):                                                                                    #파라미터 값에 sql 문을 넣을 때
            f_url.args[par[j]] = union_sql[k]
            sql_url.append(f_url.url)
            
        for k in range(len(union_sql)):                                                                                   #바로 뒤에 sql 문을 넣을 때
            baro = url_link[i] + union_sql[k]
            sql_url.append(baro)
              
        for i in range(len(sql_url)):
            res_sql = requests.get(sql_url[i])

            if "The used SELECT statements have a different number of columns" in res_sql.text:
                print("※ Union SQL 인젝션 취약점 탐지: " , res_sql.url)
                union_result.append(res_sql.url)                                                                                                  #union sql 인젝션 url 
                
                
                
    ###디렉토리 인덱싱
    def dir_indexing(self):
 
        dir_url = []
        dir = ['/icons/', '/images/', '/admin/', '/download/', '/file/']

        for k in range(len(dir)):
            baro = targetUrl + dir[k]
            dir_url.append(baro)

        for k in range(len(dir_url)):
            res_dir = requests.get(dir_url[k])
            
            if "Index of" in res_dir.text:
                print("디렉 리스트", res_dir.url)
                dir_result.append(res_dir.url)                                  #indexing url 
      

    ###파일 다운로드 취약점
    def down(self):
             
        dow = furl(targetUrl + '/pds/downloadFile?fullName=')
        dow.args['fullName']='../../../../../../../../../../windows/system32/drivers/etc/services'           #fullName 파라미터에 파일 다운로드 취약점 구문 삽입
        res_down = requests.get(dow.url)

        if res_down.status_code == 201:                     #응답코드가 201 이라면, 취약점으로 진단
            print("※ 파일 다운로드 취약점: ", res_down.url)
            #time.sleep(0.01)
            down_result.append(res_down.url)                 #파일 다운로드 url

          
    def AAA_result(self):
        for i in range(101):
            self.state_bar.setValue(i)
            time.sleep(0.5)
            i = i + 1
            
        print("---------------------------------------------------------------------------------------------------------------------------------------------------------------------------")

        print(   
            "   total URL: " + str(len(url_link))+ 
            ",  total Union SQL : " + str(len(union_result)) +
            ",  total SQL : " + str(len(sql_result)) + 
            ",  total XSS: " + str(len(xss_result)) + 
            ",  total File Download: " + str(len(down_result)) + 
            ",  total Directory Indexing: " + str(len(dir_result))
        )


        
        self.down_textBrowser.setText(          
            
            "total URL: " + str(len(url_link))+ "\n" +
            "total Union SQL : " + str(len(union_result)) + "\n" +
            "total SQL : " + str(len(sql_result)) + "\n" +
            "total XSS: " + str(len(xss_result)) + "\n" +
            "total File Download: " + str(len(down_result)) + "\n" +
            "total Directory Indexing: " + str(len(dir_result)))


   
if __name__ == '__main__':
    dow = QApplication(sys.argv)
    ex = AAA()
    sys.exit(dow.exec_())
