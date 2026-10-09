import {
  Routes,
  Route,
} from "react-router-dom";

import Sidebar from "./components/Sidebar";
import Topbar from "./components/Topbar";

import Dashboard from "./pages/Dashboard";
import MarketOverview from "./pages/MarketOverview";
import StockExplorer from "./pages/StockExplorer";
import AIForecast from "./pages/AIForecast";
import NewsSentiment from "./pages/NewsSentiment";
import CompareStocks from "./pages/CompareStocks";
import ModelAnalytics from "./pages/ModelAnalytics";
import About from "./pages/About";


function App() {
  return (
    <div className="app-layout">

      <Sidebar />


      <div className="content-area">

        <Topbar />


        <main className="main-content">

          <Routes>

            <Route
              path="/"
              element={<Dashboard />}
            />

            <Route
              path="/market"
              element={<MarketOverview />}
            />

            <Route
              path="/stocks"
              element={<StockExplorer />}
            />

            <Route
              path="/forecast"
              element={<AIForecast />}
            />

            <Route
              path="/sentiment"
              element={<NewsSentiment />}
            />

            <Route
              path="/compare"
              element={<CompareStocks />}
            />

            <Route
              path="/analytics"
              element={<ModelAnalytics />}
            />

            <Route
              path="/about"
              element={<About />}
            />

          </Routes>

        </main>

      </div>

    </div>
  );
}


export default App;