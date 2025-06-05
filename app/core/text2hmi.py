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
