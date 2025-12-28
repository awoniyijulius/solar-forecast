import React, { useRef } from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

interface HourlyChartProps {
  hours: string[];
  predictions: number[];
  confidence: number[];
  co2Data: number[];
}

const HourlyChart: React.FC<HourlyChartProps> = ({ hours, predictions, confidence, co2Data }) => {
  const chartRef = useRef<any>(null);

  const data = {
    labels: hours.map(h => {
      // Input format: "2024-12-28T12:00:00"
      const timePart = h.includes('T') ? h.split('T')[1].substring(0, 5) : h;
      return timePart;
    }),
    datasets: [
      {
        label: 'Solar Forecast (Mean)',
        data: predictions,
        borderColor: '#22c55e',
        backgroundColor: (context: any) => {
          const ctx = context.chart.ctx;
          const gradient = ctx.createLinearGradient(0, 0, 0, 400);
          gradient.addColorStop(0, 'rgba(34, 197, 94, 0.4)');
          gradient.addColorStop(1, 'rgba(34, 197, 94, 0)');
          return gradient;
        },
        fill: true,
        tension: 0.4,
        pointRadius: 0,
        pointHoverRadius: 6,
        borderWidth: 3,
        zIndex: 10
      },
      {
        label: 'Confidence Upper Bound',
        data: predictions.map((p, i) => p + (confidence[i] || 0)),
        borderColor: 'rgba(34, 197, 94, 0.1)',
        backgroundColor: 'rgba(34, 197, 94, 0.15)', // Increased opacity
        fill: '+1',
        pointRadius: 0,
        borderWidth: 0,
        tension: 0.4,
      },
      {
        label: 'Confidence Lower Bound',
        data: predictions.map((p, i) => Math.max(0, p - (confidence[i] || 0))),
        borderColor: 'rgba(34, 197, 94, 0.1)',
        fill: false,
        pointRadius: 0,
        borderWidth: 0,
        tension: 0.4,
      }
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: '#0f172a',
        padding: 16,
        cornerRadius: 12,
        titleFont: { size: 14, weight: 'bold' as const },
        bodyFont: { size: 12 },
        borderColor: 'rgba(255,255,255,0.1)',
        borderWidth: 1,
        // Only show the Mean prediction and custom info in the tooltip to avoid confusion
        filter: (item: any) => item.datasetIndex === 0,
        callbacks: {
          label: (context: any) => [` ⚡ Predicted: ${context.parsed.y.toFixed(2)} kWh`],
          afterLabel: (context: any) => {
            const idx = context.dataIndex;
            const upper = (predictions[idx] + confidence[idx]).toFixed(2);
            const lower = Math.max(0, predictions[idx] - confidence[idx]).toFixed(2);
            return [
              ` 📉 Stability Range: ${lower} - ${upper} kWh`,
              ` 🌿 CO₂ Offset: ${co2Data[idx].toFixed(3)} kg`
            ];
          }
        }
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        grid: { color: 'rgba(255, 255, 255, 0.03)', drawBorder: false },
        ticks: { color: '#64748b' }
      },
      x: {
        grid: { display: false },
        ticks: { color: '#64748b', maxTicksLimit: 12 }
      }
    },
    interaction: { intersect: false, mode: 'index' as const },
  };

  return (
    <div className="h-[420px]">
      <Line data={data} options={options} ref={chartRef} />
    </div>
  );
};

export default HourlyChart;
