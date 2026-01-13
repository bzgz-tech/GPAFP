from abc import ABC, abstractmethod

class AIAnalysisService(ABC):
    @abstractmethod
    def generate_report(self, symbol: str, data: list[dict], indicators: dict) -> dict:
        """
        根据市场数据和指标生成分析报告
        
        Args:
            symbol: 交易对名称 (e.g., XAUUSD)
            data: 最近的K线数据列表 (OHLCV)
            indicators: 只有最新一期的技术指标值
            
        Returns:
            dict: 包含 'content' (Markdown 报告) 和 'model' (使用的模型名称)
        """
        pass
