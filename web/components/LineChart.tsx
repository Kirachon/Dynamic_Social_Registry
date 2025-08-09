'use client'

import { Line } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend)

export default function LineChart({ labels, seriesLabel, data }:{ labels:string[]; seriesLabel:string; data:number[] }) {
  const dataset = {
    labels,
    datasets: [
      {
        label: seriesLabel,
        data,
        borderColor: 'rgb(37, 99, 235)',
        backgroundColor: 'rgba(37, 99, 235, 0.2)',
        tension: 0.2,
      },
    ],
  }
  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { position: 'top' as const },
      title: { display: false },
    },
    scales: {
      y: { beginAtZero: true },
    },
  }
  return (
    <div style={{height: 240}}>
      <Line data={dataset} options={options} />
    </div>
  )
}

