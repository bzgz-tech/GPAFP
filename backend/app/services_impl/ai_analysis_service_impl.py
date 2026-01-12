import json
import requests
import pandas as pd
from datetime import datetime
from app.core.config import settings
from app.services.ai_analysis_service import AIAnalysisService

class AIAnalysisServiceImpl(AIAnalysisService):
    USD_CNY_RATE = 7.1
    OZ_TO_GRAM = 31.1034768
    
    def _convert_price(self, price_usd: float) -> float:
        """
        将 USD/oz 转换为 CNY/g
        """
        if price_usd is None:
            return 0.0
        return round(float(price_usd) * self.USD_CNY_RATE / self.OZ_TO_GRAM, 2)

    def generate_report(self, symbol: str, data: list[dict], indicators: dict) -> str:
        """
        生成市场分析报告。
        如果配置了 LLM API Key，则调用大模型；否则使用内置规则引擎生成基础报告。
        """
        if settings.llm_api_key and settings.llm_api_key.strip():
            try:
                return self._call_llm(symbol, data, indicators)
            except Exception as e:
                print(f"LLM调用失败，降级为规则分析: {e}")
                return self._rule_based_analysis(symbol, data, indicators) + "\n\n*(注：AI服务暂时不可用，以上为基础规则分析)*"
        else:
            return self._rule_based_analysis(symbol, data, indicators)

    def _format_data_for_prompt(self, data: list[dict], indicators: dict) -> str:
        # Calculate MA20 for the provided data
        if not data:
            return ""
            
        df = pd.DataFrame(data)
        # Ensure 'close' is float
        df['close'] = df['close'].astype(float)
        
        # Convert close price to CNY/g
        df['close'] = df['close'].apply(lambda x: self._convert_price(x))
        
        df['ma20'] = df['close'].rolling(window=20).mean()
        
        # Take last 20 days for context to allow trend analysis
        recent_df = df.tail(20)
        
        lines = []
        for _, row in recent_df.iterrows():
            ma_str = f"{row['ma20']:.2f}" if pd.notna(row['ma20']) else "N/A"
            ts_str = row['ts']
            lines.append(f"日期: {ts_str}, 收盘: {row['close']}元/克, MA20: {ma_str}元/克")
            
        data_str = "\n".join(lines)
        
        # Convert indicators
        conv_indicators = {}
        for k, v in indicators.items():
            if k in ["MA5", "MA20", "MACD_DIF", "MACD_DEA"]:
                conv_indicators[k] = f"{self._convert_price(v)}元/克"
            else:
                conv_indicators[k] = v
        
        ind_str = "\n".join([f"{k}: {v}" for k, v in conv_indicators.items()])
        
        return f"""
近期行情数据 (含MA20，单位：元/克):
{data_str}

当前最新技术指标 (价格相关指标单位：元/克):
{ind_str}
"""

    def _call_llm(self, symbol, data, indicators) -> str:
        context = self._format_data_for_prompt(data, indicators)
        
        prompt = f"""
你是一位专业的金融市场分析师。请参考以下格式，根据提供的 {symbol} (黄金/人民币，单位：元/克) 市场数据，撰写一份详细的分析报告。

【参考格式】：
一、核心信息
标的：{symbol} (CNY/g)
周期：日 K 线
均线：20 日均线（MA20），代表中期市场平均成本
二、走势阶段拆解
1. 初期（...）：描述趋势启动或关键突破
2. 中期（...）：描述趋势延续情况
3. 近期（...）：描述当前回调或加速情况
三、当前信号与操作参考
趋势判断：...
关键信号：...
操作建议：...
四、注意点
...

【市场数据】：
{context}

要求：
1. 严格按照上述【参考格式】的四个章节进行输出。
2. 结合数据中的 MA20 和收盘价关系进行深入分析（金叉/死叉、支撑/压力）。
3. 语言专业、客观。
4. 字数控制在 400-600 字。
5. 报告中涉及价格的地方，请统一使用“元/克”作为单位。
"""
        
        headers = {
            "Authorization": f"Bearer {settings.llm_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": settings.llm_model,
            "messages": [
                {"role": "system", "content": "You are a helpful financial analyst assistant."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.5
        }
        
        # 兼容 OpenAI 格式的接口
        base_url = settings.llm_base_url.rstrip('/')
        chat_path = settings.llm_chat_path.lstrip('/')
        url = f"{base_url}/{chat_path}"
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        content = result['choices'][0]['message']['content']
        return content

    def _rule_based_analysis(self, symbol, data, indicators) -> str:
        if not data:
            return "数据不足，无法分析。"
            
        last = data[-1]
        close = self._convert_price(float(last['close']))
        prev_close = self._convert_price(float(data[-2]['close'])) if len(data) > 1 else close
        change = close - prev_close
        change_pct = (change / prev_close) * 100
        
        # 趋势判断
        ma5 = self._convert_price(indicators.get('MA5')) if indicators.get('MA5') else None
        ma20 = self._convert_price(indicators.get('MA20')) if indicators.get('MA20') else None
        trend = "震荡"
        if ma5 and ma20:
            if close > ma5 > ma20:
                trend = "上涨"
            elif close < ma5 < ma20:
                trend = "下跌"
                
        # RSI 分析
        rsi = indicators.get('RSI')
        rsi_msg = "处于中性区域"
        if rsi:
            if rsi > 70:
                rsi_msg = "处于**超买**状态，需警惕回调"
            elif rsi < 30:
                rsi_msg = "处于**超卖**状态，可能有反弹需求"
                
        # MACD 分析
        dif = indicators.get('MACD_DIF')
        dea = indicators.get('MACD_DEA')
        macd_msg = "无明显信号"
        if dif and dea:
            if dif > dea:
                macd_msg = "MACD金叉运行，动能偏多"
            else:
                macd_msg = "MACD死叉运行，动能偏空"

        return f"""
### {symbol} 智能分析报告 (基础版)

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

#### 一、核心信息
- **标的**: {symbol} (当前价格 {close}元/克)
- **周期**: 日 K 线
- **均线**: 20 日均线 (MA20: {round(ma20, 2) if ma20 else 'N/A'}元/克)，代表中期市场平均成本

#### 二、走势阶段拆解
1. **近期表现**: 
   价格较前一日{"上涨" if change > 0 else "下跌"} **{abs(change_pct):.2f}%**。
   当前价格位于 MA20 {"上方" if ma20 and close > ma20 else "下方"}，显示中期{"多头" if ma20 and close > ma20 else "空头"}信号。

#### 三、当前信号与操作参考
- **趋势判断**: 当前处于 **{trend}** 阶段。
- **关键指标**:
  - RSI ({round(rsi, 2) if rsi else '-'}): {rsi_msg}。
  - MACD: {macd_msg}。
- **操作建议**:
  {("持有多单：可继续持有，以 20 日均线作为止损线。" if trend == "上涨" else "持有空单：可继续持有，以 20 日均线作为止损线。" if trend == "下跌" else "市场震荡，建议观望，高抛低吸。")}

#### 四、注意点
当前最新价 ({close}) {"仍在" if ma20 and close > ma20 else "处于"} 20 日均线{"上方" if ma20 and close > ma20 else "下方"}。
若后续价格{"跌破" if ma20 and close > ma20 else "突破"} MA20，则需警惕趋势反转。

> *提示：未配置 AI API Key，以上为内置规则生成的分析报告。*
"""
