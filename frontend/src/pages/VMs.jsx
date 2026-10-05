import { useEffect, useMemo, useState } from "react";
import { api } from "../api";

function powerClass(state) {
  return state && state.toLowerCase().includes("running") ? "running" : "stopped";
}

function autoShutdownOn(vm) {
  return String(vm.tags?.AutoShutdown ?? "").toLowerCase() === "true";
}

function VMs() {
  const [vms, setVms] = useState([]);
  const [idleNames, setIdleNames] = useState(new Set());
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [envFilter, setEnvFilter] = useState("all");
  const [shutdownFilter, setShutdownFilter] = useState("all");
  const [idleFilter, setIdleFilter] = useState("all");

  useEffect(() => {
    Promise.all([api.getInventory(), api.getIdleVms()])
      .then(([inventory, idle]) => {
        setVms(inventory);
        setIdleNames(new Set(idle.idle_vms));
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  const environments = useMemo(
    () => [...new Set(vms.map((v) => v.environment))].sort(),
    [vms]
  );

  if (loading) return <p>Loading VMs...</p>;
  if (error) return <p>Failed to load VMs: {error}</p>;
  if (vms.length === 0)
    return <p className="muted">No VMs in inventory. Run a sync to populate it.</p>;

  const filtered = vms.filter((vm) => {
    if (envFilter !== "all" && vm.environment !== envFilter) return false;
    if (shutdownFilter === "on" && !autoShutdownOn(vm)) return false;
    if (shutdownFilter === "off" && autoShutdownOn(vm)) return false;
    const isIdle = idleNames.has(vm.vm_name);
    if (idleFilter === "idle" && !isIdle) return false;
    if (idleFilter === "active" && isIdle) return false;
    return true;
  });

  return (
    <>
      <div className="filters">
        <label>
          Environment
          <select value={envFilter} onChange={(e) => setEnvFilter(e.target.value)}>
            <option value="all">All</option>
            {environments.map((env) => (
              <option key={env} value={env}>{env}</option>
            ))}
          </select>
        </label>

        <label>
          Auto-shutdown
          <select
            value={shutdownFilter}
            onChange={(e) => setShutdownFilter(e.target.value)}
          >
            <option value="all">All</option>
            <option value="on">Enabled</option>
            <option value="off">Not enabled</option>
          </select>
        </label>

        <label>
          Idle state
          <select value={idleFilter} onChange={(e) => setIdleFilter(e.target.value)}>
            <option value="all">All</option>
            <option value="idle">Idle</option>
            <option value="active">Not idle</option>
          </select>
        </label>
      </div>

      {filtered.length === 0 ? (
        <p className="muted">No VMs match the current filters.</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Power state</th>
              <th>Idle</th>
              <th>Location</th>
              <th>Project</th>
              <th>Environment</th>
              <th>Tags</th>
              <th>Last synced</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((vm) => (
              <tr key={vm.vm_name}>
                <td>{vm.vm_name}</td>
                <td>
                  <span className={`badge ${powerClass(vm.power_state)}`}>
                    {vm.power_state}
                  </span>
                </td>
                <td>
                  {idleNames.has(vm.vm_name) ? (
                    <span className="badge idle">Idle</span>
                  ) : (
                    <span className="muted">-</span>
                  )}
                </td>
                <td>{vm.location}</td>
                <td>{vm.project}</td>
                <td>{vm.environment}</td>
                <td>
                  {Object.entries(vm.tags || {}).map(([k, v]) => (
                    <span className="tag" key={k}>
                      {k}: {v}
                    </span>
                  ))}
                </td>
                <td className="muted">
                  {vm.last_synced_at
                    ? new Date(vm.last_synced_at).toLocaleString()
                    : "-"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </>
  );
}

export default VMs;