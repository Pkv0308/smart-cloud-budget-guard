import { useState } from "react";
import { api } from "../api";
import { useLoader } from "../hooks/useLoader";
import { Loading, ErrorBox } from "../Components/Status";

const fetchAutomation = () =>
  Promise.all([api.getRecommendations(), api.getAutomationLogs()]).then(
    ([recs, logs]) => ({ recs, logs })
  );

function resultClass(result) {
  if (result === "success") return "normal";
  if (result === "skipped") return "warning";
  return "critical";
}

function statusClass(status) {
  if (status === "pending") return "warning";
  if (status === "executed") return "normal";
  return "stopped";
}

function Automation() {
  
  const [busy, setBusy] = useState(null);
  const [notice, setNotice] = useState(null);
  const { data, loading, error, retry, setData } = useLoader(fetchAutomation);

  async function refresh() {
    setData(await fetchAutomation());
  }
  

  async function handleRecommend() {
    setBusy("recommend");
    setNotice(null);
    try {
      const res = await api.recommend();
      const created = res.filter((x) => x.status === "recommended").length;
      setNotice(
        created > 0
          ? `${created} new recommendation(s) created.`
          : "No new recommendations. Either nothing is idle or recommendations are already pending."
      );
      await refresh();
    } catch (err) {
      setNotice(`Could not generate recommendations: ${err.message}`);
    } finally {
      setBusy(null);
    }
  }

  async function handleDryRun(vmName) {
    setBusy(vmName);
    setNotice(null);
    try {
      const res = await api.runAutomation(vmName, true);
      setNotice(`${vmName}: ${res.result} - ${res.detail}`);
      await refresh();
    } catch (err) {
      setNotice(`Dry run failed for ${vmName}: ${err.message}`);
    } finally {
      setBusy(null);
    }
  }

  if (loading) return <Loading label="Loading automation data..." />;
  if (error) return <ErrorBox message={error} onRetry={retry} />;

const { recs, logs } = data;

  return (
    <>
      <div className="toolbar">
        <h2 className="section-title">Recommendations</h2>
        <button
          className="btn"
          disabled={busy === "recommend"}
          onClick={handleRecommend}
        >
          {busy === "recommend" ? "Checking..." : "Generate recommendations"}
        </button>
      </div>

      {notice && <div className="notice">{notice}</div>}

      {recs.length === 0 ? (
        <p className="muted">No recommendations yet.</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>VM</th>
              <th>Reason</th>
              <th>Status</th>
              <th>Created</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {recs.map((r) => (
              <tr key={r.id}>
                <td>{r.vm_name}</td>
                <td>{r.reason}</td>
                <td>
                  <span className={`badge ${statusClass(r.status)}`}>
                    {r.status}
                  </span>
                </td>
                <td className="muted">
                  {r.created_at ? new Date(r.created_at).toLocaleString() : "-"}
                </td>
                <td>
                  {r.status === "pending" && (
                    <button
                      className="btn"
                      disabled={busy === r.vm_name}
                      onClick={() => handleDryRun(r.vm_name)}
                    >
                      {busy === r.vm_name ? "Running..." : "Dry run"}
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      <h2 className="section-title spaced">Automation log</h2>
      {logs.length === 0 ? (
        <p className="muted">No automation activity yet.</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Time</th>
              <th>VM</th>
              <th>Action</th>
              <th>Mode</th>
              <th>Result</th>
              <th>Detail</th>
            </tr>
          </thead>
          <tbody>
            {logs.slice(0, 20).map((l) => (
              <tr key={l.id}>
                <td className="muted">
                  {l.created_at ? new Date(l.created_at).toLocaleString() : "-"}
                </td>
                <td>{l.vm_name}</td>
                <td>{l.action}</td>
                <td>
                  <span className={`badge ${l.dry_run ? "stopped" : "critical"}`}>
                    {l.dry_run ? "Dry run" : "Live"}
                  </span>
                </td>
                <td>
                  <span className={`badge ${resultClass(l.result)}`}>
                    {l.result}
                  </span>
                </td>
                <td>{l.detail}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
      {logs.length > 20 && (
        <p className="muted">Showing the latest 20 of {logs.length} entries.</p>
      )}
    </>
  );
}

export default Automation;