import { useState } from "react";
import Overview from "./pages/Overview";
import VMs from "./pages/VMs";

const TABS = ["Overview", "VMs", "Alerts", "Automation"];

function App() {
  const [tab, setTab] = useState("Overview");

  return (
    <>
      <header className="app-header">
        <h1>Smart Budget Guard</h1>
        <nav className="nav">
          {TABS.map((t) => (
            <button
              key={t}
              className={tab === t ? "active" : ""}
              onClick={() => setTab(t)}
            >
              {t}
            </button>
          ))}
        </nav>
      </header>

      <main className="page">
        {tab === "Overview" && <Overview />}
        {tab === "VMs" && <VMs />}
        {(tab === "Alerts" || tab === "Automation") && (
          <p className="muted">{tab} page coming soon.</p>
        )}
      </main>
    </>
  );
}

export default App;