import httpx
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
import random

@register("quark_search", "AstrBot", "夸克网盘资源搜索插件", "1.0")
class QuarkSearchPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.api_base_url = "http://112.74.56.8:5000"
        self.http_client = httpx.AsyncClient(timeout=30.0)
        self.max_results = 5
        
    async def initialize(self):
        logger.info("夸克网盘搜索插件已启动")
    
    async def api_request(self, endpoint: str, params: dict):
        try:
            url = f"{self.api_base_url}{endpoint}"
            # logger.debug(f"API请求: {url}, 参数: {params}")
            response = await self.http_client.get(
                url,
                params=params
            )
            response.raise_for_status()
            json_response = response.json()
            # logger.debug(f"API响应: {json_response}")
            return json_response
        except Exception as e:
            logger.error(f"API请求失败: {str(e)}")
            return []

    def format_results(self, results, platform_name=""):
        if not results:
            return "未找到资源，减少关键词或换个关键词尝试。"
            
        results = results[:self.max_results]
        formatted = ""
        for result in results:
            title = result.get('original_title', '未知标题')
            url = result.get('url', '#')
            if platform_name == 'qq_official' or platform_name == 'qq_official_webhook':
                url = self.safe_link(url)
            formatted += f"{title}\n{url}\n"
            formatted += f"--------------------\n"
        
        if platform_name == 'qq_official' or platform_name == 'qq_official_webhook':
            formatted += f"\n由于平台限制,请删除所有✨/⭐/🌀/⚡类符号再访问\n\n"
        formatted += "欢迎观看！如果喜欢可以喊你的朋友一起来哦"
        return formatted
    
    def safe_link(self, url):
        symbols = ["✨","🌀","⚡","⭐","🔷"]
        return url.replace("://", f"{random.choice(symbols)}://"
                ).replace(".", f".{random.choice(symbols)}")

    @filter.command("搜索")
    async def search(self, event: AstrMessageEvent,keyword: str):
        '''说明: /搜索 关键词 '''
        if not keyword:
            yield event.plain_result("请输入要搜索的关键词")
            return
        try:
            results = await self.api_request("/api/search", {"q": keyword, "n": 5})
            platform_name = event.get_platform_name()
            response = self.format_results(results, platform_name)
            yield event.plain_result(response)
        except Exception as e:
            logger.error(f"搜索处理失败: {str(e)}")
            yield event.plain_result("搜索处理出错，请稍后重试")

    @filter.command("热门资源")
    async def hot_resources(self, event: AstrMessageEvent):
        '''说明: 热门资源 '''
        try:
            results = await self.api_request("/api/hot", {"n": 5})
            platform_name = event.get_platform_name()
            response = self.format_results(results,platform_name)
            yield event.plain_result(response)
        except Exception as e:
            logger.error(f"热门资源处理失败: {str(e)}")
            yield event.plain_result("热门资源处理出错，请稍后重试")

    @filter.command("随机资源")
    async def random_resources(self, event: AstrMessageEvent):
        '''说明: 随机资源 '''
        try:
            results = await self.api_request("/api/random", {"n": 5})
            platform_name = event.get_platform_name()
            response = self.format_results(results,platform_name)
            yield event.plain_result(response)
        except Exception as e:
            logger.error(f"随机资源处理失败: {str(e)}")
            yield event.plain_result("随机资源处理出错，请稍后重试")

    async def terminate(self):
        await self.http_client.aclose()
        logger.info("夸克网盘搜索插件已关闭")
