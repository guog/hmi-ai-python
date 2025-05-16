# hmi-ai-python

## HTTP API 调用

参见[API 调用说明](./docs/README.md).

## 开发环境准备

- uv: 管理 python 版本,依赖。[Installing uv](https://docs.astral.sh/uv/getting-started/installation/)
  - python >= 3.13
- VSCode >= 1.99

## 运行

```sh
uv sync
uv run fastapi dev
```

根据需要执行以下

```shell
# 激活虚拟环境,适用于macos或linux
source ./.venv/bin/activate
```

## 主要技术栈

- FastAPI : Web Server 框架
- Python-dotenv : 从.env 文件读取环境变量

## 浏览器端调用

```javascript
const eventSource = new EventSource("http://localhost:8000/text2hmi");

eventSource.addEventListener("message", (event) => {
  console.log("收到消息用于显示:", event.data.content);
});
eventSource.addEventListener("action", (event) => {
  console.log(
    `需要执行的函数,第一个函数名称: ${event.data.payload.actions[0].funcName} , 参数: ${event.data.payload.actions[0].params}`
  );
});
eventSource.addEventListener("done", () => {
  console.log("传输完成了.");
  eventSource.close();
});
```

## 通讯协议

基于 [Server-Send Events](https://developer.mozilla.org/zh-CN/docs/Web/API/Server-sent_events/Using_server-sent_events)(SSE)方式进行通讯,可扩充。

服务端每次响应的**原始**格式为:

```txt
event: 事件名称
\n
数据
\n
\n
```

其中，`\n`表示一个空行, `事件名称`和`数据`是需要前后端共同约定和遵守的——协议。

### 消息显示(message)

用于文字显示。

```txt
event: message
\n
data:{id:"chat ID",createdAt:datetime, payload:{ conentx:"文字内容"}}
\n
\n
```

`data`结构说明：

- `id` 用户对话唯一标识,单次用户对话相同,
- `createdAt` ISO8601 格式日期,每次不同,服务端消息产生时间戳
- `payload` 变化的部分，根据 event 类型的不同而不同.
  - `content` 显示的消息文本

### 函数执行(action)

用于需要让用户选择的场景。

```txt
event: action
\n
data:{id:"chat ID",createdAt:datetime, payload:{ actions:[{funcName:str, params: object }]  }}
\n
\n
```

`data`结构说明：

- `id` 用户对话唯一标识,单次用户对话相同,
- `createdAt` ISO8601 格式日期,每次不同,服务端消息产生时间戳
- `payload` 变化的部分，根据 event 类型的不同而不同.
  - `actions` 执行的函数及参数,按数组顺序执行
    - `funcName` 函数名称
    - `params` 可选，函数参数,一个,`null`、`undefined`或者没有表示没有参数

### 用户确认(confirm)

用于需要让用户确认的场景。

```txt
event: confirm
\n
data:{id:"chat ID",createdAt:datetime, payload:{ conentx:"xxx,确认继续?"}}
\n
\n
```

`data`结构说明：

- `id` 用户对话唯一标识,单次用户对话相同,
- `createdAt` ISO8601 格式日期,每次不同,服务端消息产生时间戳
- `payload` 变化的部分，根据 event 类型的不同而不同.
  - `content` 显示的消息文本

### 用户选择(select)

用于需要让用户选择的场景。

```txt
event: select
\n
data:{id:"chat ID",createdAt:datetime, payload:{ items:[object,object]}}
\n
\n
```
