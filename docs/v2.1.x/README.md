# 安装指南



## 1. 安装Link IoT Edge版本 >= 2.1.0

## 2. 准备系统依赖库，需要系统支持编译.
### 2.1. Ubuntu 

```
sudo apt-get install libgirepository1.0-dev \
  libcairo2-dev gobject-introspection libreadline-dev \
  libdbus-1-dev libdbus-glib-1-dev libxml2-dev libxslt1-dev

```
### 2.2. CentOS 
```
sudo yum install dbus-devel dbus-glib-devel cairo-devel \
  gobject-introspection-devel cairo-gobject-devel readline-devel \
  libxml2-devel libxslt-devel
```

## 3. 安装python解析器和pip工具，python版本 >= 3.5.2
输入下述命令，确认是否已经安装了python3环境
```
python3 -V
```
如果已经存在python3环境则直接进入步骤4，否则继续以下步骤

### 3.1. Ubuntu
```
sudo apt-get update
sudo apt-get install python3
```

### 3.2. CentOS
```
sudo yum update
sudo yum install python3
```

## 4. 安装python runtime依赖的第三方库
```
./python_install.sh
```

# 问题列表

1. 安装过程中，遇到File "/usr/lib/python3.5/locale.py", line 594, in setlocale
    return _setlocale(category, locale)错误

	```
	export LC_ALL=C
	```

2. Python.h: No such file or directory 

	```
	for Ubuntu
		sudo apt-get install python3-dev
		
	for CentOS
		sudo yum install python3-devel
	```

3. py3cairo.h: No such file or directory

	查找该文件，一般在这里/usr/local/include/pycairo/
	
	```
	mkdir /usr/include/pycairo
	cp /usr/local/include/pycairo/py3cairo.h /usr/include/pycairo
	```
  
