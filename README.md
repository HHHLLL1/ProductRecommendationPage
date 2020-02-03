# 商品推荐系统网页
## 运行环境：
    python 3.6
    django
    numpy
    pandas
    pymysql
    ......
 
 
 ## 目录说明
    analytics: 用户商品行为信息数据库模型、保存离线推荐结果、获取点击行为数据
    items: 商品信息数据库模型
    login: 与网页的连接、读取数据库数据并在网页中展示、注册并保存用户信息、登录
    recommend: 推荐算法
    RecSysInItem: django配置文件
    reptile: 数据采集并导入数据库中（getItemInfo.py）、数据处理
    static: js和css文件
    templates: html文件
    
 
## main
    本项目是基于python、mysql和django网页的商品推荐系统网站。
    项目分为三部分：数据采集、网页设计和推荐算法
    
### 数据采集
    爬取淘宝搜索页面的商品信息，使用了建立IP池、随机UA等反反爬机制，并且把数据通过pymysql导入到数据库中

### 网页设计
    使用django网页设计
    学习了这个教程：https://www.jianshu.com/p/033217dbfe25
   
### 推荐算法
    使用numpy进行了常见推荐算法的实现
   
 
## 总结
    此项目完成了一个简单网页商品推荐的实现，从数据采集到每个用户的个性化商品推荐到网页展示，流程完整，学习了很多。
    
    
