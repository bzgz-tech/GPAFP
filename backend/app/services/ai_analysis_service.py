from abc import ABC, abstractmethod

class AIAnalysisService(ABC):
    @abstractmethod
    def generate_report(self, symbol: str, data: list[dict], indicators: dict) -> str:
        """
        根据市场数据和指标生成分析报告
        
        Args:
            symbol: 交易对名称 (e.g., XAUUSD)
            data: 最近的K线数据列表 (OHLCV)
            indicators: 只有最新一期的技术指标值
            
        Returns:
            str: Markdown 格式的分析报告
        """
        pass
