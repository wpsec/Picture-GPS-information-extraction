# Picture-GPS-information-extraction
图片GPS信息提取



依赖
```bash
pip install -r requirements.txt
```



单张图片获取

```python
python2 imagegps.py -p 图片名
```

![image](https://github.com/wpsec/Picture-GPS-information-extraction/blob/main/%E5%9B%BE%E7%89%87/1.png)


目录内提取

```python
python2 imagegps.py -d 目录名
```

![image](https://github.com/wpsec/Picture-GPS-information-extraction/blob/main/%E5%9B%BE%E7%89%87/2.1.png)


从网站爬取提取

爬取的图片会保存在本目录的 gpsimage文件夹里

```python
python imagegps.py -u url
```

![image](https://github.com/wpsec/Picture-GPS-information-extraction/blob/main/%E5%9B%BE%E7%89%87/2.gif)
