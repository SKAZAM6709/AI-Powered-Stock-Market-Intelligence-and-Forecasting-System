import { NavLink } from "react-router-dom";

import {
  LayoutDashboard,
  Activity,
  Search,
  BrainCircuit,
  Newspaper,
  GitCompareArrows,
  BarChart3,
  Info,
  TrendingUp,
} from "lucide-react";


const menuItems = [
  {
    name: "Dashboard",
    path: "/",
    icon: LayoutDashboard,
  },
  {
    name: "Market Overview",
    path: "/market",
    icon: Activity,
  },
  {
    name: "Stock Explorer",
    path: "/stocks",
    icon: Search,
  },
  {
    name: "AI Forecast",
    path: "/forecast",
    icon: BrainCircuit,
  },
  {
    name: "News Sentiment",
    path: "/sentiment",
    icon: Newspaper,
  },
  {
    name: "Compare Stocks",
    path: "/compare",
    icon: GitCompareArrows,
  },
  {
    name: "Model Analytics",
    path: "/analytics",
    icon: BarChart3,
  },
  {
    name: "About",
    path: "/about",
    icon: Info,
  },
];


function Sidebar() {
  return (
    <aside className="sidebar">

      <div className="sidebar-logo">

        <div className="logo-icon">
          <TrendingUp size={26} />
        </div>

        <div>
          <h2>StockAI</h2>
          <span>Intelligence</span>
        </div>

      </div>


      <nav className="sidebar-menu">

        {menuItems.map((item) => {

          const Icon = item.icon;

          return (
            <NavLink
              key={item.path}
              to={item.path}
              end={item.path === "/"}
              className={({ isActive }) =>
                isActive
                  ? "sidebar-link active"
                  : "sidebar-link"
              }
            >

              <Icon size={20} />

              <span>
                {item.name}
              </span>

            </NavLink>
          );
        })}

      </nav>


      <div className="sidebar-footer">

        <div className="status-dot"></div>

        <div>
          <strong>
            Backend Ready
          </strong>

          <small>
            FastAPI Connected
          </small>
        </div>

      </div>

    </aside>
  );
}


export default Sidebar;