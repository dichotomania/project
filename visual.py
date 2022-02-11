from ast import Lambda
from itertools import groupby
import pandas as pd
import pymysql
from pyecharts.charts import Bar, Line, Pie
from pyecharts import options as opts


conn = pymysql.connect(host="localhost", user="root",
                       passwd="123456", port=3306, db="591")
cursor = conn.cursor()

sql = 'select * from rent'

cursor.execute(sql)
result = cursor.fetchall()

df = pd.read_sql(sql, conn)


location_group = df.groupby(["location"])
location_com = location_group["price"].aggregate(["mean", "count"])
location_com.reset_index(inplace=True)
location_message = location_com.sort_values("count", ascending=False)
locationr = location_message["location"]
l1 = location_message["count"]
l2 = location_message["mean"]
l2 = ['%.2f' % i for i in l2.tolist()]
# print(l2)
# print(location_com)
# #%%
# #租房數&租金直方折線圖

bar = (
    Bar(init_opts=opts.InitOpts(width="1200px", height="500px", theme='light'))
    .add_xaxis(locationr.tolist())
    .add_yaxis("房屋出租數", l1.tolist())
    .extend_axis(
        yaxis=opts.AxisOpts(
            axislabel_opts=opts.LabelOpts(formatter="{value} 元"), interval=10000
        )
    )
    .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
    .set_global_opts(
        title_opts=opts.TitleOpts(title="台北市各行政區出租房數&平均租金"),
        yaxis_opts=opts.AxisOpts(
            axislabel_opts=opts.LabelOpts(formatter="{value} 間")),
    )
)

line = Line().add_xaxis(locationr.tolist()).add_yaxis(
    "平均租金",  l2, yaxis_index=1)
bar.overlap(line)
bar.render("台北市各行政區出租房數&平均租金.html")


# 出租房面積圓環圖

square_info = df['size'].astype(float)
print(type(square_info[0]))
bins = [0, 10, 20, 40, 60, 100, 300]
level = ['0-10坪', '10-20坪', '20-40坪', '40-60坪', '60-100坪', '100-300坪']
square_stage = pd.cut(square_info, bins=bins,
                      labels=level).value_counts().sort_index()
attr = square_stage.index.tolist()
v1 = square_stage.values.tolist()

pie = (
    Pie()
    .add("", [list(z)for z in zip(attr, v1)], radius=[80, 150])
    # 加入百分比
    .set_series_opts(label_opts=opts.LabelOpts(is_show=True, formatter="{d}%"))
    .set_global_opts(title_opts=opts.TitleOpts(title="台北市出租房房屋面積分布",
                                               pos_left="center",
                                               pos_bottom="center"),
                     legend_opts=opts.LegendOpts(pos_left="left",
                                                 orient="vertical"),
                     ))
pie.render("台北市出租房房屋面積分布.html")


# #%%
# 出租房型疊加直方圖
mask = (df["kind"] != "其他")  # 過濾掉其他
location_group = df[mask].groupby("location")
location_values = [k[0] for k in location_group]
gp = df[mask].sort_values("location").groupby("kind")
s1 = gp.get_group("獨立套房")["location"].value_counts().tolist()
s2 = gp.get_group("分租套房")["location"].value_counts().tolist()
s3 = gp.get_group("雅房")["location"].value_counts().tolist()
s4 = gp.get_group("整層住家")["location"].value_counts().tolist()
# s5 = gp.get_group("車位")["location"].value_counts().tolist()

bar = (
    Bar(init_opts=opts.InitOpts(width="1200px", height="500px", theme='light'))
    .add_xaxis(location_values)
    .add_yaxis("獨立套房", s1, stack="stack1")
    .add_yaxis("分租套房", s2, stack="stack1")
    .add_yaxis("雅房", s3, stack="stack1")
    .add_yaxis("整層住家", s4, stack="stack1")
    # .add_yaxis("車位", s5, stack="stack1")
    .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
    .set_global_opts(
        title_opts=opts.TitleOpts(title="房型分類"),
        yaxis_opts=opts.AxisOpts(
            axislabel_opts=opts.LabelOpts(formatter="{value} 間")),
    )
)
bar.render("台北市各行政區出租房型分類.html")


# -----------------------------------------
# 單坪租金折現面積圖

df["location"] = df["location"].apply(
    lambda x: "".join([i for i in x if not i.isdigit()]))
df = (df[df["kind"].isin(["雅房", "整層住家", "獨立套房", "分租套房", "車位"])].
      groupby(["location", "kind"])[["price", "size"]]
      .sum()
      .reset_index()
      .sort_values("location"))
df.insert(4, column="average", value=df["price"]//df["size"])


line = (
    Line()
    .add_xaxis(location_values)
    .add_yaxis("雅房", df.groupby("kind").get_group("雅房")["average"],
               areastyle_opts=opts.AreaStyleOpts(opacity=0.5))
    .add_yaxis("整層住家", df.groupby("kind").get_group("整層住家")["average"],
               areastyle_opts=opts.AreaStyleOpts(opacity=0.4))
    .add_yaxis("獨立套房", df.groupby("kind").get_group("獨立套房")["average"],
               areastyle_opts=opts.AreaStyleOpts(opacity=0.3))
    .add_yaxis("分租套房", df.groupby("kind").get_group("分租套房")["average"],
               areastyle_opts=opts.AreaStyleOpts(opacity=0.2))
    # .add_yaxis("車位", df.groupby("kind").get_group("車位")["average"],
    #            areastyle_opts=opts.AreaStyleOpts(opacity=0.1))
    .set_global_opts(title_opts=opts.TitleOpts(title="各房型單坪租金"))

)
line.render("單坪租金圖.html")


# ------------------------------------------------------
