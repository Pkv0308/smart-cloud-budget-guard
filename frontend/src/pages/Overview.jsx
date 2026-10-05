import { useEffect, useState } from "react";
import { api } from "../api";

function Overview() {
  const [budgets, setBudgets] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    Promise.all([api.getSpendSummary(), api.getAlerts()])
      .then(([spend, alertList]) => {
        setBudgets(spend);
        setAlerts(alertList);
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p>Loading overview...</p>;
  if (error) return <p>Failed to load overview: {error}</p>;

  const active = alerts.filter((a) => !a.acknowledged);
  const stats = [
    { label: "Active alerts", value: active.length, tone: "" },
    {
      label: "Critical",
      value: active.filter((a) => a.severity === "critical").length,
      tone: "critical",
    },
    {
      label: "Warning",
      value: active.filter((a) => a.severity === "warning").length,
      tone: "warning",
    },
    { label: "Acknowledged", value: alerts.length - active.length, tone: "" },
  ];

  return (
    <>
      <h2 className="section-title">Alerts</h2>
      <div className="stat-grid">
        {stats.map((s) => (
          <div className={`stat-card ${s.tone}`} key={s.label}>
            <div className="value">{s.value}</div>
            <div className="label">{s.label}</div>
          </div>
        ))}
      </div>

      <h2 className="section-title">Budgets</h2>
      {budgets.length === 0 ? (
        <p className="muted">No budgets yet. Create one with POST /budgets/.</p>
      ) : (
        <div className="budget-list">
          {budgets.map((b) => {
            const pct =
              b.monthly_limit > 0
                ? Math.min(100, (b.current_spend / b.monthly_limit) * 100)
                : 0;
            return (
              <div className="budget-card" key={b.budget_id}>
                <div className="budget-head">
                  <strong>{b.project}</strong>
                  <span className={`badge ${b.state}`}>{b.state}</span>
                </div>
                <div className="bar">
                  <div
                    className={`bar-fill ${b.state}`}
                    style={{ width: `${pct}%` }}
                  />
                </div>
                <div className="muted">
                  ${b.current_spend.toFixed(2)} of ${b.monthly_limit.toFixed(2)}{" "}
                  ({pct.toFixed(0)}%)
                </div>
              </div>
            );
          })}
        </div>
      )}
    </>
  );
}

export default Overview;