import json
import requests
import pandas as pd
from datetime import datetime
from app.core.config import settings
from app.services.ai_analysis_service import AIAnalysisService
from app.services_impl.system_setting_service_impl import SystemSettingServiceImpl

class AIAnalysisServiceImpl(AIAnalysisService):
    USD_CNY_RATE = 7.1
    OZ_TO_GRAM = 31.1034768
    
    def __init__(self):
        self.settings_service = SystemSettingServiceImpl()
    
    def _convert_price(self, price_usd: float) -> float:
        """
        将 USD/oz 转换为 CNY/g
        """
        if price_usd is None:
            return 0.0
        return round(float(price_usd) * self.USD_CNY_RATE / self.OZ_TO_GRAM, 2)

    def _get_data_range(self, data: list[dict]) -> tuple[str, str]:
        if not data:
            return "N/A", "N/A"
        start = data[0].get('ts', 'N/A')
        end = data[-1].get('ts', 'N/A')
        return start, end

    def generate_report(self, symbol: str, data: list[dict], indicators: dict) -> dict:
        """
        生成市场分析报告。
        如果配置了 LLM API Key，则调用大模型；否则使用内置规则引擎生成基础报告。
        """
        ai_config = self.settings_service.get_ai_config()
        api_key = ai_config.get('ai_api_key') or settings.llm_api_key
        
        if api_key and api_key.strip():
            try:
                return self._call_llm(symbol, data, indicators, ai_config)
            except Exception as e:
                print(f"LLM调用失败，降级为规则分析: {e}")
                report = self._rule_based_analysis(symbol, data, indicators) + "\n\n*(注：AI服务暂时不可用，以上为基础规则分析)*"
                return {"content": report, "model": "Rule Engine (Fallback)"}
        else:
            report = self._rule_based_analysis(symbol, data, indicators)
            return {"content": report, "model": "Rule Engine"}

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

    def _call_llm(self, symbol, data, indicators, ai_config=None) -> dict:
        if ai_config is None:
            ai_config = self.settings_service.get_ai_config()
            
        api_key = ai_config.get('ai_api_key') or settings.llm_api_key
        model = ai_config.get('ai_model') or settings.llm_model
        
        start_date, end_date = self._get_data_range(data)
        context = self._format_data_for_prompt(data, indicators)
        
        prompt = f"""
你是一位专业的金融市场分析师。请根据提供的 {symbol} (HJ/人民币，单位：元/克) 市场数据，撰写一份结构清晰、重点突出的分析报告。

【参考格式】：
### 📊 市场分析报告：{symbol} (CNY/g)
**分析周期**：日 K 线 | **数据范围**：{start_date} 至 {end_date} | **基准均线**：MA20 (中期成本)

#### 1. 核心观点
- **趋势判断**：[上涨/下跌/震荡]
- **关键价位**：支撑位 [xxx]，压力位 [xxx]

#### 2. 走势阶段拆解
- **初期 (启动)**：...
- **中期 (延续)**：...
- **近期 (现状)**：...

#### 3. 技术信号解读
- **均线系统**：... (结合 MA20 分析多空力度)
- **辅助指标**：... (RSI/MACD 等)

#### 4. 操作建议 💡
- **策略**：...
- **风控**：...

#### 5. 风险提示 ⚠️
...

【市场数据】：
{context}

要求：
1. **严格遵循上述 Markdown 格式**，使用二级标题(###)和三级标题(####)。
2. **增强可读性**：关键数字（如价格、涨跌幅）请使用 **加粗** 显示。
3. **数据准确**：结合数据中的 MA20 和收盘价关系进行深入分析。
4. **单位统一**：所有价格均使用“元/克”。
5. **字数控制**：400-600 字，语言专业且简练。
"""
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": "You are a helpful financial analyst assistant."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.5
        }
        
        # 兼容 OpenAI 格式的接口
        base_url_config = ai_config.get('ai_base_url') or settings.llm_base_url
        base_url = base_url_config.rstrip('/')
        chat_path_config = ai_config.get('ai_chat_path') or settings.llm_chat_path
        chat_path = chat_path_config.lstrip('/')
        url = f"{base_url}/{chat_path}"
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        content = result['choices'][0]['message']['content']
        return {"content": content, "model": model}

    def _rule_based_analysis(self, symbol, data, indicators) -> str:
        if not data:
            return "数据不足，无法分析。"
            
        start_date, end_date = self._get_data_range(data)
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
### 📊 {symbol} 智能分析报告 (基础版)

**生成时间**：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**数据范围**：{start_date} 至 {end_date}

#### 1. 核心信息
- **标的**: {symbol}
- **当前价格**: **{close}** 元/克
- **MA20均线**: **{round(ma20, 2) if ma20 else 'N/A'}** 元/克

#### 2. 走势阶段拆解
- **近期表现**: 
  价格较前一日{"上涨" if change > 0 else "下跌"} **{abs(change_pct):.2f}%**。
  当前价格位于 MA20 {"上方" if ma20 and close > ma20 else "下方"}，显示中期{"多头" if ma20 and close > ma20 else "空头"}信号。

#### 3. 当前信号与操作参考
- **趋势判断**: 当前处于 **{trend}** 阶段。
- **关键指标**:
  - RSI ({round(rsi, 2) if rsi else '-'}): {rsi_msg}。
  - MACD: {macd_msg}。
- **操作建议 💡**:
  {("持有多单：可继续持有，以 20 日均线作为止损线。" if trend == "上涨" else "持有空单：可继续持有，以 20 日均线作为止损线。" if trend == "下跌" else "市场震荡，建议观望，高抛低吸。")}

#### 4. 风险提示 ⚠️
当前最新价 (**{close}**) {"仍在" if ma20 and close > ma20 else "处于"} 20 日均线{"上方" if ma20 and close > ma20 else "下方"}。
若后续价格{"跌破" if ma20 and close > ma20 else "突破"} MA20，则需警惕趋势反转。

> *提示：未配置 AI API Key，以上为内置规则生成的分析报告。*
"""
