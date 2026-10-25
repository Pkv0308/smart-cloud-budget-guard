import { api } from "../api";
import { useLoader } from "../hooks/useLoader";
import { Loading, ErrorBox } from "../Components/Status";
import { VmStateChart, BudgetChart } from "../components/Charts";

const fetchOverview = () =>
  Promise.all([
    api.getSpendSummary(),
    api.getAlerts(),
    api.getInventory(),
    api.getIdleVms(),
  ]).then(([budgets, alerts, vms, idle]) => ({
    budgets,
    alerts,
    vms,
    idleNames: new Set(idle.idle_vms),
  }));
function Overview() {
  const { data, loading, error, retry } = useLoader(fetchOverview);

  if (loading) return <Loading label="Loading overview..." />;
  if (error) return <ErrorBox message={error} onRetry={retry} />;

  const { budgets, alerts, vms, idleNames } = data;

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

  const isRunning = (vm) => vm.power_state?.toLowerCase().includes("running");
  const idleCount = vms.filter((v) => idleNames.has(v.vm_name)).length;
  const activeCount = vms.filter(
    (v) => isRunning(v) && !idleNames.has(v.vm_name)
  ).length;
  const vmChartData = [
    { name: "Active", count: activeCount, color: "#10b981" },
    { name: "Idle", count: idleCount, color: "#f59e0b" },
    { name: "Not running", count: vms.length - idleCount - activeCount, color: "#9ca3af" },
  ];

  const budgetChartData = budgets.map((b) => ({
    project: b.project,
    spend: b.current_spend,
    limit: b.monthly_limit,
    state: b.state,
  }));

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

      <div className="chart-grid">
        <VmStateChart data={vmChartData} />
        {budgets.length > 0 && <BudgetChart data={budgetChartData} />}
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