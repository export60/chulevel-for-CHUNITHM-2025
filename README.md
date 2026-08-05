# chulevel-for-CHUNITHM-2025
## 简介
  适用于中二节奏2025的带分数的等级分表生成器，数据格式支持水鱼和落雪。

  当前版本为 2026.07.16 更新后，版本号Ver.CN1.33。

## 数据
  支持水鱼查分器和落雪查分器
  
### 水鱼  
  查分器地址：[跳转链接](maimai.diving-fish.com, "水鱼查分器")
  
  需要您亲手点击一次“解锁全曲”并确认，然后点击“导出为CSV”按钮，选择“UTF-8”编码，放至项目根目录下，重命名为df_score.csv。
  
### 落雪
  查分器地址：[跳转链接](maimai.lxns.net, "落雪查分器")
  
  左侧栏跳转到“成绩管理”，选择“备份成绩”，选择“导出成绩”，放至项目根目录下，重命名为lx_score.csv。
  
## 环境
  Python3 且安装有json、PIL、pandas库，版本没有严格要求。
  
  如若遇到问题，可尝试更换库版本如下：
  
  PIL == 9.3.0
  
  pandas == 2.1.4

## 使用方法

  将导出的存档重命名为 df_score.csv 或 lx_score.csv 后，放在与draw_chart.py文件同一目录下，直接使用Python运行draw_chart.py即可。
  
  您需要输入所生成分表的等级，目前支持 10、10+、11、11+、12、12+、13、13+、14、14+、15、15+。
  
  于draw_chart.py文件开头部分，可以更改Player名称、是否生成高清图，以及选择使用哪种查分器。
  
  程序正常运行后分表图片将输出至./output/目录下。

## Q&A

    Q:为什么要做这么一个东西？
    
    A:单纯做着玩的，若有人需要可以随时拿去用。


    Q:程序报错 UnicodeDecodeError: 'utf-8' codec can't decode byte 0xc5 in position 0: invalid continuation byte. 
  
    A:使用了类似于Office、WPS等富文本编辑器进行了保存，导致数据格式上发生了一些改变。建议直接重命名导出的csv文件，然后移动至目标目录。
