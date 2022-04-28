# -*- coding:utf-8 -*-

import sys
import time
import csv
import json
import importlib
import requests
import pandas as pd
from crawl_pois_baidu import baidu_coordinate
import os
from headers import get_headers
import math

# 圆形区域检索
# https://api.map.baidu.com/place/v2/search?query=银行&location=39.915,116.404&radius=2000&output=xml&ak=您的密钥 //GET请求
# 求同纬度不同经度两地距离公式：|两地经度差|*cos纬度*111.1 km
# 已知两点的经纬度，求其直线距离30.706458, 121.22551, 30.919843, 121.49802
# SET @x1 = 10, @y1 = 10, @x2=30, @y2=10, @PI=3.14159265358978;（经度，纬度）
# 2*6538.137*ASIN(SQRT(POW(SIN((@y1-@y2)*@PI/360.0),2)+COS(@y1*@PI/180.0)*COS(@y2*@PI/180.0)*POW(SIN((@x1-@x2)*@PI/360.0),2)))


# 根据经纬度求直线距离（纬度，经度）
def cal_dist(pot1_lat, pot1_lng, pot2_lat, pot2_lng):
    PI = 3.14159265358978
    dis = 2*6538.137*math.asin(math.sqrt(math.pow(math.sin((pot1_lat-pot2_lat)*PI/360.0),2) +
                                         math.cos(pot1_lat*PI/180.0)*math.cos(pot2_lat*PI/180.0)*
                                         math.pow(math.sin((pot1_lng-pot2_lng)*PI/360.0),2)))
    return dis


class BaiDuPOI(object):
    def __init__(self, itemy, loc,filename):
        self.itemy = itemy
        self.loc = loc
        self.filename=filename

    def urls(self):  # 返回一个url列表
        global itemy
        itemy=self.itemy
        loc=self.loc
        api_key = baidu_api
        urls = []
        for pages in range(0,1):
        # for pages in range(0, 20):
            url = 'https://api.map.baidu.com/place/v2/search?query=' + itemy + '&location=' + loc + '&radius=' + str(radius) + '&page_size=20&page_num=' \
                  + str(pages) + '&output=json&ak=' + api_key
            # print(url)
            urls.append(url)

        return urls

    def baidu_search(self):
        filename=self.filename
        urls=self.urls()
        dfs=[]
        jnames=[]
        jlats=[]
        jlngs=[]
        #for i in range(0,1):
        for i in range(0, len(urls)):
            #print(urls[i])
            try:
                json_obj=requests.get(urls[i], headers=header, timeout=15)
                data=json_obj.json()
                # print(data)
                data=pd.DataFrame(data)
                # print(data)
                for item in data['results']:
                    # print(item)
                    jname = item["name"]
                    # print(jname)
                    jnames.append(jname)
                    jlat = item["location"]["lat"]
                    # print(jlat)
                    jlats.append(jlat)
                    jlng = item["location"]["lng"]
                    jlngs.append(jlng)

                df=pd.DataFrame({'name':jnames,'bdlat':jlats,'bdlng':jlngs})
                dfs.append(df)
            except Exception as e:
                print(e)
                continue
        dfs=pd.concat(dfs,axis=0,sort=False,ignore_index=True)
        #print(dfs)
        return dfs

    def merge_df(self):
        dfs=[]
        df=self.baidu_search()


# 根据左下、右上的坐标来切分网格(纬度，经度)
def LocaDiv_Circle(pot1_lat, pot1_lng, pot2_lat, pot2_lng, radius, filetmp):
    pot_lats, pot_lngs = pot2_lat - pot1_lat, pot2_lng - pot1_lng
    dist0 = cal_dist(pot1_lat, pot1_lng, pot2_lat, pot2_lng) * 1000  # 转换为米
    # print(dist0)
    lens = math.ceil(dist0 / radius)  # 向上取整，按RADIUS来计算POT1与POT2之间可分为几段
    print("POT1与POT2之间可分为%s段！" % lens)
    lat_x, lng_x = pot_lats / lens, pot_lngs / lens  # 求每段的经度、纬度（由于一般情况下两点间的跨度较小，故误差可忽略）
    # print(lat_x, lng_x)
    pot_centers = []

    # 将分割点信息写入中间文件
    with open(filetmp, 'a+', newline='') as f:
        csv_write = csv.writer(f)
        csv_write.writerow(['FID', 'POT1', 'POT2', 'DIR1', 'DIR2', 'DIR3', 'DIR-3', 'DIR-2'])

        x = 0
        while x < lens:
            # print(x)
            pot_lat_1, pot_lng_1 = pot1_lat + lat_x * 2 * x, pot1_lng + lng_x * 2 * x  # 第1个方向，由POT1向对角线变化
            pot_lat_2, pot_lng_2 = pot1_lat + lat_x * 2 * x, pot1_lng  # 第2个方向，由POT1向上变化
            pot_lat_3, pot_lng_3 = pot1_lat, pot1_lng + lng_x * 2 * x  # 第3个方向，由POT1向右变化
            pot_lat_4, pot_lng_4 = pot2_lat, pot2_lng - lng_x * 2 * x  # 第4个方向，由POT2向左变化
            pot_lat_5, pot_lng_5 = pot2_lat - lat_x * 2 * x, pot2_lng   # 第5个方向，由POT2向下变化
            pot_centeri = [(pot_lat_1, pot_lng_1), (pot_lat_2, pot_lng_2),
                           (pot_lat_3, pot_lng_3), (pot_lat_4, pot_lng_4), (pot_lat_5, pot_lng_5)]

            pot_i = [x, (pot1_lat, pot1_lng), (pot2_lat, pot2_lng), (pot_lat_1, pot_lng_1), (pot_lat_2, pot_lng_2),
                     (pot_lat_3, pot_lng_3), (pot_lat_4, pot_lng_4), (pot_lat_5, pot_lng_5)]
            # print(pot_i)
            csv_write.writerow(pot_i)  # 将信息存入中间文件
            # 将点无差别写为圆心点
            pot_centers.extend(pot_centeri)
            x += 1

    pot_centers1 = list_redunt(pot_centers)  # 对列表去除并重新排序
    print("一共有%s个圆心点！" % len(pot_centers1))
    return pot_centers1


# 对列表去除，并且重新排序
def list_redunt(orgList):
    formatList = list(set(orgList))
    formatList.sort(key=orgList.index)
    # print(formatList)
    return formatList


def tranform(filename):
    df = pd.read_csv(filename, sep=',', encoding="ANSI")
    bdlats, bdlngs = df['bdlat'], df['bdlng']
    wgslats, wgslngs = [], []
    for i in range(0, len(bdlngs)):
        # print(i)
        wgs = baidu_coordinate.bd09_wgs84(bdlngs[i], bdlats[i])
        wgslats.append(wgs[1])
        wgslngs.append(wgs[0])
    df_wgs = pd.DataFrame({"wgslats": wgslats, "wgslngs": wgslngs})
    df1 = pd.concat([df, df_wgs], axis=1)
    print(df1.head())
    df1.to_csv(filename, sep=',', encoding="ANSI")


# write string to json
def string_json():
    '''写入JSON'''
    datas = {
        "POIS": {
            "itemy": ['公园', '植物园', '游乐园', '博物馆', '水族馆', '海滨浴场', '文物古迹', '教堂', '风景区'],
            "APK_KEY": 'QaQv3V6zIk7jWw6PrvShdUHS1oGtpFwv',
            "POT1_LAT": 30.706458,
            "POT1_LNG": 121.22551,
            "POT2_LAT": 30.919843,
            "POT2_LNG": 121.49802,
            "RADIUS": 20000,
        }
    }
    with open(basepath + "\\data_set.json", "w") as write_file:
        write_file.write(json.dumps(datas, ensure_ascii=False, indent=4, separators=(", ", ": ")))


# 对POI结果进行去重
def df_redunt():
    pass


if __name__ == '__main__':
    print("开始爬数据，请稍等...")
    start_time = time.time()
    header={'User-Agent':get_headers()}

    # 路径设置
    basepath = os.getcwd()
    filepath = basepath + "\\baidu_poi\\"
    # print(filepath1)

    # 准备数据
    configs_datas = {
            "itemy": ['公司'],
            "APK_KEY": '******',
            "POT1_LAT": 30.706458,
            "POT1_LNG": 121.22551,
            "POT2_LAT": 30.919843,
            "POT2_LNG": 121.49802,
            "RADIUS": 2000,
    }

    baidu_api = configs_datas['APK_KEY']  # API_KEY设置
    itemys = configs_datas['itemy']  # 标签设置
    pot1_lat, pot1_lng = configs_datas['POT1_LAT'], configs_datas['POT1_LNG']  # 左下角点
    pot2_lat, pot2_lng = configs_datas['POT2_LAT'], configs_datas['POT2_LNG']  # 右上角点
    pot12 = str(int(pot1_lat)) + str(int(pot1_lng)) + "_" + str(int(pot2_lat)) + str(int(pot2_lng))
    radius = configs_datas['RADIUS']  # 圆形搜索的半径

    '''分割区域'''
    filetmp = filepath + pot12 + '.csv'
    locs = LocaDiv_Circle(pot1_lat, pot1_lng, pot2_lat, pot2_lng, radius, filetmp)
    print("已将分割信息写入%s文件！" % filetmp)

    '''检索POI'''
    for itemy in itemys:
        filename = filepath + itemy + pot12 + '.csv'
        # print(locs)
        '''爬取POI'''
        dfs=[]
        for i in range(0,len(locs)):
        # for i in range(0, 2):
            print("第%s个圆心！" % i)
            loci = locs[i]
            loci1 = str(loci[0]) + ',' + str(loci[1])
            # print(loci1)
            par = BaiDuPOI(itemy, loci1,filename)  # 请修改这里的类型参数
            # print(par)
            df = par.baidu_search()
            # print(df)
            dfs.append(df)
        dfs=pd.concat(dfs,axis=0,sort=False,ignore_index=True)
        # print(dfs.head())
        dfs1 = dfs.drop_duplicates(subset=['name', 'bdlat', 'bdlng'])  # 结果去重
        dfs1.to_csv(filename, sep=',', encoding='ANSI')
        print("已将POI写入%s文件！" % filename)

        '''百度坐标纠偏'''
        tranform(filename)
        print("已完成坐标纠偏！")

    end_time = time.time()
    print("数据爬取完毕，用时%.2f秒" % (end_time - start_time))

