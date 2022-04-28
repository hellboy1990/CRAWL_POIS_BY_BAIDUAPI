# 利用百度API提供的圆形检索爬取POIS

## 一、根据左下点、右上角切分检索区域
### 1.1 首先计算左下点POI1与右上点POT2的直线距离DIST.
### 1.2 解方程
#### 1）求X，X为分段数。DIST = X * RADIUS
#### 2）求LAT_X，LNG_X，LAT_X为当前分段数下每段的纬度差。LAT_X = (LAT2 - LAT1)/X
### 1.3 根据X生成圆心列表。
#### 1）方向一。起点为左下点，沿斜线方向，变化值为LAT_X * 2，LNG_X * 2。
#### 2）方向二。起点为左下点，沿垂直方向，变化值为LAT_X * 2，0。
#### 3）方向三。起点为左下点，沿水平方向，变化值为0，LNG_X * 2。
#### 4）方向四。起点为右上点，沿水平方向，变化值为0，-LNG_X * 2。
#### 5）方向五。起点为右上点，沿垂直方向，变化值为-LAT_X * 2，0。

## 二、基于圆心列表，检索POI
### 2.1 检索API并进行坐标纠偏
https://api.map.baidu.com/place/v2/search?query=银行&location=39.915,116.404&radius=2000&output=xml&ak=您的密钥 //GET请求
### 2.2 对POIS结果去重
### 2.3 写入CSV
#### 1）区域分割文件命名方式为filetmp = filepath + pot12 + '.csv'
#### 2）POI文件命名方式为filename = filepath + itemy + pot12 + '.csv'
