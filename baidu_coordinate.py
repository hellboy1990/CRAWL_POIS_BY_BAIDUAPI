# -*- coding: utf-8 -*-

import math

x_pi = 3.14159265358979324 * 3000.0 / 180.0
pi = 3.1415926535897932384626  # π
a = 6378245.0  # 长半轴
ee = 0.00669342162296594323  # 偏心率平方

def bd09_to_gcj02(bd_lng,bd_lat):#百度坐标系(BD-09)转火星坐标系(GCJ-02)
    global gc_lng,gc_lat
    x = bd_lng - 0.0065
    y = bd_lat - 0.006
    z = math.sqrt(x * x + y * y) - 0.00002 * math.sin(y * x_pi)
    theta = math.atan2(y, x) - 0.000003 * math.cos(x * x_pi)
    gc_lng = z * math.cos(theta)
    gc_lat = z * math.sin(theta)
    return [gc_lng, gc_lat]

def gcj02_to_wgs84(gc_lng,gc_lat):#GCJ02(火星坐标系)转GPS84
    if out_of_china(gc_lng, gc_lat):
        dlat = transformgc_lat(gc_lng - 105.0, gc_lat - 35.0)
        dlng = transformgc_lng(gc_lng - 105.0, gc_lat - 35.0)
        radlat = gc_lat / 180.0 * pi
        magic = math.sin(radlat)
        magic = 1 - ee * magic * magic
        sqrtmagic = math.sqrt(magic)
        dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * pi)
        dlng = (dlng * 180.0) / (a / sqrtmagic * math.cos(radlat) * pi)
        mglat = gc_lat + dlat
        mglng = gc_lng + dlng
        wgslng=gc_lng * 2 - mglng
        wgslat=gc_lat * 2 - mglat
        return [wgslng,wgslat ]
    else:
        return [gc_lng, gc_lat]

def transformgc_lng(gc_lng,gc_lat):
    ret = 300.0 + gc_lng + 2.0 * gc_lat + 0.1 * gc_lng * gc_lng + \
          0.1 * gc_lng * gc_lat + 0.1 * math.sqrt(math.fabs(gc_lng))
    ret += (20.0 * math.sin(6.0 * gc_lng * pi) + 20.0 *
            math.sin(2.0 * gc_lng * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(gc_lng * pi) + 40.0 *
            math.sin(gc_lng / 3.0 * pi)) * 2.0 / 3.0
    ret += (150.0 * math.sin(gc_lng / 12.0 * pi) + 300.0 *
            math.sin(gc_lng / 30.0 * pi)) * 2.0 / 3.0
    return ret

def transformgc_lat(gc_lng,gc_lat):
    ret = -100.0 + 2.0 * gc_lng + 3.0 * gc_lat + 0.2 * gc_lat * gc_lat + \
          0.1 * gc_lng * gc_lat + 0.2 * math.sqrt(math.fabs(gc_lng))
    ret += (20.0 * math.sin(6.0 * gc_lng * pi) + 20.0 *
            math.sin(2.0 * gc_lng * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(gc_lat * pi) + 40.0 *
            math.sin(gc_lat / 3.0 * pi)) * 2.0 / 3.0
    ret += (160.0 * math.sin(gc_lat / 12.0 * pi) + 320 *
            math.sin(gc_lat * pi / 30.0)) * 2.0 / 3.0
    return ret

def out_of_china(gc_lng,gc_lat):
    return (gc_lng > 73.66 and gc_lng < 135.05 and gc_lat > 3.86 and gc_lat < 53.55)

def bd09_wgs84(bd_lng,bd_lat):
    gc = bd09_to_gcj02(bd_lng,bd_lat)
    wgs = gcj02_to_wgs84(gc[0],gc[1])
    return [wgs[0],wgs[1]]