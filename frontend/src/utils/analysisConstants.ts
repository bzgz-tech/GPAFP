export const indicatorDefinitions: Record<string, { title: string; desc: string; type: 'success' | 'warning' | 'info' | 'error' }> = {
  RSI: {
    title: '相对强弱指标 (RSI)',
    desc: 'RSI 通过比较一段时期内的平均收盘涨数和平均收盘跌数来分析市场买卖盘的意向和实力。RSI > 70 通常表示超买（可能下跌），RSI < 30 通常表示超卖（可能上涨）。',
    type: 'warning'
  },
  MACD: {
    title: '平滑异同移动平均线 (MACD)',
    desc: 'MACD 利用收盘价的短期（常用为12日）指数移动平均线与长期（常用为26日）指数移动平均线之间的聚合与分离状况，对买进、卖出时机作出研判。',
    type: 'info'
  },
  MA: {
    title: '移动平均线 (MA)',
    desc: '移动平均线是将某一段时间的收盘价之和除以该周期，从而得到的一条带有趋势性的轨迹。它能消除价格短期波动的干扰，反映价格的长期趋势。',
    type: 'success'
  }
}
