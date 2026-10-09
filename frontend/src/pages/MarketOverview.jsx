import {
  useEffect,
  useState,
} from "react";

import api from "../api/api";

import Loading from "../components/Loading";
import ErrorMessage from "../components/ErrorMessage";


function MarketOverview() {

  const [data, setData] =
    useState(null);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");


  useEffect(() => {

    const loadMarket = async () => {

      try {

        const response = await api.get(
          "/market/overview?limit=10"
        );

        setData(
          response.data
        );

      } catch (err) {

        console.error(err);

        setError(
          "Unable to load market overview."
        );

      } finally {

        setLoading(false);

      }

    };

    loadMarket();

  }, []);


  if (loading) {
    return (
      <Loading
        text="Loading market..."
      />
    );
  }


  if (error) {
    return (
      <ErrorMessage
        message={error}
      />
    );
  }


  return (
    <div>

      <div className="page-header">

        <div>

          <h1>
            Market Overview
          </h1>

          <p>
            View the strongest gainers,
            losers, and most active stocks.
          </p>

        </div>

      </div>


      <div className="three-column-grid">

        <MarketTable
          title="Top Gainers"
          data={data?.top_gainers}
          mode="change"
        />

        <MarketTable
          title="Top Losers"
          data={data?.top_losers}
          mode="change"
        />

        <MarketTable
          title="Most Active"
          data={data?.most_active}
          mode="volume"
        />

      </div>

    </div>
  );
}


function MarketTable({
  title,
  data = [],
  mode,
}) {

  return (
    <div className="card">

      <h3 className="section-title">
        {title}
      </h3>


      <div className="table-wrapper">

        <table>

          <thead>

            <tr>

              <th>
                Ticker
              </th>

              <th>
                Close
              </th>

              <th>
                {mode === "volume"
                  ? "Volume"
                  : "Change"}
              </th>

            </tr>

          </thead>


          <tbody>

            {data.map(
              (stock, index) => (
                <tr
                  key={
                    stock.ticker ||
                    stock.Name ||
                    index
                  }
                >

                  <td>
                    {stock.ticker ||
                      stock.Name}
                  </td>

                  <td>
                    ${stock.close}
                  </td>

                  <td>
                    {mode === "volume"
                      ? stock.volume
                      : `${stock.change_pct}%`
                    }
                  </td>

                </tr>
              )
            )}

          </tbody>

        </table>

      </div>

    </div>
  );
}


export default MarketOverview;