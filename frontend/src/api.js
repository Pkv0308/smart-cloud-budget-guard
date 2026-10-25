const API_BASE = "http://localhost:8000";

async function request(path, options = {}) {
  let res;
  try {
    res = await fetch(`${API_BASE}${path}`, {
      headers: { "Content-Type": "application/json" },
      ...options,
    });
  } catch {
    throw new Error(
      "Cannot reach the backend. Check that the API is running on localhost:8000."
    );
  }

  if (!res.ok) {
    let detail = `${res.status} ${res.statusText}`;
    try {
      const body = await res.json();
      if (typeof body.detail === "string") detail = body.detail;
    } catch {
      // response had no JSON body, keep the status text
    }
    throw new Error(detail);
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
  getRecommendations: () => request("/automation/recommendations"),
  getAutomationLogs: () => request("/automation/logs"),
  runAutomation: (vmName, dryRun = true) =>
    request("/automation/run", {
      method: "POST",
      body: JSON.stringify({ vm_name: vmName, dry_run: dryRun }),
    }),
};