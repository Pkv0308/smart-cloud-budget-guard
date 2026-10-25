import { useState } from "react";
import { api } from "../api";
import { useLoader } from "../hooks/useLoader";
import { Loading, ErrorBox } from "../Components/Status";

const TYPE_LABELS = {
  idle_vm: "Idle VM",
  budget_breach: "Budget breach",
};

function Alerts() {
  const { data: alerts, loading, error, retry, setData: setAlerts } = useLoader(api.getAlerts);
  const [view, setView] = useState("active");
  const [busyId, setBusyId] = useState(null);
  const [actionError, setActionError] = useState(null);

  async function handleAcknowledge(id) {
    setBusyId(id);
    setActionError(null);
    try {
      await api.acknowledgeAlert(id);
      setAlerts((prev) =>
        prev.map((a) => (a.id === id ? { ...a, acknowledged: true } : a))
      );
    } catch (err) {
      setActionError(`Could not acknowledge alert ${id}: ${err.message}`);
    } finally {
      setBusyId(null);
    }
  }

  if (loading) return <Loading label="Loading alerts..." />;
  if (error) return <ErrorBox message={error} onRetry={retry} />;

  const counts = {
    active: alerts.filter((a) => !a.acknowledged).length,
    acknowledged: alerts.filter((a) => a.acknowledged).length,
    all: alerts.length,
  };

  const visible = alerts.filter((a) => {
    if (view === "active") return !a.acknowledged;
    if (view === "acknowledged") return a.acknowledged;
    return true;
  });

  return (
    <>
      <div className="view-toggle">
        {["active", "acknowledged", "all"].map((v) => (
          <button
            key={v}
            className={view === v ? "active" : ""}
            onClick={() => setView(v)}
          >
            {v.charAt(0).toUpperCase() + v.slice(1)} ({counts[v]})
          </button>
        ))}
      </div>

      {actionError && <p className="error-text">{actionError}</p>}

      {visible.length === 0 ? (
        <p className="muted">No {view === "all" ? "" : view} alerts.</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Severity</th>
              <th>Type</th>
              <th>Subject</th>
              <th>Message</th>
              <th>Created</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {visible.map((a) => (
              <tr key={a.id}>
                <td>
                  <span className={`badge ${a.severity}`}>{a.severity}</span>
                </td>
                <td>{TYPE_LABELS[a.alert_type] || a.alert_type}</td>
                <td>
                  {a.alert_type === "idle_vm"
                    ? a.vm_name
                    : `Budget #${a.budget_id}`}
                </td>
                <td>{a.message}</td>
                <td className="muted">
                  {a.created_at ? new Date(a.created_at).toLocaleString() : "-"}
                </td>
                <td>
                  {a.acknowledged ? (
                    <span className="muted">Acknowledged</span>
                  ) : (
                    <button
                      className="btn"
                      disabled={busyId === a.id}
                      onClick={() => handleAcknowledge(a.id)}
                    >
                      {busyId === a.id ? "Saving..." : "Acknowledge"}
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </>
  );
}

export default Alerts;