import { useState } from "react";
import Overview from "./pages/Overview";
import VMs from "./pages/VMs";
import Alerts from "./pages/Alerts";
import Automation from "./pages/Automation";

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
        {tab === "Alerts" && <Alerts />}
        {tab === "Automation" && <Automation />}
      </main>
    </>
  );
}

export default App;
