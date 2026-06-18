/**
 * SalesChart — Recharts line chart for revenue over time
 */

import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'

const mockData = [
  { day: 'Mon', revenue: 2400 },
  { day: 'Tue', revenue: 1398 },
  { day: 'Wed', revenue: 3800 },
  { day: 'Thu', revenue: 3908 },
  { day: 'Fri', revenue: 4800 },
  { day: 'Sat', revenue: 3800 },
  { day: 'Sun', revenue: 4300 },
]

export default function SalesChart() {
  return (
    <ResponsiveContainer width="100%" height={200}>
      <AreaChart data={mockData}>
        <defs>
          <linearGradient id="colorRevenue" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="var(--tg-theme-accent-text-color, #2481cc)" stopOpacity={0.3} />
            <stop offset="95%" stopColor="var(--tg-theme-accent-text-color, #2481cc)" stopOpacity={0} />
          </linearGradient>
        </defs>
        <XAxis
          dataKey="day"
          axisLine={false}
          tickLine={false}
          tick={{ fill: 'var(--tg-theme-hint-color, #999)', fontSize: 12 }}
        />
        <YAxis hide />
        <Tooltip
          contentStyle={{
            background: 'var(--tg-theme-section-bg-color, #fff)',
            border: 'none',
            borderRadius: '12px',
            boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
          }}
          formatter={(value: number) => [`⭐ ${value}`, 'Revenue']}
        />
        <Area
          type="monotone"
          dataKey="revenue"
          stroke="var(--tg-theme-accent-text-color, #2481cc)"
          strokeWidth={2}
          fillOpacity={1}
          fill="url(#colorRevenue)"
        />
      </AreaChart>
    </ResponsiveContainer>
  )
}
