### 简介

这是一个帮助B站5000粉丝数以下的主播获取推流码的程序

只实现了基础功能，包括简单的配置功能

本程序需要你安装了直播姬

### 运行

在命令行运行

```shell
python stream.py
```

或如果是exe版本：

```shell
./stream.exe
```

如果程序在当前目录下没有找到 `config.json` 文件，则进入交互模式，按照提示输入信息即可顺利获取服务器地址和推流码进行直播

如果在当前目录下找到 `config.json` 文件，则默认使用此文件中的配置

若要指定配置文件，请运行

```shell
python stream.py --config PATH_TO_CONFIG
```

或

```shell
./stream.exe --config PATH_TO_CONFIG
```

### 配置

config文件是形如下面的json文件

```json
{
    "blive_path": "path/to/your/livehime"
    "user_cookies": "your_cookie",
    "room_id": 123456,
    "area": 235
}
```

程序会默认查找当前目录下的 `config.json` 文件，如果未找到则进入交互模式，需要在命令行中输入必要信息。

其中：

- `blive_path` 为你的直播姬安装的绝对路径，用双引号包围，一般来说这是一个名为 `livehime` 的文件夹，其中有一个可执行文件 `livehime.exe` 和一个命名为直播姬版本号的文件夹

- `user_cookies` 为你的B站Cookies值，用双引号包围，获取方法可以参见交互模式下给出的提示

- `room_id` 为你的直播间号

- `area` 为分区号。程序本身会输出分区列表和ID的对应关系，可以参照输出进行查找

- 如果任意配置项缺失，则仍会要求在命令行中输入

### 注意

- 本程序不保证没有bug，也不保证B站是否会对使用者的账号做出限制。使用本程序后果自负
