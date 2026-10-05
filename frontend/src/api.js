const API_BASE = "http://localhost:8000";

async function request(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    throw new Error(`${res.status} ${res.statusText}`);
  }
  return res.json();
}

export const api = {
  // health
  getHealth: () => request("/health"),

  // vms
  getInventory: () => request("/vms/inventory"),
  getIdleVms: () => request("/vms/idle"),
  syncVms: () => request("/vms/sync", { method: "POST" }),

  // budgets
  getBudgets: () => request("/budgets/"),
  getSpendSummary: () => request("/budgets/spend"),

  // alerts
  getAlerts: (acknowledged) =>
    request(
      acknowledged === undefined
        ? "/alerts/"
        : `/alerts/?acknowledged=${acknowledged}`
    ),
  acknowledgeAlert: (id) =>
    request(`/alerts/${id}/acknowledge`, { method: "POST" }),

  // automation
  recommend: () => request("/automation/recommend", { method: "POST" }),
  getAutomationLogs: () => request("/automation/logs"),
  runAutomation: (vmName, dryRun = true) =>
    request("/automation/run", {
      method: "POST",
      body: JSON.stringify({ vm_name: vmName, dry_run: dryRun }),
    }),
};