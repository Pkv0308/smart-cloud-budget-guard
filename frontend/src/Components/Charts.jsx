import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid,
  ResponsiveContainer,
  Cell,
} from "recharts";

const STATE_COLORS = {
  normal: "#10b981",
  warning: "#f59e0b",
  critical: "#dc2626",
};

export function VmStateChart({ data }) {
  return (
    <div className="chart-card">
      <h3>VMs by state</h3>
      <ResponsiveContainer width="100%" height={220}>
        <BarChart data={data} margin={{ top: 8, right: 16, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" vertical={false} />
          <XAxis dataKey="name" />
          <YAxis allowDecimals={false} />
          <Tooltip />
          <Bar dataKey="count" name="VMs" radius={[4, 4, 0, 0]}>
            {data.map((d) => (
              <Cell key={d.name} fill={d.color} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export function BudgetChart({ data }) {
  return (
    <div className="chart-card">
      <h3>Spend vs limit</h3>
      <ResponsiveContainer width="100%" height={220}>
        <BarChart data={data} margin={{ top: 8, right: 16, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" vertical={false} />
          <XAxis dataKey="project" />
          <YAxis />
          <Tooltip formatter={(v) => `$${Number(v).toFixed(2)}`} />
          <Legend />
          <Bar dataKey="limit" name="Limit" fill="#cbd5e1" radius={[4, 4, 0, 0]} />
          <Bar dataKey="spend" name="Spend" fill="#065a82" radius={[4, 4, 0, 0]}>
            {data.map((d) => (
              <Cell key={d.project} fill={STATE_COLORS[d.state] || "#065a82"} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}