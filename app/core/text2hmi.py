import asyncio
import json
from datetime import datetime


async def create_paper(input: str):
  yield f"event:message\ndata:{
    json.dumps(
      {'content': '准备创建图纸', 'createdAt': f'{datetime.now().isoformat()}'}
    )
  }\n\n"
  await asyncio.sleep(2)
  yield f"event: message\ndata: {
    json.dumps(
      {
        'content': '寻找合适的模版',
        'createdAt': f'{datetime.now().isoformat()}',
        'payload': {},
      }
    )
  }\n\n"
  await asyncio.sleep(2)
  yield f"event: confirm\ndata: {
    json.dumps(
      {
        'content': '需要用户确认使用模版',
        'createdAt': f'{datetime.now().isoformat()}',
      }
    )
  }\n\n"
  await asyncio.sleep(2)
  yield f"event: message\ndata: {
    json.dumps(
      {
        'content': '正在创建图纸',
        'createdAt': f'{datetime.now().isoformat()}',
      }
    )
  }\n\n"
  await asyncio.sleep(2)
  yield f"event: done\ndata: {
    json.dumps(
      {
        'content': '图纸已经创建完成',
        'createdAt': f'{datetime.now().isoformat()}',
      }
    )
  }\n\n"
  # new_describe=template_describe.replace('"',"'")
  # 调用模板选择助手
  # result = chain2.invoke({"input":new_describe})
  # print(result)
  # index=int(float(result))
  # #file_path = "/home/llm-hmi/tagged_displays.json"
  # 给HMI后端发送图纸指令
  # file_path = "C:/Users/xuzhihong/Downloads/tagged_displays.json"
  # with open(file_path, 'r', encoding='utf-8') as file:
  #     json_data = file.read()
  # lines = json.loads(json_data)
  # #url="http://172.28.4.42:8000/editorSvc/test/paste"
  # url="http://172.28.11.85:8000/editorSvc/test/paste"
  # payload = json.dumps({
  #     "destPath":'displays/新建文件夹',
  #     "fileType":'file',
  #     "name":lines[index]['name'],
  #     "projectCode":lines[index]['project_code'],
  #     "resType":"displays",
  #     "srcPath":lines[index]['preview_address']
  #     })
  # headers = {'Content-Type':'application/json'}
  # response = requests.request("POST", url, headers=headers,data=payload)
  # open_data=[]
  # print("payload",payload)
  # if response.status_code ==200:
  # #    print('t8:',datetime.now())
  #     data = response.text
  #     print('data:',data)
  #     #print(type(data))
  #     data = json.loads(data)
  #     #return data
  #     #global open_data
  #     open_data.append(data["data"])
  # format_function={
  #     "type":"function",
  #     "payload":{
  #     "funcName":"__hmi_editor.tabs.openTab",
  #     "params":open_data}}
  # return format_function
