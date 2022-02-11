from bs4 import BeautifulSoup as bs
import requests
from selenium import webdriver
from fake_useragent import UserAgent
import pymysql
import time
import math


def conndb():
    db = pymysql.connect(host="localhost",
                         port=3306,
                         user="root",
                         passwd="123456",
                         db="591",
                         charset="utf8mb4")
    cursor = db.cursor()
    cursor.execute("SELECT VERSION()")
    data = cursor.fetchone()
    print("Database version:%s" % data)
    return db


# %%定義參數條件


def seturl(value):
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
    url = baseurl + param

    return url


# %%定義換頁網址


def getnexturl(firstrow, totalrows, url):
    print(firstrow)
    print(totalrows)
    result = url + f"&firstRow={firstrow}&totalRows={totalrows}"
    return result


# %% 資料庫寫入


def insert_sql(data, db):
    print("data = " , data)
    keys = ",".join(f"`{k}`" for k in data.keys())
    print("keys = " , keys)
    values = ",".join(f"'{k}'" for k in data.values())
    print("values = " , values)
    sql = f"INSERT IGNORE INTO `rent` ({keys}) VALUES ({values});"
    cursor = db.cursor()
    cursor.execute(sql)
    db.commit()


# %%資料欄位，條件篩選


def get591data(area):
    db = conndb()
    url = seturl(area)
    user_agent = UserAgent()
    res_item = requests.get(url, headers={"user-agent": user_agent.random})
    if res_item.status_code == 200:
        browser = webdriver.Chrome("/Users/jarvis/Desktop/chromedriver")
        browser.get(url)
        time.sleep(3)

        soup = bs(browser.page_source, "html.parser")
        totalrows = int(soup.find("span", "TotalRecord").text.split(" ")[1])
        #totalrows = soup.find("div",{"class":"switch-amount"}.find("span").text)
        #totalrows = int((soup.find( "div" , { "class":"switch-amount" })).find("span").text)
        print("totalrows:", totalrows)

        page_lenth = math.ceil(totalrows / 30)
        print("page:", page_lenth)

        firstrow = 0

        while firstrow <= totalrows:
            soup = bs(browser.page_source, "html.parser")
            currect_page_list = soup.find_all("section", "vue-list-rent-item")
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

                data_info = {
                    "area": area,
                    "location": location,
                    "address": address,
                    "title": title,
                    "price": price,
                    "kind": kind,
                    "size": size,
                    "floor": floor,
                    "roomstyle": roomstyle
                }

                insert_sql(data_info, db)

            # 換頁
            if soup.find("a", "pageNext last"):
                print("終於爬完啦")
                browser.close()
                break

            else:
                firstrow += 30
                nexturl = getnexturl(firstrow, totalrows, url)
                browser.get(nexturl)
                time.sleep(3)


# %%
if __name__ == "__main__":
    get591data("台北市")
