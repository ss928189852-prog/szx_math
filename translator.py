from googletrans import Translator
import asyncio

async def translate_tw(content):
    async with Translator() as translator:
        result = await translator.translate(content, dest='zh-tw')
        return result.text
async def translate_cn(content):
    async with Translator() as translator:
        result = await translator.translate(content, dest='zh-cn')
        return result.text
async def translate_hk(content):
    async with Translator() as translator:
        result = await translator.translate(content, dest='yue')
        return result.text