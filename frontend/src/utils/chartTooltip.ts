export const INDICATOR_EXPLANATIONS: Record<string, string> = {
  'MA': '移动平均线 (Moving Average)。反映一段时间内的平均价格成本。短期线上穿长期线为金叉(看涨)，下穿为死叉(看跌)。',
  'MACD': '平滑异同移动平均线。DIF快线上穿DEA慢线为金叉(买入)，下穿为死叉(卖出)。柱状图代表动能强弱。',
  'RSI': '相对强弱指标 (Relative Strength Index)。>70为超买(可能回调)，<30为超卖(可能反弹)，50为强弱分界。',
  'KDJ': '随机指标。K线上穿D线为金叉(买入)，下穿为死叉(卖出)。J线反应最快，>100超买，<0超卖。',
  'SUPPORT': '支撑位。价格下跌时可能遇到的支撑区域，通常是买入机会。',
  'RESISTANCE': '压力位。价格上涨时可能遇到的阻力区域，通常是卖出机会。'
}

export const formatChartTooltip = (params: any[]) => {
  if (!params || params.length === 0) return ''
  
  const date = params[0].axisValue
  let html = `<div style="font-weight:bold;margin-bottom:5px;">${date}</div>`
  
  // Track which indicators are shown to display their descriptions at the bottom
  const visibleIndicators = new Set<string>()

  params.forEach(param => {
    const { seriesName, value, color, componentType } = param
    if (componentType === 'markLine') return
    
    // Skip if value is empty or invalid
    if (value === undefined || value === null) return

    let displayValue = value
    // Handle K-line data: [open, close, low, high]
    if (Array.isArray(value) && value.length >= 2) {
       // Open, Close, Low, High
       const open = Number(value[0]).toFixed(2)
       const close = Number(value[1]).toFixed(2)
       const low = Number(value[2]).toFixed(2)
       const high = Number(value[3]).toFixed(2)
       const changeVal = Number(value[1]) - Number(value[0])
       const change = changeVal.toFixed(2)
       const changePct = (changeVal / Number(value[0]) * 100).toFixed(2)
       
       html += `
       <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:3px;">
         <span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:${color};margin-right:5px;"></span>
         <span>价格</span>
       </div>
       <div style="padding-left:15px;font-size:12px;line-height:1.5;color:#666;">
         开盘: ${open}<br/>
         收盘: ${close}<br/>
         最高: ${high}<br/>
         最低: ${low}<br/>
         涨跌: <span style="color:${changeVal >= 0 ? '#ef232a' : '#14b143'}">${changeVal >= 0 ? '+' : ''}${change} (${changePct}%)</span>
       </div>
       `
       return
    }

    // Format numbers
    if (typeof value === 'number') {
        displayValue = value.toFixed(2)
    }
    
    html += `
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:3px;">
      <div style="display:flex;align-items:center;">
        <span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:${color};margin-right:5px;"></span>
        <span>${seriesName}</span>
      </div>
      <span style="font-weight:bold;margin-left:15px;">${displayValue}</span>
    </div>
    `

    // Identify indicator type for description
    if (seriesName.includes('MA')) visibleIndicators.add('MA')
    else if (seriesName.includes('MACD') || seriesName === 'DIF' || seriesName === 'DEA') visibleIndicators.add('MACD')
    else if (seriesName.includes('RSI')) visibleIndicators.add('RSI')
    else if (seriesName.includes('K') || seriesName.includes('D') || seriesName.includes('J')) visibleIndicators.add('KDJ')
    else if (seriesName.includes('Support') || seriesName === '支撑位') visibleIndicators.add('SUPPORT')
    else if (seriesName.includes('Resistance') || seriesName === '压力位') visibleIndicators.add('RESISTANCE')
  })

  // Add descriptions footer if there are indicators
  if (visibleIndicators.size > 0) {
      html += `<div style="margin-top:8px;padding-top:8px;border-top:1px solid #eee;font-size:11px;color:#888;max-width:300px;white-space:normal;word-wrap:break-word;">`
      visibleIndicators.forEach(ind => {
          if (INDICATOR_EXPLANATIONS[ind]) {
              html += `<div style="margin-bottom:4px;line-height:1.4;"><strong>${ind}:</strong> ${INDICATOR_EXPLANATIONS[ind]}</div>`
          }
      })
      html += `</div>`
  }
  
  return html
}
