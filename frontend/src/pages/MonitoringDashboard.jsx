
import {
  Activity,
  Bell,
  ChevronRight,
  ClipboardList,
  LayoutDashboard,
  LogOut,
  Package,
  Settings,
  ShieldCheck,
  Snowflake,
  Thermometer,
  Truck,
} from "lucide-react";
import {
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
} from "recharts";
import "./MonitoringDashboard.css";

const units = [
  { id: "UNIT_001", name: "Dairy", temperature: 4.43, limit: 5, icon: "milk" },
  { id: "UNIT_002", name: "Produce", temperature: 5.25, limit: 8, icon: "produce" },
  { id: "UNIT_003", name: "Frozen", temperature: -17.67, limit: -15, icon: "frozen" },
];

const incidents = [
  { time: "2026-10-21 16:00", unit: "UNIT_002", type: "Produce", status: "CRITICAL" },
  { time: "2026-10-21 11:00", unit: "UNIT_003", type: "Frozen", status: "CRITICAL" },
  { time: "2026-10-21 10:00", unit: "UNIT_001", type: "Dairy", status: "WARNING" },
  { time: "2026-10-20 17:00", unit: "UNIT_002", type: "Produce", status: "WARNING" },
];

const incidentData = [
  { name: "UNIT_001", incidents: 3, color: "#38bdf8" },
  { name: "UNIT_002", incidents: 2, color: "#0284c7" },
  { name: "UNIT_003", incidents: 2, color: "#818cf8" },
];

function Sidebar() {
  const links = [
    { name: "Dashboard", icon: LayoutDashboard, active: true },
    { name: "Units", icon: Package },
    { name: "Incidents", icon: Bell },
    { name: "Reports", icon: ClipboardList },
    { name: "Settings", icon: Settings },
  ];

  return (
    <aside className="monitor-sidebar">
      <a className="monitor-brand" href="/">
        <span className="monitor-brand-icon"><Snowflake size={22} /></span>
        <span>ICEQ<small>Cold Chain Control</small></span>
      </a>

      <p className="sidebar-label">WORKSPACE</p>
      <nav className="monitor-nav">
        {links.map(({ name, icon: Icon, active }) => (
          <a
            key={name}
            href={name === "Dashboard" ? "#overview" : `#${name.toLowerCase()}`}
            className={active ? "monitor-nav-link active" : "monitor-nav-link"}
          >
            <Icon size={18} />
            {name}
            {active && <ChevronRight className="nav-chevron" size={15} />}
          </a>
        ))}
      </nav>

      <div className="sidebar-bottom">
        <div className="sidebar-demo-note">
          <ShieldCheck size={18} />
          <span>Demo environment<small>Simulated sensor data</small></span>
        </div>
        <a href="/" className="monitor-logout">
          <LogOut size={17} /> Back to website
        </a>
      </div>
    </aside>
  );
}

function TemperatureTrend() {
  const chartData = Array.from({ length: 12 }, (_, i) => ({
    time: `${String(i * 2).padStart(2, "0")}:00`,
    Dairy: 4 + Math.sin(i * 1.4) * 0.7,
    Produce: 6 + Math.cos(i * 1.1) * 0.8,
    Frozen: -18 + Math.sin(i * 1.3) * 0.7,
  }));

  const points = (key, min, max) =>
    chartData.map((d, i) => {
      const x = (i / (chartData.length - 1)) * 100;
      const y = 100 - ((d[key] - min) / (max - min)) * 100;
      return `${x},${y}`;
    }).join(" ");

  return (
    <div className="trend-visual">
      <div className="trend-y-labels"><span>10°C</span><span>0°C</span><span>-20°C</span></div>
      <svg viewBox="0 0 100 100" preserveAspectRatio="none" role="img" aria-label="Illustrative temperature trends">
        {[10, 50, 90].map((y) => (
          <line key={y} x1="0" y1={y} x2="100" y2={y} stroke="#16466b" strokeDasharray="2 2" vectorEffect="non-scaling-stroke" />
        ))}
        <polyline points={points("Dairy", -20, 10)} fill="none" stroke="#38bdf8" strokeWidth="1.5" vectorEffect="non-scaling-stroke" />
        <polyline points={points("Produce", -20, 10)} fill="none" stroke="#2dd4bf" strokeWidth="1.5" vectorEffect="non-scaling-stroke" />
        <polyline points={points("Frozen", -20, 10)} fill="none" stroke="#818cf8" strokeWidth="1.5" vectorEffect="non-scaling-stroke" />
      </svg>
      <div className="trend-x-labels"><span>00:00</span><span>06:00</span><span>12:00</span><span>18:00</span><span>24:00</span></div>
    </div>
  );
}

function UnitCards() {
  return (
    <div className="monitor-unit-list">
      {units.map((unit) => {
        const isRisk = unit.icon === "frozen"
          ? unit.temperature > unit.limit
          : unit.temperature > unit.limit;

        return (
          <article className="monitor-unit" key={unit.id}>
            <div className="monitor-unit-icon"><Thermometer size={20} /></div>
            <div className="monitor-unit-info">
              <strong>{unit.id}</strong>
              <span>{unit.name}</span>
              <small>Limit: {unit.limit}°C</small>
            </div>
            <div className="monitor-unit-reading">
              <strong>{unit.temperature.toFixed(2)}°C</strong>
              <span className={isRisk ? "risk-pill" : "safe-pill"}>
                {isRisk ? "Above limit" : "Normal"}
              </span>
            </div>
          </article>
        );
      })}
    </div>
  );
}

export default function MonitoringDashboard() {
  return (
    <div className="monitor-app" id="overview">
      <Sidebar />

      <main className="monitor-main">
        <header className="monitor-header">
          <div>
            <span className="monitor-overline">ICEQ CONTROL CENTER</span>
            <h1>Monitoring Dashboard</h1>
            <p>Monitor conditions, review incidents, and investigate risk signals.</p>
          </div>
          <div className="monitor-header-actions">
            <span className="demo-tag">● SIMULATED DATA</span>
            <div className="monitor-avatar">D</div>
            <span>Demo User</span>
          </div>
        </header>

        <div className="monitor-banner">
          <Activity size={17} />
          <span>This is a demonstration using simulated readings, not a live sensor feed.</span>
        </div>

        <section className="monitor-metrics">
          <article className="monitor-metric">
            <span><Package size={18} /> Total Units</span>
            <strong>3</strong>
            <small>Configured demo units</small>
          </article>
          <article className="monitor-metric">
            <span><Bell size={18} /> Example Incidents</span>
            <strong>7</strong>
            <small>Illustrative incident records</small>
          </article>
          <article className="monitor-metric">
            <span><Truck size={18} /> Units Monitored</span>
            <strong>3 / 3</strong>
            <small>Simulated data available</small>
          </article>
          <article className="monitor-metric">
            <span><ShieldCheck size={18} /> Platform Status</span>
            <strong className="healthy-text">Demo</strong>
            <small>Interface operational</small>
          </article>
        </section>

        <section className="monitor-grid">
          <article className="monitor-panel">
            <div className="monitor-panel-heading">
              <div><h2>Cold Chain Units</h2><p>Latest illustrative readings</p></div>
              <span className="panel-count">03 UNITS</span>
            </div>
            <UnitCards />
          </article>

          <article className="monitor-panel">
            <div className="monitor-panel-heading">
              <div><h2>Temperature Trend</h2><p>Illustrative 24-hour pattern</p></div>
              <span className="panel-count">24 HOURS</span>
            </div>
            <div className="trend-legend">
              <span><i className="legend-dairy" /> Dairy</span>
              <span><i className="legend-produce" /> Produce</span>
              <span><i className="legend-frozen" /> Frozen</span>
            </div>
            <TemperatureTrend />
          </article>
        </section>

        <section className="monitor-grid monitor-lower-grid">
          <article className="monitor-panel">
            <div className="monitor-panel-heading">
              <div><h2>Recent Incidents</h2><p>Example records for the demo</p></div>
              <a href="#incidents">View all <ChevronRight size={15} /></a>
            </div>
            <div className="incident-table-wrap">
              <table className="incident-table">
                <thead>
                  <tr><th>Time</th><th>Unit</th><th>Type</th><th>Status</th></tr>
                </thead>
                <tbody>
                  {incidents.map((item, i) => (
                    <tr key={`${item.unit}-${i}`}>
                      <td>{item.time}</td>
                      <td>{item.unit}</td>
                      <td>{item.type}</td>
                      <td><span className={item.status === "CRITICAL" ? "incident-critical" : "incident-warning"}>{item.status}</span></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </article>

          <article className="monitor-panel incident-chart-panel">
            <div className="monitor-panel-heading">
              <div><h2>Incidents by Unit</h2><p>Illustrative distribution</p></div>
            </div>
            <div className="incident-donut-wrap">
              <div className="incident-donut">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={incidentData}
                      dataKey="incidents"
                      nameKey="name"
                      innerRadius="64%"
                      outerRadius="88%"
                      paddingAngle={4}
                      stroke="none"
                    >
                      {incidentData.map((entry) => (
                        <Cell key={entry.name} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip
                      contentStyle={{ background: "#071c32", border: "1px solid #16466b", borderRadius: 8, color: "#e0f2fe" }}
                    />
                  </PieChart>
                </ResponsiveContainer>
                <div className="donut-center"><strong>7</strong><span>Demo incidents</span></div>
              </div>
              <div className="incident-legend">
                {incidentData.map((item) => (
                  <div key={item.name}>
                    <span><i style={{ background: item.color }} />{item.name}</span>
                    <strong>{item.incidents}</strong>
                  </div>
                ))}
              </div>
            </div>
          </article>
        </section>

        <footer className="monitor-footer">
          <span>ICEQ · Predictive Cooling. Absolute Control.</span>
          <span>Demo interface · No physical sensors connected</span>
        </footer>
      </main>
    </div>
  );
}
