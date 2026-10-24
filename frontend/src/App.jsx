
import { useState } from "react";
import { Routes, Route } from "react-router-dom";
import Login from "./Login.jsx";
import Signup from "./Signup.jsx";
import SensorSimulator from "./SensorSimulator";
import MonitoringDashboard from "./MonitoringDashboard.jsx";
import {
  ArrowRight,
  Play,
  ShieldCheck,
  Thermometer,
  Truck,
  Package,
  FlaskConical,
  Activity,
  BellRing,
  FileText,
  Menu,
  X,
  Snowflake,
  Leaf,
  Milk,
} from "lucide-react";

import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from "recharts";
import "./App.css";
import iceqLogo from "./assets/iceq-logo.png";

const solutions = [
  {
    icon: Thermometer,
    title: "Cold Storage Facilities",
    description: "Keep temperature-sensitive inventory under continuous watch.",
  },
  {
    icon: Truck,
    title: "Food Distribution",
    description: "Monitor cold-chain conditions throughout distribution.",
  },
  {
    icon: Package,
    title: "Refrigerated Logistics",
    description: "Gain visibility across temperature-controlled deliveries.",
  },
  {
    icon: Milk,
    title: "Dairy & Beverages",
    description: "Track configured temperature limits for dairy products.",
  },
  {
    icon: Leaf,
    title: "Fresh Produce",
    description: "Monitor environmental conditions for fresh products.",
  },
  {
    icon: FlaskConical,
    title: "Pharmaceuticals",
    description: "Support monitoring workflows for sensitive inventory.",
  },
];

const challenges = [
  {
    icon: Thermometer,
    title: "Hidden temperature excursions",
    description: "Small deviations can go unnoticed and reduce shelf life.",
  },
  {
    icon: Activity,
    title: "Late spoilage detection",
    description: "Teams need earlier visibility into changing conditions.",
  },
  {
    icon: FileText,
    title: "Manual compliance records",
    description: "Scattered records make reviews and audits harder.",
  },
  {
    icon: ShieldCheck,
    title: "Avoidable food waste",
    description: "Better monitoring can help teams investigate losses.",
  },
];

const capabilities = [
  {
    icon: Activity,
    title: "Real-time monitoring",
    description: "Review temperature, humidity, and unit status in one place.",
  },
  {
    icon: ShieldCheck,
    title: "Predictive risk engine",
    description: "Analyse threshold excursions and sustained temperature risks.",
  },
  {
    icon: BellRing,
    title: "Instant alerts",
    description: "Surface warning and critical conditions for review.",
  },
  {
    icon: FileText,
    title: "Compliance reports",
    description: "Review incident history and recorded temperature excursions.",
  },
];

const demoUnits = [
  { id: "UNIT_001", type: "Dairy", temp: "4.43°C", status: "Normal" },
  { id: "UNIT_002", type: "Produce", temp: "5.25°C", status: "Normal" },
  { id: "UNIT_003", type: "Frozen", temp: "-17.67°C", status: "Normal" },
];

// Illustrative counts for the visual prototype, not live API results.
const demoIncidents = [
  { id: "UNIT_001", type: "Dairy", count: 3 },
  { id: "UNIT_002", type: "Produce", count: 2 },
  { id: "UNIT_003", type: "Frozen", count: 2 },
];

function Header() {
  const [menuOpen, setMenuOpen] = useState(false);
  const closeMenu = () => setMenuOpen(false);

  return (
    <header className="site-header">
      <a className="brand" href="#home" onClick={closeMenu}>
        <img src={iceqLogo} alt="IceQ — Predictive Cooling. Absolute Control." />
      </a>

      <button
        className="mobile-menu-button"
        aria-label={menuOpen ? "Close navigation" : "Open navigation"}
        aria-expanded={menuOpen}
        onClick={() => setMenuOpen(!menuOpen)}
      >
        {menuOpen ? <X /> : <Menu />}
      </button>

      <nav className={menuOpen ? "main-nav is-open" : "main-nav"}>
        <a href="#home" onClick={closeMenu}>Home</a>
        <a href="#platform" onClick={closeMenu}>Platform</a>
        <a href="#solutions" onClick={closeMenu}>Solutions</a>
        <a href="#about" onClick={closeMenu}>About</a>
        <a href="#contact" onClick={closeMenu}>Contact</a>
        <a href="/login" onClick={closeMenu}>Login</a>
        <a
          className="button button-primary nav-cta"
          href="#contact"
          onClick={closeMenu}
        >
          Request a Demo <ArrowRight size={16} />
        </a>
      </nav>
    </header>
  );
}

function Hero() {
  return (
    <section className="hero" id="home">
      <div className="hero-content">
        <p className="eyebrow">AI-POWERED COLD-CHAIN MONITORING</p>

        <h1>
          Protect Every Degree.
          <span>Preserve Every Delivery.</span>
        </h1>

        <p className="hero-description">
          IceQ is a cold-chain monitoring platform designed to help teams
          understand temperature excursions, monitor storage conditions, and
          investigate risk across temperature-sensitive logistics.
        </p>

        <p className="hero-supporting">
          Built for dairy, produce, meat, seafood, pharmaceuticals, and
          temperature-sensitive supply chains.
        </p>

        <div className="hero-actions">
          <a className="button button-primary" href="#contact">
            Request a Demo <ArrowRight size={17} />
          </a>
          <a className="button button-outline" href="#how-it-works">
            <Play size={15} /> See How It Works
          </a>
        </div>

        <div className="hero-proof">
          <ShieldCheck size={17} />
          <span>Designed for visibility, traceability, and informed action</span>
        </div>
      </div>

      <div className="hero-visual" aria-label="IceQ monitoring preview">
        <div className="hero-glow" />

        <div className="floating-temperature-card">
          <div className="mini-card-heading">
            <span className="mini-brand">
              <Snowflake size={17} /> ICEQ MONITOR
            </span>
            <span className="simulated-badge">SIMULATED DATA</span>
          </div>

          <div className="mini-unit">
            <div className="mini-unit-icon"><Milk size={23} /></div>
            <div>
              <span className="muted-text">UNIT_001 · Dairy</span>
              <strong>4.43°C</strong>
              <span className="normal-badge">Normal</span>
            </div>
          </div>

          <div className="mini-chart">
            <div className="chart-gridline" />
            <div className="chart-gridline" />
            <svg
              viewBox="0 0 300 75"
              role="img"
              aria-label="Illustrative temperature trend"
            >
              <polyline
                points="0,43 24,40 48,46 72,36 96,41 120,29 144,34 168,27 192,38 216,31 240,35 264,24 300,30"
                fill="none"
                stroke="#38BDF8"
                strokeWidth="2.5"
                strokeLinejoin="round"
                strokeLinecap="round"
              />
            </svg>
          </div>

          <div className="mini-card-footer">
            <ShieldCheck size={15} />
            <span>Illustrative monitoring preview</span>
          </div>
        </div>

        <div className="floating-status-card">
          <span className="status-pulse" />
          <div>
            <strong>Cold-chain visibility</strong>
            <p>Monitor. Understand. Act.</p>
          </div>
        </div>
      </div>
    </section>
  );
}

function Solutions() {
  return (
    <section className="section section-light" id="solutions">
      <div className="section-container">
        <p className="eyebrow eyebrow-blue">OUR SOLUTIONS</p>

        <div className="section-heading">
          <div>
            <h2>Built for temperature-sensitive operations.</h2>
            <p>
              From farm to fork, IceQ aims to help teams keep products safe,
              conditions visible, and operations informed.
            </p>
          </div>
        </div>

        <div className="solution-grid">
          {solutions.map(({ icon: Icon, title, description }) => (
            <article className="solution-card" key={title}>
              <div className="icon-circle"><Icon size={22} /></div>
              <h3>{title}</h3>
              <p>{description}</p>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}

function Challenges() {
  return (
    <section className="section section-dark">
      <div className="section-container">
        <p className="eyebrow">THE CHALLENGE</p>
        <h2>The cold chain loses value silently.</h2>
        <p className="section-intro">Small deviations. Big consequences.</p>

        <div className="challenge-grid">
          {challenges.map(({ icon: Icon, title, description }) => (
            <article className="challenge-card" key={title}>
              <div className="icon-circle icon-circle-blue">
                <Icon size={22} />
              </div>
              <h3>{title}</h3>
              <p>{description}</p>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}

function Platform() {
  return (
    <section className="section section-light" id="platform">
      <div className="section-container">
        <p className="eyebrow eyebrow-blue">THE ICEQ PLATFORM</p>
        <h2>Smarter monitoring. Better decisions.</h2>
        <p className="section-intro">
          A connected view of conditions, risk signals, and incident history.
        </p>

        <div className="capability-grid">
          {capabilities.map(({ icon: Icon, title, description }) => (
            <article className="capability-card" key={title}>
              <div className="icon-circle"><Icon size={22} /></div>
              <h3>{title}</h3>
              <p>{description}</p>
            </article>
          ))}
        </div>

        <a className="button button-dark" href="#dashboard-preview">
          Explore the Platform <ArrowRight size={17} />
        </a>
      </div>
    </section>
  );
}

function TemperatureChart() {
  return (
    <>
      <div className="trend-chart">
        <div className="trend-labels">
          <span>10°C</span>
          <span>0°C</span>
          <span>-20°C</span>
        </div>

        <svg
          viewBox="0 0 420 190"
          preserveAspectRatio="none"
          role="img"
          aria-label="Illustrative temperature trend chart"
        >
          {[30, 75, 120, 165].map((y) => (
            <line
              key={y}
              x1="0"
              y1={y}
              x2="420"
              y2={y}
              stroke="#16466B"
              strokeDasharray="4 5"
            />
          ))}

          <polyline
            points="0,58 35,52 70,62 105,47 140,54 175,43 210,52 245,46 280,57 315,49 350,55 385,43 420,50"
            fill="none"
            stroke="#38BDF8"
            strokeWidth="2.5"
          />

          <polyline
            points="0,120 35,124 70,115 105,122 140,119 175,126 210,118 245,122 280,116 315,121 350,117 385,125 420,119"
            fill="none"
            stroke="#0284C7"
            strokeWidth="2.5"
          />
        </svg>
      </div>

      <div className="chart-times">
        <span>00:00</span>
        <span>06:00</span>
        <span>12:00</span>
        <span>18:00</span>
        <span>24:00</span>
      </div>
    </>
  );
}

function UnitStatusChart() {
  return (
    <div className="dashboard-status">
      <h3>Unit Status</h3>

      <div className="status-chart">
        <ResponsiveContainer width="100%" height={150}>
          <PieChart>
            <Pie
              data={[{ name: "Normal", value: 3 }]}
              cx="50%"
              cy="50%"
              innerRadius={42}
              outerRadius={58}
              dataKey="value"
              stroke="none"
            >
              <Cell fill="#38BDF8" />
            </Pie>
            <Tooltip />
          </PieChart>
        </ResponsiveContainer>

        <div className="status-chart-center">
          <strong>3</strong>
          <span>Demo units</span>
        </div>
      </div>

      <div className="status-legend">
        <div>
          <span className="legend-dot legend-normal" />
          Normal <strong>3</strong>
        </div>
        <div>
          <span className="legend-dot legend-warning" />
          Warning <strong>0</strong>
        </div>
        <div>
          <span className="legend-dot legend-critical" />
          Critical <strong>0</strong>
        </div>
      </div>

      <small className="chart-disclaimer">
        Illustrative distribution · Simulated data
      </small>
    </div>
  );
}

function IncidentsByUnit() {
  return (
    <div className="dashboard-incidents">
      <h3>Incidents by Unit</h3>

      {demoIncidents.map((unit) => (
        <div className="incident-row" key={unit.id}>
          <span className="legend-dot legend-normal" />
          <span>{unit.id} ({unit.type})</span>
          <strong>{unit.count}</strong>
        </div>
      ))}

      <small className="chart-disclaimer">
        Illustrative incident counts · Simulated data
      </small>
    </div>
  );
}

function DashboardPreview() {
  return (
    <section
      className="section section-dark dashboard-preview"
      id="dashboard-preview"
    >
      <div className="section-container">
        <div className="dashboard-heading">
          <div>
            <p className="eyebrow">ICEQ CONTROL ROOM</p>
            <h2>One control room for every cold-chain asset.</h2>
            <p className="section-intro">
              A clear view of units, conditions, and risk signals.
            </p>
          </div>
          <span className="simulated-badge">SIMULATED DATA</span>
        </div>

        <div className="dashboard-shell">
          <div className="dashboard-topbar">
            <div className="dashboard-brand">
              <Snowflake size={22} /> IceQ
            </div>
            <span className="simulated-badge">DEMO DATA</span>
          </div>

          <div className="dashboard-metrics">
            <div className="metric-card">
              <span>Total Units</span>
              <strong>3</strong>
              <small>Illustrative units</small>
            </div>

            <div className="metric-card">
              <span>Active Alerts</span>
              <strong className="metric-warning">2</strong>
              <small>Example alert states</small>
            </div>

            <div className="metric-card">
              <span>System Status</span>
              <strong className="metric-healthy">Demo</strong>
              <small>Simulated feed</small>
            </div>
          </div>

          <div className="dashboard-content">
            <div className="dashboard-units">
              <h3>Cold Chain Units</h3>

              {demoUnits.map((unit) => (
                <div className="dashboard-unit" key={unit.id}>
                  <div className="unit-snowflake">
                    <Snowflake size={19} />
                  </div>

                  <div className="unit-details">
                    <strong>{unit.id}</strong>
                    <span>{unit.type}</span>
                  </div>

                  <strong className="unit-temperature">{unit.temp}</strong>
                  <span className="normal-badge">{unit.status}</span>
                </div>
              ))}
            </div>

            <div className="dashboard-trend">
              <h3>Temperature Trend (Last 24 Hours)</h3>
              <TemperatureChart />
            </div>

            <UnitStatusChart />
            <IncidentsByUnit />
          </div>

          <div className="dashboard-bottom">
            <div>
              <span className="status-pulse" />
              Historical sample data · Not live sensors
            </div>

            <a className="button button-primary" href="#contact">
              Explore the Platform <ArrowRight size={16} />
            </a>
          </div>
        </div>
      </div>
    </section>
  );
}

function HowItWorks() {
  const steps = [
    {
      number: "01",
      title: "Connect",
      description:
        "Start with simulated sensor streams while the platform is developed for future integrations.",
    },
    {
      number: "02",
      title: "Analyse",
      description:
        "Evaluate temperature readings against configured limits and sustained-excursion rules.",
    },
    {
      number: "03",
      title: "Act",
      description:
        "Review alerts and incident records to support informed operational decisions.",
    },
  ];

  return (
    <section className="section section-light" id="how-it-works">
      <div className="section-container">
        <p className="eyebrow eyebrow-blue">FROM DATA TO ACTION</p>
        <h2>Simple. Smart. Connected.</h2>

        <div className="steps-grid">
          {steps.map((step) => (
            <article className="step-card" key={step.number}>
              <span className="step-number">{step.number}</span>
              <h3>{step.title}</h3>
              <p>{step.description}</p>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}

function About() {
  return (
    <section className="section section-dark about-section" id="about">
      <div className="section-container about-content">
        <div>
          <p className="eyebrow">ABOUT ICEQ</p>
          <h2>Predictive cooling. More informed decisions.</h2>
          <p>
            IceQ is being developed to make cold-chain conditions easier to
            monitor, understand, and investigate. The current product
            demonstrates its workflow using simulated data.
          </p>
          <a className="button button-primary" href="#platform">
            Learn More About IceQ <ArrowRight size={16} />
          </a>
        </div>

        <div className="about-values">
          <div>
            <ShieldCheck />
            <strong>Visibility by design</strong>
            <span>Make conditions easier to review.</span>
          </div>
          <div>
            <Activity />
            <strong>Data-informed operations</strong>
            <span>Turn readings into useful summaries.</span>
          </div>
          <div>
            <Snowflake />
            <strong>Built for cold chains</strong>
            <span>Designed around temperature-sensitive workflows.</span>
          </div>
        </div>
      </div>
    </section>
  );
}


function Contact() {
  const [submitting, setSubmitting] = useState(false);
  const [notice, setNotice] = useState("");
  const [error, setError] = useState("");

  async function handleSubmit(event) {
    event.preventDefault();

    setSubmitting(true);
    setNotice("");
    setError("");

    const form = event.currentTarget;
    const formData = new FormData(form);

    const requestData = {
      name: formData.get("name").trim(),
      email: formData.get("email").trim(),
      organisation: formData.get("organisation").trim(),
      message: formData.get("message").trim(),
    };

    if (
      requestData.name.length < 2 ||
      requestData.organisation.length < 2 ||
      requestData.message.length < 10
    ) {
      setError(
        "Please enter your name, organisation, and a message of at least 10 characters."
      );
      setSubmitting(false);
      return;
    }

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/api/demo-requests",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(requestData),
        }
      );

      const result = await response.json();

      if (!response.ok) {
        throw new Error(
          result.detail || "Unable to submit your request."
        );
      }

      setNotice(
        "Thank you! Your demo request has been received successfully."
      );
      form.reset();
    } catch (err) {
      setError(
        err.message === "Failed to fetch"
          ? "Could not connect to IceQ. Please check that the backend is running and try again."
          : err.message || "Something went wrong. Please try again."
      );
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <section className="section section-light" id="contact">
      <div className="section-container contact-layout">
        <div>
          <p className="eyebrow eyebrow-blue">LET'S CONNECT</p>
          <h2>Let's build a safer cold chain together.</h2>
          <p>
            Interested in the IceQ concept or want to discuss a demonstration?
            Send a message using the form.
          </p>

          <div className="contact-note">
            <ShieldCheck size={21} />
            <span>
              Submit a request to contact the IceQ team. This prototype
              stores requests locally and does not send email notifications.
            </span>
          </div>
        </div>

        <form className="contact-form" onSubmit={handleSubmit}>
          <label>
            Name
            <input
              name="name"
              required
              minLength={2}
              maxLength={100}
              placeholder="Your name"
            />
          </label>

          <label>
            Business email
            <input
              name="email"
              type="email"
              required
              maxLength={254}
              placeholder="you@company.com"
            />
          </label>

          <label>
            Organisation
            <input
              name="organisation"
              required
              minLength={2}
              maxLength={150}
              placeholder="Company or organisation"
            />
          </label>

          <label>
            How can we help?
            <textarea
              name="message"
              required
              minLength={10}
              maxLength={2000}
              rows="4"
              placeholder="Tell us what you'd like to explore..."
            />
          </label>

          <button
            className="button button-primary form-submit"
            type="submit"
            disabled={submitting}
          >
            {submitting ? "Sending..." : "Send Message"}
            {!submitting && <ArrowRight size={16} />}
          </button>

          {notice && (
            <p className="form-notice" role="status">
              {notice}
            </p>
          )}

          {error && (
            <p className="form-notice" role="alert">
              {error}
            </p>
          )}
        </form>
      </div>
    </section>
  );
}

function Footer() {
  return (
    <footer className="site-footer">
      <div className="footer-main">
        <a className="brand footer-brand" href="#home">
          <img src={iceqLogo} alt="IceQ" />
        </a>

        <p>Predictive Cooling. Absolute Control.</p>

        <nav aria-label="Footer navigation">
          <a href="#platform">Platform</a>
          <a href="#solutions">Solutions</a>
          <a href="#about">About</a>
          <a href="#contact">Contact</a>
        </nav>
      </div>

      <div className="footer-bottom">
        <span>© {new Date().getFullYear()} IceQ · Prototype</span>
        <span>Monitoring interface uses simulated data.</span>
      </div>
    </footer>
  );
}


export default function App() {
  return (
    <Routes>
      <Route
        path="/"
        element={
          <div className="iceq-app">
            <Header />

            <main>
              <Hero />
              <Solutions />
              <Challenges />
              <Platform />
              <DashboardPreview />
              <HowItWorks />
              <About />
              <Contact />
            </main>

            <Footer />
          </div>
        }
      />

      <Route path="/login" element={<Login />} />
      <Route path="/signup" element={<Signup />} />
      <Route path="/dashboard" element={<MonitoringDashboard />} />
      <Route path="/sensor-simulator" element={<SensorSimulator />} />


      <Route
        path="*"
        element={
          <div className="iceq-app">
            <Header />
            <main>
              <section className="section section-dark">
                <div className="section-container">
                  <h2>Page not found</h2>
                  <p>The page you requested doesn't exist.</p>
                  <a className="button button-primary" href="/">
                    Back to Home
                  </a>
                </div>
              </section>
            </main>
            <Footer />
          </div>
        }
      />
    </Routes>
  );
}
