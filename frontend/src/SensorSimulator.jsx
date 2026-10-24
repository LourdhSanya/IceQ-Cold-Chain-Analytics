
import { useEffect, useMemo, useState } from "react";
import {
  Activity, AlertTriangle, Bell, Check, CheckCircle2, ChevronDown,
  CircleHelp, Clock3, Droplet, FileText, Gauge, Home, Info,
  Leaf, LogOut, Menu, Radio, Settings, ShieldCheck, Snowflake,
  Thermometer, TrendingUp, Waves, X
} from "lucide-react";
import {
  CartesianGrid, Line, LineChart, ResponsiveContainer,
  Tooltip, XAxis, YAxis
} from "recharts";
import "./SensorSimulator.css";

const STORAGE_KEY = "iceq-simulator-readings-v1";

const categories = {
  Dairy: { threshold: 5, unit: "UNIT_001", color: "#22d3ee", icon: "dairy" },
  Produce: { threshold: 8, unit: "UNIT_002", color: "#10b981", icon: "produce" },
  Frozen: { threshold: -15, unit: "UNIT_003", color: "#8b5cf6", icon: "frozen" }
};

const initialReadings = [
  { id: 1, time: "11:45 AM", unit: "UNIT_001", food: "Dairy", temperature: 9, humidity: 70, status: "Critical", threshold: 5 },
  { id: 2, time: "11:42 AM", unit: "UNIT_001", food: "Dairy", temperature: 4.2, humidity: 66, status: "Normal", threshold: 5 },
  { id: 3, time: "11:39 AM", unit: "UNIT_002", food: "Produce", temperature: 7.5, humidity: 72, status: "Normal", threshold: 8 },
  { id: 4, time: "11:36 AM", unit: "UNIT_003", food: "Frozen", temperature: -16.8, humidity: 58, status: "Normal", threshold: -15 },
  { id: 5, time: "11:33 AM", unit: "UNIT_002", food: "Produce", temperature: 8.6, humidity: 75, status: "Warning", threshold: 8 }
];

function getStatus(temperature, threshold) {
  const exceeds = temperature > threshold;

  if (!exceeds) return "Normal";

  const difference = temperature - threshold;
  return difference >= 3 ? "Critical" : "Warning";
}

function getRecommendations(reading) {
  if (reading.status === "Normal") {
    return [
      "Continue monitoring temperature readings.",
      "Review the trend for sudden changes.",
      "Maintain routine checks of the cooling system.",
      "Confirm that storage conditions match the product requirements."
    ];
  }

  return [
    "Verify the reading and inspect the storage unit.",
    "Check the cooling system, power supply and door seals.",
    "Record how long the temperature has exceeded the configured limit.",
    "Follow the applicable food-safety procedure before releasing goods."
  ];
}

function loadReadings() {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    return saved ? JSON.parse(saved) : initialReadings;
  } catch {
    return initialReadings;
  }
}

function formatTime(value) {
  return new Date(value).toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit"
  });
}

function CategoryIcon({ category, size = 20 }) {
  if (category === "Dairy") return <Droplet size={size} />;
  if (category === "Produce") return <Leaf size={size} />;
  return <Snowflake size={size} />;
}

function StatusBadge({ status }) {
  const className = status.toLowerCase();

  return (
    <span className={`sim-status sim-status-${className}`}>
      <span className="sim-status-dot" />
      {status}
    </span>
  );
}

function SidebarLink({ icon: Icon, children, active = false, onClick }) {
  return (
    <button
      className={`sim-side-link ${active ? "active" : ""}`}
      onClick={onClick}
      type="button"
    >
      <Icon size={20} />
      <span>{children}</span>
    </button>
  );
}

export default function SensorSimulator() {
  const [food, setFood] = useState("Dairy");
  const [unit, setUnit] = useState("UNIT_001");
  const [temperature, setTemperature] = useState("9.0");
  const [humidity, setHumidity] = useState("70");
  const [readings, setReadings] = useState(loadReadings);
  const [selectedReading, setSelectedReading] = useState(null);
  const [message, setMessage] = useState("");
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const config = categories[food];

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(readings));
    } catch {
      setMessage("Browser storage is unavailable. Your history may not persist.");
    }
  }, [readings]);

  const latest = selectedReading || readings[0];

  const stats = useMemo(() => ({
    total: readings.length,
    critical: readings.filter((r) => r.status === "Critical").length,
    warning: readings.filter((r) => r.status === "Warning").length,
    normal: readings.filter((r) => r.status === "Normal").length
  }), [readings]);

  const chartData = useMemo(() => {
    return [...readings]
      .filter((r) => r.food === food)
      .slice(0, 12)
      .reverse()
      .map((r) => ({
        time: r.time,
        temperature: r.temperature,
        threshold: r.threshold
      }));
  }, [readings, food]);

  function handleCategoryChange(nextFood) {
    setFood(nextFood);
    setUnit(categories[nextFood].unit);
    setSelectedReading(null);
    setMessage("");
  }

  function analyzeReading(event) {
    event.preventDefault();

    const temp = Number(temperature);
    const hum = Number(humidity);

    if (temperature.trim() === "" || !Number.isFinite(temp)) {
      setMessage("Enter a valid temperature.");
      return;
    }

    if (humidity.trim() === "" || !Number.isFinite(hum) || hum < 0 || hum > 100) {
      setMessage("Humidity must be between 0 and 100%.");
      return;
    }

    const newReading = {
      id: `${Date.now()}-${Math.random().toString(16).slice(2)}`,
      time: formatTime(new Date()),
      timestamp: new Date().toISOString(),
      unit,
      food,
      temperature: temp,
      humidity: hum,
      threshold: config.threshold,
      status: getStatus(temp, config.threshold),
      source: "Simulated manual input"
    };

    setReadings((previous) => [newReading, ...previous].slice(0, 100));
    setSelectedReading(newReading);
    setMessage(`Reading analyzed successfully for ${unit}.`);
  }

  function triggerExcursion() {
    const targetTemperature = config.threshold + 4;
    setTemperature(String(targetTemperature));
    setMessage("Demo excursion prepared. Click Analyze Reading to record it.");
  }

  function resetDemo() {
    setReadings(initialReadings);
    setSelectedReading(null);
    setFood("Dairy");
    setUnit("UNIT_001");
    setTemperature("9.0");
    setHumidity("70");
    setMessage("Demo history reset to the illustrative sample readings.");
  }

  function goTo(path) {
    window.location.href = path;
  }

  const recommendations = latest ? getRecommendations(latest) : [];

  return (
    <div className="sim-app">
      <header className="sim-topbar">
        <button
          type="button"
          className="sim-mobile-menu"
          onClick={() => setSidebarOpen(!sidebarOpen)}
          aria-label="Toggle navigation"
        >
          <Menu size={22} />
        </button>

        <button className="sim-brand" onClick={() => goTo("/")} type="button">
          <span className="sim-logo"><span>Q</span></span>
          <span className="sim-brand-copy">
            <strong>ICEQ</strong>
            <small>Predictive Cooling. Absolute Control.</small>
          </span>
        </button>

        <div className="sim-top-actions">
          <span className="sim-top-demo"><Radio size={15} /> SIMULATION MODE</span>
          <button className="sim-icon-button" type="button" title="Notifications">
            <Bell size={19} />
            <span className="sim-notification-dot" />
          </button>
          <div className="sim-user">
            <span className="sim-avatar">LS</span>
            <span>Lourdh Sanya</span>
            <ChevronDown size={15} />
          </div>
        </div>
      </header>

      <div className="sim-layout">
        <aside className={`sim-sidebar ${sidebarOpen ? "sim-sidebar-open" : ""}`}>
          <nav className="sim-nav">
            <SidebarLink icon={Home} onClick={() => goTo("/dashboard")}>Dashboard</SidebarLink>
            <SidebarLink icon={Gauge} onClick={() => goTo("/dashboard")}>Units</SidebarLink>
            <SidebarLink icon={AlertTriangle} onClick={() => goTo("/dashboard")}>Incidents</SidebarLink>
            <SidebarLink icon={FileText} onClick={() => goTo("/dashboard")}>Reports</SidebarLink>
            <SidebarLink icon={Settings} onClick={() => setMessage("Settings are not part of this simulator page yet.")}>Settings</SidebarLink>
            <SidebarLink icon={Radio} active onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}>Sensor Simulator</SidebarLink>
            <SidebarLink icon={LogOut} onClick={() => goTo("/")}>Exit</SidebarLink>
          </nav>

          <div className="sim-sidebar-bottom">
            <Snowflake size={32} />
            <strong>Keep it Fresh<br />Keep it Safe</strong>
            <small>IceQ – Cold Chain Monitoring & Predictive Analytics</small>
          </div>
        </aside>

        <main className="sim-main">
          <section className="sim-page-banner">
            <div className="sim-banner-icon"><Radio size={29} /></div>
            <div className="sim-banner-copy">
              <h1>Sensor Simulator &amp; Risk Advisor</h1>
              <p>Enter sensor readings to simulate conditions, get risk analysis, preventive actions and track reading history.</p>
            </div>
            <div className="sim-banner-mode">
              <span><Radio size={14} /> SIMULATION MODE</span>
              <small>Not live sensor data <CircleHelp size={12} /></small>
            </div>
          </section>

          <div className="sim-main-grid">
            <div className="sim-left-column">
              <section className="sim-panel sim-input-panel">
                <div className="sim-section-title">
                  <span className="sim-step-number">1</span>
                  <h2>Enter a simulated sensor reading</h2>
                </div>

                <form onSubmit={analyzeReading}>
                  <label className="sim-label">Food Category</label>
                  <div className="sim-category-grid">
                    {Object.entries(categories).map(([name, item]) => (
                      <button
                        type="button"
                        key={name}
                        className={`sim-category-card ${food === name ? "selected" : ""}`}
                        onClick={() => handleCategoryChange(name)}
                      >
                        <CategoryIcon category={name} size={23} />
                        <strong>{name}</strong>
                        <small>Threshold: {item.threshold}°C</small>
                      </button>
                    ))}
                  </div>

                  <label className="sim-label" htmlFor="sim-unit">Storage Unit</label>
                  <div className="sim-select-wrap">
                    <Gauge size={18} />
                    <select
                      id="sim-unit"
                      value={unit}
                      onChange={(event) => setUnit(event.target.value)}
                    >
                      <option value="UNIT_001">UNIT_001</option>
                      <option value="UNIT_002">UNIT_002</option>
                      <option value="UNIT_003">UNIT_003</option>
                    </select>
                    <ChevronDown size={16} />
                  </div>

                  <div className="sim-field-grid">
                    <div>
                      <label className="sim-label" htmlFor="sim-temperature">Temperature (°C)</label>
                      <div className="sim-input-wrap">
                        <Thermometer size={18} />
                        <input
                          id="sim-temperature"
                          type="number"
                          step="0.1"
                          value={temperature}
                          onChange={(event) => setTemperature(event.target.value)}
                          required
                        />
                      </div>
                      <small className="sim-field-hint">e.g. 9.0</small>
                    </div>
                    <div>
                      <label className="sim-label" htmlFor="sim-humidity">Humidity (%)</label>
                      <div className="sim-input-wrap">
                        <Droplet size={18} />
                        <input
                          id="sim-humidity"
                          type="number"
                          min="0"
                          max="100"
                          step="0.1"
                          value={humidity}
                          onChange={(event) => setHumidity(event.target.value)}
                          required
                        />
                      </div>
                      <small className="sim-field-hint">e.g. 70</small>
                    </div>
                  </div>

                  <button className="sim-primary-button" type="submit">
                    <Activity size={18} /> Analyze Reading
                  </button>

                  <button className="sim-secondary-button" type="button" onClick={triggerExcursion}>
                    <AlertTriangle size={17} /> Prepare Excursion Demo
                  </button>

                  {message && (
                    <div className="sim-message" role="status">
                      <Info size={16} /> {message}
                    </div>
                  )}
                </form>
              </section>

              <section className="sim-panel sim-history-panel">
                <div className="sim-panel-heading">
                  <h2><Clock3 size={18} /> Live Reading History</h2>
                  <button type="button" onClick={() => setMessage("Showing the most recent readings saved in this browser.")}>View All</button>
                </div>
                <div className="sim-table-scroll">
                  <table className="sim-table">
                    <thead>
                      <tr>
                        <th>Time</th>
                        <th>Unit</th>
                        <th>Food</th>
                        <th>Temp. °C</th>
                        <th>Humidity</th>
                        <th>Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {readings.slice(0, 5).map((r) => (
                        <tr
                          key={r.id}
                          className={selectedReading?.id === r.id ? "sim-row-selected" : ""}
                          onClick={() => setSelectedReading(r)}
                          title="Click to inspect this reading"
                        >
                          <td>{r.time}</td>
                          <td>{r.unit}</td>
                          <td>{r.food}</td>
                          <td>{Number(r.temperature).toFixed(1)}</td>
                          <td>{Number(r.humidity).toFixed(1)}%</td>
                          <td><StatusBadge status={r.status} /></td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                <div className="sim-history-footer">
                  <span>{readings.length} readings in this browser</span>
                  <button type="button" onClick={resetDemo}>Reset Demo</button>
                </div>
              </section>
            </div>

            <div className="sim-right-column">
              <section className="sim-panel sim-risk-panel">
                <div className="sim-section-title">
                  <span className="sim-step-number">2</span>
                  <h2>Risk Assessment</h2>
                </div>

                {latest ? (
                  <>
                    <div className={`sim-risk-banner sim-risk-${latest.status.toLowerCase()}`}>
                      {latest.status === "Normal" ? <CheckCircle2 size={28} /> : <AlertTriangle size={28} />}
                      <div>
                        <strong>{latest.status === "Critical" ? "High Risk" : latest.status === "Warning" ? "Warning" : "Within Configured Threshold"}</strong>
                        <span>
                          {latest.status === "Normal"
                            ? "Temperature is within the configured threshold"
                            : "Temperature is above the configured threshold"}
                        </span>
                      </div>
                    </div>

                    <div className="sim-reading-details">
                      <div className="sim-detail-row">
                        <span className="sim-detail-icon"><CategoryIcon category={latest.food} /></span>
                        <div><small>Food Category</small><strong>{latest.food}</strong></div>
                      </div>
                      <div className="sim-detail-row">
                        <span className="sim-detail-icon"><Gauge size={20} /></span>
                        <div><small>Storage Unit</small><strong>{latest.unit}</strong></div>
                      </div>
                      <div className="sim-detail-row">
                        <span className="sim-detail-icon"><Thermometer size={20} /></span>
                        <div>
                          <small>Temperature</small>
                          <strong>{Number(latest.temperature).toFixed(1)}°C</strong>
                          <small>Configured threshold: {latest.threshold}°C</small>
                        </div>
                      </div>
                      <div className="sim-detail-row">
                        <span className="sim-detail-icon"><Droplet size={20} /></span>
                        <div><small>Humidity</small><strong>{Number(latest.humidity).toFixed(1)}%</strong></div>
                      </div>
                      <div className="sim-detail-row">
                        <span className="sim-detail-icon"><Clock3 size={20} /></span>
                        <div><small>Recorded at</small><strong>{latest.time}</strong><small>Simulated input</small></div>
                      </div>
                    </div>
                  </>
                ) : (
                  <p>No reading selected.</p>
                )}
              </section>

              <section className="sim-panel sim-reference-panel">
                <h2><CircleHelp size={19} /> Quick Reference</h2>
                <h3>Configured Temperature Thresholds</h3>
                {Object.entries(categories).map(([name, item]) => (
                  <div className="sim-reference-row" key={name}>
                    <span className="sim-reference-name">
                      <i style={{ background: item.color }} />
                      {name}
                    </span>
                    <strong>{item.threshold}°C</strong>
                  </div>
                ))}
                <div className="sim-reference-divider" />
                <h3>Risk Levels</h3>
                <div className="sim-reference-row"><span className="sim-reference-name"><i className="dot-normal" />Normal</span><small>Within threshold</small></div>
                <div className="sim-reference-row"><span className="sim-reference-name"><i className="dot-warning" />Warning</span><small>Up to 3°C above</small></div>
                <div className="sim-reference-row"><span className="sim-reference-name"><i className="dot-critical" />Critical</span><small>3°C or more above</small></div>
              </section>

              <section className="sim-panel sim-actions-panel">
                <h2><ShieldCheck size={20} /> Recommended Actions</h2>
                <ul>
                  {recommendations.map((item, index) => (
                    <li key={index}><Check size={15} /><span>{item}</span></li>
                  ))}
                </ul>
              </section>

              <section className="sim-disclaimer">
                <Info size={22} />
                <p>This page uses simulated input and a simple threshold rule. It does not establish actual food spoilage or prove food safety.</p>
              </section>
            </div>
          </div>

          <div className="sim-bottom-grid">
            <section className="sim-panel sim-chart-panel">
              <div className="sim-panel-heading">
                <h2><TrendingUp size={18} /> Temperature Trend</h2>
                <span className="sim-chart-legend"><i style={{ background: config.color }} />{food}</span>
              </div>
              <p className="sim-chart-subtitle">Recent recorded readings for {food}</p>
              {chartData.length > 0 ? (
                <div className="sim-chart">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={chartData} margin={{ top: 10, right: 14, left: -15, bottom: 4 }}>
                      <CartesianGrid stroke="#183b5a" strokeDasharray="3 3" />
                      <XAxis dataKey="time" tick={{ fill: "#9dbbd5", fontSize: 10 }} axisLine={{ stroke: "#254967" }} tickLine={false} />
                      <YAxis tick={{ fill: "#9dbbd5", fontSize: 10 }} axisLine={false} tickLine={false} />
                      <Tooltip contentStyle={{ background: "#071d33", border: "1px solid #155078", borderRadius: 8, color: "#e0f2fe" }} />
                      <Line type="monotone" dataKey="temperature" name="Temperature °C" stroke={config.color} strokeWidth={2.5} dot={{ r: 3 }} activeDot={{ r: 5 }} />
                      <Line type="monotone" dataKey="threshold" name="Threshold °C" stroke="#f59e0b" strokeDasharray="5 4" dot={false} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              ) : (
                <div className="sim-empty">Analyze a reading to start the trend.</div>
              )}
            </section>

            <section className="sim-panel sim-alerts-panel">
              <div className="sim-panel-heading">
                <h2><Bell size={18} /> Recent Alerts</h2>
                <span className="sim-alert-count">{stats.critical + stats.warning} flagged</span>
              </div>
              <div className="sim-alert-summary">
                <div><span className="dot-critical" /><strong>{stats.critical}</strong><small>Critical</small></div>
                <div><span className="dot-warning" /><strong>{stats.warning}</strong><small>Warning</small></div>
                <div><span className="dot-normal" /><strong>{stats.normal}</strong><small>Normal</small></div>
              </div>
              <div className="sim-alert-list">
                {readings.filter((r) => r.status !== "Normal").slice(0, 4).map((r) => (
                  <button className="sim-alert-item" type="button" key={r.id} onClick={() => setSelectedReading(r)}>
                    <span className={`sim-alert-marker ${r.status.toLowerCase()}`} />
                    <span className="sim-alert-copy">
                      <strong>{r.unit} · {r.food}</strong>
                      <small>Temperature {Number(r.temperature).toFixed(1)}°C · Threshold {r.threshold}°C</small>
                      <small>{r.time}</small>
                    </span>
                    <StatusBadge status={r.status} />
                  </button>
                ))}
                {readings.every((r) => r.status === "Normal") && (
                  <div className="sim-empty">No warning or critical readings recorded.</div>
                )}
              </div>
            </section>
          </div>

          <footer className="sim-footer">
            <span>ICEQ · Cold-Chain Monitoring &amp; Predictive Analytics</span>
            <span><Waves size={14} /> Software simulation · Not connected to physical sensors</span>
          </footer>
        </main>
      </div>
    </div>
  );
}
