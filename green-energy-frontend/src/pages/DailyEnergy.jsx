import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

export default function DailyEnergy() {
  const [summary, setSummary] = useState({
    totalKwh: 0,
    estimatedCost: 0,
    peakHour: "--:--",
  });
  const [hourlyUsage, setHourlyUsage] = useState([]);
  const [hours, setHours] = useState([]);
  const [tip, setTip] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      navigate("/login");
      return;
    }

    const fetchDailyEnergy = async () => {
      try {
        setLoading(true);
        setError("");

        const response = await fetch(
          // TODO: change this to real scenario endpoint
          "http://localhost:8000/scenario/run",
          {
            method: "POST", 
            headers: {
              "Content-Type": "application/json",
              Authorization: `Bearer ${token}`,
            },
          }
        );

        if (response.status === 401 || response.status === 403) {
          localStorage.clear();
          navigate("/login");
          return;
        }

        if (!response.ok) {
          throw new Error("Failed to fetch energy data");
        }

        const data = await response.json();
        console.log("Scenario response:", data);

        const curve = data.predicted_usage_curve || [];

        // total kWh = sum of kwh_consumption
        const totalKwh = curve.reduce(
          (sum, point) => sum + (point.kwh_consumption || 0),
          0
        );

        // we’ll show scenario_cost as “Estimated cost”
        const estimatedCost = data.scenario_cost || 0;

        // find highest kwh_consumption point for peak hour
        let peakHour = "--:--";
        if (curve.length > 0) {
          const peakPoint = curve.reduce((max, p) =>
            p.kwh_consumption > max.kwh_consumption ? p : max
          );
          peakHour = new Date(peakPoint.timestamp).toLocaleTimeString(
            "en-GB",
            { hour: "2-digit", minute: "2-digit" }
          );
        }

        const usageArray = curve.map((p) => p.kwh_consumption);
        const hourLabels = curve.map((p) =>
          new Date(p.timestamp).toLocaleTimeString("en-GB", {
            hour: "2-digit",
            minute: "2-digit",
          })
        );

        setSummary({
          totalKwh,
          estimatedCost,
          peakHour,
        });

        setHourlyUsage(usageArray);
        setHours(hourLabels);

        setTip(
          "Peak usage occurs in the evening. Shifting heavy appliances to off-peak hours can lower costs by around 10–15%."
        );
      } catch (err) {
        console.error(err);
        setError("We couldn't load your energy data just now.");
      } finally {
        setLoading(false);
      }
    };

    fetchDailyEnergy();
  }, [navigate]);

  const safeHours =
    hours && hours.length
      ? hours
      : hourlyUsage.map((_, idx) => `${idx}:00`);

  const { peakIndex, lowIndex, maxUsage } = useMemo(() => {
    if (!hourlyUsage.length) {
      return { peakIndex: -1, lowIndex: -1, maxUsage: 0 };
    }

    let maxVal = -Infinity;
    let minVal = Infinity;
    let maxIdx = 0;
    let minIdx = 0;

    hourlyUsage.forEach((v, i) => {
      if (v > maxVal) {
        maxVal = v;
        maxIdx = i;
      }
      if (v < minVal) {
        minVal = v;
        minIdx = i;
      }
    });

    return { peakIndex: maxIdx, lowIndex: minIdx, maxUsage: maxVal };
  }, [hourlyUsage]);

  const points = useMemo(() => {
    if (!hourlyUsage.length || maxUsage <= 0) return "";

    return hourlyUsage
      .map((val, i) => {
        const x = (i / (hourlyUsage.length - 1)) * 100;
        const y = 100 - (val / maxUsage) * 100;
        return `${x},${y}`;
      })
      .join(" ");
  }, [hourlyUsage, maxUsage]);

  function handleViewDevices() {
    navigate("/homeowner/devices"); // change to your real devices route
  }

  if (loading) {
    return <div className="energy-page">Loading your energy data…</div>;
  }

  if (error) {
    return <div className="energy-page">{error}</div>;
  }

  return (
    <div className="energy-page">
      {/* Header */}
      <div className="energy-header-card">
        <div className="energy-header-top">
          <span className="energy-period-pill">Daily</span>
        </div>
        <div className="energy-header-text">
          <p className="energy-hello">Hello Ryan</p>
          <h1 className="energy-title">Energy usage</h1>
        </div>
      </div>

      {/* Summary cards */}
      <div className="energy-summary-row">
        <div className="energy-summary-card">
          <p className="energy-summary-label">Energy usage today</p>
          <p className="energy-summary-value">
            {summary.totalKwh.toFixed(2)} kWh
          </p>
        </div>

        <div className="energy-summary-card">
          <p className="energy-summary-label">Estimated cost</p>
          <p className="energy-summary-value">
            £{summary.estimatedCost.toFixed(2)}
          </p>
        </div>

        <div className="energy-summary-card">
          <p className="energy-summary-label">Peak usage hour</p>
          <p className="energy-summary-value">{summary.peakHour}</p>
        </div>
      </div>

      {/* Toggle buttons */}
      <div className="energy-toggle-row">
        <button className="energy-toggle-btn energy-toggle-btn--active">
          Day
        </button>
        <button className="energy-toggle-btn">Week</button>
        <button className="energy-toggle-btn">Month</button>
      </div>

      {/* Chart */}
      <div className="energy-chart-card">
        {hourlyUsage.length && maxUsage > 0 ? (
          <>
            <svg
              viewBox="0 0 100 100"
              preserveAspectRatio="none"
              className="energy-chart-svg"
            >
              <polyline
                fill="none"
                stroke="#C56BEE"
                strokeWidth="2"
                points={points}
              />

              {hourlyUsage.map((val, i) => {
                const x = (i / (hourlyUsage.length - 1)) * 100;
                const y = 100 - (val / maxUsage) * 100;

                if (i === peakIndex || i === lowIndex) return null;

                return (
                  <circle
                    key={i}
                    cx={x}
                    cy={y}
                    r="1.3"
                    fill="#C56BEE"
                  />
                );
              })}

              {peakIndex >= 0 && (() => {
                const val = hourlyUsage[peakIndex];
                const x = (peakIndex / (hourlyUsage.length - 1)) * 100;
                const y = 100 - (val / maxUsage) * 100;
                return <circle cx={x} cy={y} r="1.7" fill="#E53B38" />;
              })()}

              {lowIndex >= 0 && (() => {
                const val = hourlyUsage[lowIndex];
                const x = (lowIndex / (hourlyUsage.length - 1)) * 100;
                const y = 100 - (val / maxUsage) * 100;
                return <circle cx={x} cy={y} r="1.7" fill="#8ADF5E" />;
              })()}
            </svg>

            <div className="energy-chart-xlabels">
              {safeHours.map((h) => (
                <span key={h}>{h}</span>
              ))}
            </div>
          </>
        ) : (
          <p>No usage data available for today.</p>
        )}
      </div>

      {/* Legend */}
      <div className="energy-legend">
        <div className="energy-legend-item">
          <span className="energy-legend-dot energy-legend-dot--red" />
          <span>Peak usage</span>
        </div>
        <div className="energy-legend-item">
          <span className="energy-legend-dot energy-legend-dot--green" />
          <span>Lowest usage</span>
        </div>
      </div>

      {/* Tip card */}
      <div className="energy-tip-card">
        <h2 className="energy-tip-title">Energy saving suggestions</h2>
        <p className="energy-tip-text">{tip}</p>

        <button
          type="button"
          className="energy-tip-button"
          onClick={handleViewDevices}
        >
          View devices
        </button>
      </div>
    </div>
  );
}