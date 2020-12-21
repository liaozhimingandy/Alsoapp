## pip导出依赖包

```python
# 1.导出python依赖包
pip freeze > requirements.txt
# 2.根据导出依赖包文件批量安装依赖包并且从指定镜像地址下载
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
# 3.根据导出依赖包文件批量卸载依赖包
pip uninstall -r requirements.txt -y
```
