import tkinter as tk
from tkinter import ttk
from tkinter import *
from tkinter.filedialog import askdirectory
from bs4 import BeautifulSoup as bs
import requests
from selenium import webdriver
from fake_useragent import UserAgent
import pymysql
import time
import math


class UI():
    def __init__(self):
        self.url = "https://rent.591.com.tw/"
        self.user_agent = UserAgent()
        self.res_item = requests.get(
            self.url, headers={"user-agent": self.user_agent.random})
        self.window = tk.Tk()
        self.window.title("Crawler Pics")
        # self.window.resizable(0,0)
        self.menu = ttk.Combobox(self.window, width=6)
        self.path = StringVar()
        self.lab1 = tk.Label(self.window, text="保存路徑:")
        self.lab2 = tk.Label(self.window, text="選擇分類:")
        self.lab3 = tk.Label(self.window, text="爬取頁數:")
        self.page = tk.Entry(self.window, width=5)
        self.input = tk.Entry(
            self.window, textvariable=self.path, width=80)
        self.info = tk.Text(self.window, height=20 )   #

        self.menu['value'] = ("台北市", "新北市", "桃園市", "新竹市", "新竹縣", "宜蘭縣", "基隆市",
                              "台中市", "彰化縣", "雲林縣", "苗栗縣", "南投縣", "高雄市", "台南市",
                              "嘉義市", "嘉義縣", "屏東縣", "台東縣", "花蓮縣", "澎湖縣", "金門縣", "連江縣")
        self.menu.current(0)

        self.t_button = tk.Button(
            self.window, text='選擇路徑', relief=tk.RAISED, width=8, height=1, command=self.select_Path)

        self.t_button1 = tk.Button(
            # self.window, text='爬取', relief=tk.RAISED, width=8, height=1, command=self.download)
            self.window, text='爬取', relief=tk.RAISED, width=8, height=1, command=self.startcrawler)

        self.c_button2 = tk.Button(
            self.window, text='清空輸出', relief=tk.RAISED, width=8, height=1, command=self.cle)

    def select_Path(self):
        # 本地路徑
        path_ = askdirectory()
        self.path.set(path_)

    def gui_arrang(self):

        self.lab1.grid(row=0, column=0)
        self.lab2.grid(row=1, column=0)
        self.menu.grid(row=1, column=1, sticky=W)
        self.lab3.grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.page.grid(row=2, column=1, sticky=W)
        self.input.grid(row=0, column=1)
        self.info.grid(row=3, rowspan=5, column=0,
                       columnspan=3, padx=15, pady=15)
        self.t_button.grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.t_button1.grid(row=1, column=2)
        self.c_button2.grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)

    def cle(self):
        """定義一个函数，用于清空输出框的内容"""
        self.info.delete(1.0, "end")

    def startcrawler(self):
        self.write("startcrawler")
        self.get591data(self.menu.get())

    def conndb(self):
        db = pymysql.connect(host="localhost", port=3306, user="root",
                             passwd="123456", db="591", charset="utf8mb4")
        cursor = db.cursor()
        cursor.execute("SELECT VERSION()")
        data = cursor.fetchone()
        self.write("連線資料庫 Database version:%s" % data)
        return db

    def seturl(self, value):
        city_dict = {
            "台北市": "&region=1",
            "新北市": "&region=3",
            "桃園市": "&region=6",
            "新竹市": "&region=4",
            "新竹縣": "&region=5",
            "宜蘭縣": "&region=21",
            "基隆市": "&region=2",
            "台中市": "&region=8",
            "彰化縣": "&region=10",
            "雲林縣": "&region=14",
            "苗栗縣": "&region=7",
            "南投縣": "&region=11",
            "高雄市": "&region=17",
            "台南市": "&region=15",
            "嘉義市": "&region=12",
            "嘉義縣": "&region=13",
            "屏東縣": "&region=19",
            "台東縣": "&region=22",
            "花蓮縣": "&region=23",
            "澎湖縣": "&region=24",
            "金門縣": "&region=25",
            "連江縣": "&region=26",
        }
        baseurl = "https://rent.591.com.tw/?showMore=1"
        param = city_dict[value]
        url = baseurl+param

        return url

    def getnexturl(self, firstrow, totalrows, url):
        #self.write(firstrow)
        #self.write(totalrows)
        result = url + f"&firstRow={firstrow}&totalRows={totalrows}"
        return result

    def insert_sql(self, data, db):
        keys = ",".join(f"`{k}`" for k in data.keys())
        values = ",".join(f"'{k}'" for k in data.values())
        sql = f"INSERT IGNORE INTO `rent` ({keys}) VALUES ({values});"
        cursor = db.cursor()
        cursor.execute(sql)
        db.commit()

    def get591data(self, area):
        db = self.conndb()
        url = self.seturl(area)
        if self.res_item.status_code == 200:
            browser = webdriver.Chrome("./chromedriver")
            browser.get(url)
            time.sleep(3)


            soup = bs(browser.page_source, "html.parser")
            totalrows = int(
                soup.find("span", "TotalRecord").text.split(" ")[1])
            #totalrows = soup.find("div",{"class":"switch-amount"}.find("span").text)
            #totalrows = int((soup.find( "div" , { "class":"switch-amount" })).find("span").text)
            self.write("總共筆數:", totalrows)

            page_lenth = math.ceil(totalrows/30)
            self.write("總頁數:", page_lenth)

            firstrow = 0
            while firstrow <= totalrows:
                self.write("正在擷取第: " + str(int(firstrow/30+1))+ " 頁")
                soup = bs(browser.page_source, "html.parser")
                currect_page_list = soup.find_all(
                    "section", "vue-list-rent-item")
                for i in currect_page_list:
                    location = (
                        i.find("div", {"class": "item-area"}).find("span").text).split("-")[0]
                    address = (
                        i.find("div", {"class": "item-area"}).find("span").text).split("-")[1]
                    # rstrip 刪除右邊的標籤,strip 刪除空格或換行
                    title = (
                        i.find("div", {"class": "item-title"}).text).rstrip("優選好屋").strip()
                    price = ((i.find("div", {"class": "item-price-text"}).find(
                        "span").text).strip().rstrip("元/月")).replace(",", "")
                    stylelist = (i.find("ul", "item-style").text).split(" ")
                    kind = stylelist[0]
                    roomstyle = stylelist[1]
                    size = stylelist[2].rstrip("坪")
                    floor = stylelist[3]

                    data_info = {"area": area,
                                 "location": location,
                                 "address": address,
                                 "title": title,
                                 "price": price,
                                 "kind": kind,
                                 "size": size,
                                 "floor": floor,
                                 "roomstyle": roomstyle}

                    self.insert_sql(data_info, db)
                # 換頁
                if soup.find("a", "pageNext last"):
                    self.write("終於爬完啦")
                    browser.close()
                    break

                else:
                    firstrow += 30
                    nexturl = self.getnexturl(firstrow, totalrows, url)
                    browser.get(nexturl)
                    time.sleep(3)

    def write(self, *message, endline="\n", sep=" "):
        text = ""
        for item in message:
            text += "{}".format(item)
            text += sep
        text += endline
        self.info.insert(INSERT, text)
        self.info.update()
        self.info.yview_pickplace("end")

def main():
    t = UI()
    t.gui_arrang()
    tk.mainloop()


if __name__ == '__main__':
    main()
