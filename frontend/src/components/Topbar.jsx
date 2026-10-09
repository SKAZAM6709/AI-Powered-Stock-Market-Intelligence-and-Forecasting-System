import {
  Bell,
  Database,
} from "lucide-react";


function Topbar() {
  return (
    <header className="topbar">

      <div>
        <span className="topbar-title">
          AI-Powered Stock Market Intelligence
        </span>
      </div>


      <div className="topbar-actions">

        <div className="api-badge">
          <Database size={16} />
          API Online
        </div>

        <button
          className="icon-button"
          type="button"
        >
          <Bell size={19} />
        </button>

      </div>

    </header>
  );
}


export default Topbar;