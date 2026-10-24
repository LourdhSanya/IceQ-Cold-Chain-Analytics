
import { useEffect, useState } from 'react'
import {
  Activity,
  AlertTriangle,
  ArrowUpRight,
  Bell,
  ChevronRight,
  CircleHelp,
  Clock3,
  LayoutDashboard,
  LogOut,
  Menu,
  Package,
  Radio,
  RefreshCw,
  ShieldCheck,
  Thermometer,
  Truck,
  X,
} from 'lucide-react'
import {
  Area,
  AreaChart,
  CartesianGrid,
  Line,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { useNavigate } from 'react-router-dom'
import iceqLogo from './assets/iceq-logo.png'
import './MonitoringDashboard.css'

const API_BASE_URL = 'http://127.0.0.1:8000'

function formatDate(value) {
  if (!value) return '—'

  const date = new Date(value)

  if (Number.isNaN(date.getTime())) {
    return String(value)
  }

  return date.toLocaleString([], {
    day: '2-digit',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  })
}

function formatTemperature(value) {
  if (value === null || value === undefined || value === '') {
    return '—'
  }

  const temperature = Number(value)

  return Number.isFinite(temperature)
    ? `${temperature.toFixed(2)}°C`
    : '—'
}

function formatHumidity(value) {
  if (value === null || value === undefined || value === '') {
    return '—'
  }

  const humidity = Number(value)

  return Number.isFinite(humidity)
    ? `${humidity.toFixed(1)}%`
    : '—'
}

function formatStatus(status) {
  return String(status || 'UNKNOWN').toUpperCase()
}

function getStatusClass(status) {
  const normalized = formatStatus(status)

  if (normalized === 'NORMAL') return 'normal'
  if (normalized === 'WARNING') return 'warning'
  if (normalized === 'CRITICAL') return 'critical'

  return 'unknown'
}

function getFoodIcon(category) {
  const name = String(category || '').toLowerCase()

  if (name.includes('dairy')) return '🥛'
  if (name.includes('produce')) return '🥬'
  if (name.includes('frozen')) return '❄️'
  if (name.includes('meat')) return '🥩'
  if (name.includes('seafood')) return '🐟'
  if (name.includes('pharma')) return '💊'

  return '📦'
}

function getUnitName(unit) {
  return (
    unit.unit_id ||
    unit.id ||
    unit.name ||
    'Unknown unit'
  )
}

function getUnitCategory(unit) {
  return (
    unit.food_type ||
    unit.category ||
    unit.name ||
    'Cold-chain unit'
  )
}

function getUnitTemperature(unit) {
  return (
    unit.temperature_c ??
    unit.temperature ??
    unit.current_temperature_c
  )
}

// Supports the humidity field names commonly used by the API.
function getUnitHumidity(unit) {
  return (
    unit.humidity_pct ??
    unit.humidity_percent ??
    unit.humidity_percentage ??
    unit.humidity ??
    unit.current_humidity_pct ??
    unit.current_humidity_percent ??
    unit.current_humidity ??
    unit.relative_humidity_pct ??
    unit.relative_humidity ??
    null
  )
}

function getUnitStatus(unit) {
  return (
    unit.risk_status ||
    unit.status ||
    'UNKNOWN'
  )
}

function getUnitThreshold(unit) {
  return (
    unit.temperature_threshold_c ??
    unit.threshold_c ??
    unit.threshold
  )
}

function getIncidentId(incident, index) {
  return (
    incident.incident_id ||
    incident.id ||
    `INC-${String(index + 1).padStart(3, '0')}`
  )
}

function getIncidentUnit(incident) {
  return incident.unit_id || incident.unit || 'Unknown unit'
}

function getIncidentMaximum(incident) {
  return (
    incident.max_temperature_c ??
    incident.maximum_temperature_c ??
    incident.max_temperature
  )
}

function getIncidentStart(incident) {
  return (
    incident.start_time ||
    incident.timestamp ||
    incident.start_timestamp
  )
}

function getIncidentEnd(incident) {
  return incident.end_time || incident.end_timestamp
}

function getIncidentCount(incident) {
  return (
    incident.total_readings ??
    incident.reading_count ??
    incident.critical_readings ??
    0
  )
}

function getIncidentDuration(incident) {
  if (incident.elapsed_minutes !== undefined) {
    return `${incident.elapsed_minutes} min`
  }

  if (incident.start_time && incident.end_time) {
    const start = new Date(incident.start_time).getTime()
    const end = new Date(incident.end_time).getTime()

    if (Number.isFinite(start) && Number.isFinite(end)) {
      return `${Math.max(0, Math.round((end - start) / 60000))} min`
    }
  }

  return '—'
}

function MonitoringDashboard() {
  const navigate = useNavigate()

  const [units, setUnits] = useState([])
  const [incidents, setIncidents] = useState([])
  const [summary, setSummary] = useState(null)

  const [loading, setLoading] = useState(true)
  const [apiError, setApiError] = useState('')
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  const [readings, setReadings] = useState([])
  const [selectedUnitId, setSelectedUnitId] = useState('UNIT_001')
  const [readingsLoading, setReadingsLoading] = useState(false)
  const [readingsError, setReadingsError] = useState('')

  // Load units, incidents, and summary from the IceQ API.
  useEffect(() => {
    let cancelled = false

    async function loadDashboard() {
      try {
        setLoading(true)
        setApiError('')

        const [unitsResponse, incidentsResponse, summaryResponse] =
          await Promise.all([
            fetch(`${API_BASE_URL}/api/units`),
            fetch(`${API_BASE_URL}/api/incidents`),
            fetch(`${API_BASE_URL}/api/summary`),
          ])

        if (
          !unitsResponse.ok ||
          !incidentsResponse.ok ||
          !summaryResponse.ok
        ) {
          throw new Error(
            'Unable to load dashboard data. Check that the IceQ API is running.',
          )
        }

        const [unitsData, incidentsData, summaryData] =
          await Promise.all([
            unitsResponse.json(),
            incidentsResponse.json(),
            summaryResponse.json(),
          ])

        if (cancelled) return

        const unitsList = Array.isArray(unitsData)
          ? unitsData
          : unitsData.units || unitsData.data || []

        const incidentsList = Array.isArray(incidentsData)
          ? incidentsData
          : incidentsData.incidents || incidentsData.data || []

        setUnits(unitsList)
        setIncidents(incidentsList)
        setSummary(summaryData)
      } catch (error) {
        if (!cancelled) {
          setApiError(
            error.message || 'Could not connect to the IceQ API.',
          )
        }
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }

    loadDashboard()

    return () => {
      cancelled = true
    }
  }, [])

  // Load historical readings for the selected monitoring unit.
  useEffect(() => {
    let cancelled = false

    async function loadReadings() {
      try {
        setReadingsLoading(true)
        setReadingsError('')

        const response = await fetch(
          `${API_BASE_URL}/api/readings?unit_id=${encodeURIComponent(selectedUnitId)}&limit=288`,
        )

        if (!response.ok) {
          throw new Error(
            'Could not load historical temperature readings.',
          )
        }

        const data = await response.json()

        if (cancelled) return

        const readingsList = Array.isArray(data)
          ? data
          : data.readings || data.data || []

        const formattedReadings = readingsList
          .map((reading) => {
            const timestamp = new Date(reading.timestamp)

            return {
              ...reading,
              temperature_c: Number(reading.temperature_c),
              temperature_threshold_c: Number(
                reading.temperature_threshold_c,
              ),
              chartTime: Number.isNaN(timestamp.getTime())
                ? String(reading.timestamp || '')
                : timestamp.toLocaleTimeString([], {
                    hour: '2-digit',
                    minute: '2-digit',
                    hour12: false,
                  }),
            }
          })
          .filter(
            (reading) =>
              Number.isFinite(reading.temperature_c) &&
              Number.isFinite(reading.temperature_threshold_c),
          )
          .sort(
            (a, b) =>
              new Date(a.timestamp).getTime() -
              new Date(b.timestamp).getTime(),
          )

        setReadings(formattedReadings)
      } catch (error) {
        if (!cancelled) {
          setReadings([])
          setReadingsError(
            error.message || 'Unable to load historical readings.',
          )
        }
      } finally {
        if (!cancelled) {
          setReadingsLoading(false)
        }
      }
    }

    loadReadings()

    return () => {
      cancelled = true
    }
  }, [selectedUnitId])

  const totalUnits = summary?.total_units ?? units.length
  const statusCounts = summary?.status_counts || {}

  const normalCount =
    statusCounts.NORMAL ??
    units.filter(
      (unit) => formatStatus(getUnitStatus(unit)) === 'NORMAL',
    ).length

  const warningCount =
    statusCounts.WARNING ??
    units.filter(
      (unit) => formatStatus(getUnitStatus(unit)) === 'WARNING',
    ).length

  const criticalCount =
    statusCounts.CRITICAL ??
    units.filter(
      (unit) => formatStatus(getUnitStatus(unit)) === 'CRITICAL',
    ).length

  const totalIncidents = summary?.total_incidents ?? incidents.length

  const selectedUnit = units.find(
    (unit) => getUnitName(unit) === selectedUnitId,
  )

  const selectedCategory = selectedUnit
    ? getUnitCategory(selectedUnit)
    : selectedUnitId === 'UNIT_001'
      ? 'Dairy'
      : selectedUnitId === 'UNIT_002'
        ? 'Produce'
        : selectedUnitId === 'UNIT_003'
          ? 'Frozen'
          : 'Cold-chain'

  const latestTimestamp =
    summary?.latest_timestamp ||
    summary?.last_updated ||
    null

  async function refreshDashboard() {
    setLoading(true)
    setApiError('')

    try {
      const [unitsResponse, incidentsResponse, summaryResponse] =
        await Promise.all([
          fetch(`${API_BASE_URL}/api/units`),
          fetch(`${API_BASE_URL}/api/incidents`),
          fetch(`${API_BASE_URL}/api/summary`),
        ])

      if (
        !unitsResponse.ok ||
        !incidentsResponse.ok ||
        !summaryResponse.ok
      ) {
        throw new Error('Unable to refresh the IceQ dashboard.')
      }

      const [unitsData, incidentsData, summaryData] =
        await Promise.all([
          unitsResponse.json(),
          incidentsResponse.json(),
          summaryResponse.json(),
        ])

      setUnits(
        Array.isArray(unitsData)
          ? unitsData
          : unitsData.units || unitsData.data || [],
      )

      setIncidents(
        Array.isArray(incidentsData)
          ? incidentsData
          : incidentsData.incidents || incidentsData.data || [],
      )

      setSummary(summaryData)
    } catch (error) {
      setApiError(
        error.message || 'Unable to refresh dashboard data.',
      )
    } finally {
      setLoading(false)
    }
  }

  function handleLogout() {
    navigate('/')
  }

  return (
    <div className="monitor-dashboard">
      {mobileMenuOpen && (
        <button
          type="button"
          className="monitor-mobile-overlay"
          aria-label="Close navigation menu"
          onClick={() => setMobileMenuOpen(false)}
        />
      )}

      <aside
        className={`monitor-sidebar ${
          mobileMenuOpen ? 'monitor-sidebar-open' : ''
        }`}
      >
        <div className="monitor-brand">
          <img
            src={iceqLogo}
            alt="IceQ logo"
            className="monitor-brand-logo"
          />

          <div className="monitor-brand-copy">
            <span className="monitor-brand-name">IceQ</span>
            <span className="monitor-brand-caption">
              COLD-CHAIN INTELLIGENCE
            </span>
          </div>

          <button
            type="button"
            className="monitor-mobile-close"
            aria-label="Close navigation"
            onClick={() => setMobileMenuOpen(false)}
          >
            <X size={18} />
          </button>
        </div>

        <div className="monitor-nav-label">WORKSPACE</div>

        <nav className="monitor-navigation">
          <button
            type="button"
            className="monitor-nav-item monitor-nav-active"
            onClick={() => setMobileMenuOpen(false)}
          >
            <LayoutDashboard size={18} />
            <span>Overview</span>
          </button>

          <button
            type="button"
            className="monitor-nav-item"
            onClick={() => {
              document
                .getElementById('cold-chain-units')
                ?.scrollIntoView({ behavior: 'smooth' })
              setMobileMenuOpen(false)
            }}
          >
            <Package size={18} />
            <span>Monitoring units</span>
            <span className="monitor-nav-count">{totalUnits}</span>
          </button>



          <button
            type="button"
            className="monitor-nav-item"
            onClick={() => {
              document
                .getElementById('incident-history')
                ?.scrollIntoView({ behavior: 'smooth' })
              setMobileMenuOpen(false)
            }}
          >
            <Bell size={18} />
            <span>Incident history</span>
            {totalIncidents > 0 && (
              <span className="monitor-nav-count">{totalIncidents}</span>
            )}
          </button>

          <button
            type="button"
            className="monitor-nav-item"
            onClick={() => {
              document
                .getElementById('temperature-trends')
                ?.scrollIntoView({ behavior: 'smooth' })
              setMobileMenuOpen(false)
            }}
          >
            <Activity size={18} />
            <span>Temperature trends</span>
          </button>
<button
  type="button"
  className="monitor-nav-item"
  onClick={() => {
    navigate('/sensor-simulator')
    setMobileMenuOpen(false)
  }}
>
  <Radio size={18} />
  <span>Sensor Simulator</span>
</button>

        </nav>

        <div className="monitor-sidebar-spacer" />

        <div className="monitor-demo-card">
          <div className="monitor-demo-icon">
            <ShieldCheck size={18} />
          </div>
          <div>
            <strong>Demo environment</strong>
            <p>Simulated sensor data</p>
          </div>
          <span className="monitor-demo-dot" />
        </div>

        <button
          type="button"
          className="monitor-nav-item monitor-logout"
          onClick={handleLogout}
        >
          <LogOut size={18} />
          <span>Back to website</span>
        </button>

        <div className="monitor-sidebar-footer">
          <span>ICEQ MONITOR</span>
          <span>SOFTWARE DEMO</span>
        </div>
      </aside>

      <main className="monitor-main">
        <header className="monitor-topbar">
          <div className="monitor-topbar-left">
            <button
              type="button"
              className="monitor-menu-button"
              aria-label="Open navigation"
              onClick={() => setMobileMenuOpen(true)}
            >
              <Menu size={21} />
            </button>

            <div className="monitor-breadcrumb">
              <span>Workspace</span>
              <ChevronRight size={14} />
              <strong>Overview</strong>
            </div>
          </div>

          <div className="monitor-topbar-right">
            <span className="monitor-environment">
              <span className="monitor-demo-dot" />
              SIMULATED DATA
            </span>

            <button
              type="button"
              className="monitor-refresh-button"
              onClick={refreshDashboard}
              disabled={loading}
              title="Refresh dashboard"
            >
              <RefreshCw
                size={15}
                className={loading ? 'monitor-spin' : ''}
              />
              <span>Refresh</span>
            </button>

            <div className="monitor-avatar">IQ</div>
          </div>
        </header>

        <div className="monitor-content">
          <section className="monitor-page-heading">
            <div>
              <div className="monitor-eyebrow">
                <span className="monitor-eyebrow-dot" />
                COLD-CHAIN INTELLIGENCE PLATFORM
              </div>

              <h1>Monitoring overview</h1>

              <p>
                Monitor simulated cold-chain conditions and review
                historical temperature excursions.
              </p>
            </div>

            <div className="monitor-updated">
              <Clock3 size={14} />
              <span>
                Latest reading:{' '}
                {latestTimestamp
                  ? formatDate(latestTimestamp)
                  : 'Awaiting API data'}
              </span>
            </div>
          </section>

          <div className="monitor-simulation-banner">
            <div className="monitor-simulation-icon">
              <CircleHelp size={18} />
            </div>

            <div className="monitor-simulation-copy">
              <strong>Software demonstration · Simulated data</strong>
              <p>
                The dashboard uses historical simulated sensor readings
                from the IceQ API. It is not connected to physical IoT
                sensors and does not provide validated real-world spoilage
                predictions.
              </p>
            </div>
          </div>

          {apiError && (
            <div className="monitor-error-banner" role="alert">
              <AlertTriangle size={18} />
              <div>
                <strong>Dashboard connection issue</strong>
                <p>{apiError}</p>
              </div>
              <button type="button" onClick={refreshDashboard}>
                Try again
              </button>
            </div>
          )}

          <section className="monitor-stat-grid">
            <article className="monitor-stat-card">
              <div className="monitor-stat-top">
                <span className="monitor-stat-label">
                  Total monitoring units
                </span>
                <span className="monitor-stat-icon stat-icon-blue">
                  <Package size={19} />
                </span>
              </div>
              <div className="monitor-stat-value">
                {loading ? '—' : totalUnits}
              </div>
              <div className="monitor-stat-footer">
                <span className="monitor-stat-neutral">
                  Configured demo units
                </span>
              </div>
            </article>

            <article className="monitor-stat-card">
              <div className="monitor-stat-top">
                <span className="monitor-stat-label">Normal units</span>
                <span className="monitor-stat-icon stat-icon-green">
                  <ShieldCheck size={19} />
                </span>
              </div>
              <div className="monitor-stat-value">
                {loading ? '—' : normalCount}
              </div>
              <div className="monitor-stat-footer">
                <span className="monitor-stat-success">
                  Within configured limits
                </span>
              </div>
            </article>

            <article className="monitor-stat-card">
              <div className="monitor-stat-top">
                <span className="monitor-stat-label">Warning units</span>
                <span className="monitor-stat-icon stat-icon-amber">
                  <AlertTriangle size={19} />
                </span>
              </div>
              <div className="monitor-stat-value">
                {loading ? '—' : warningCount}
              </div>
              <div className="monitor-stat-footer">
                <span className="monitor-stat-warning">
                  Historical rule-based status
                </span>
              </div>
            </article>

            <article className="monitor-stat-card">
              <div className="monitor-stat-top">
                <span className="monitor-stat-label">Critical units</span>
                <span className="monitor-stat-icon stat-icon-red">
                  <Thermometer size={19} />
                </span>
              </div>
              <div className="monitor-stat-value">
                {loading ? '—' : criticalCount}
              </div>
              <div className="monitor-stat-footer">
                <span className="monitor-stat-danger">
                  Historical rule-based status
                </span>
              </div>
            </article>
          </section>

          <section
            id="temperature-trends"
            className="monitor-panel trend-panel"
          >
            <div className="monitor-panel-heading">
              <div>
                <h2>Temperature trends</h2>
                <p>
                  Historical {selectedCategory} readings from the IceQ demo
                  dataset
                </p>
              </div>

              <div className="chart-controls">
                <label htmlFor="chart-unit-select">Monitoring unit</label>
                <select
                  id="chart-unit-select"
                  className="chart-unit-select"
                  value={selectedUnitId}
                  onChange={(event) => setSelectedUnitId(event.target.value)}
                  disabled={units.length === 0}
                >
{[...units]
  .sort((a, b) =>
    getUnitName(a).localeCompare(getUnitName(b))
  )
  .map((unit) => {
    const unitId = getUnitName(unit)

    return (
      <option key={unitId} value={unitId}>
        {unitId} · {getUnitCategory(unit)}
      </option>
    )
  })}


                  {units.length === 0 && (
                    <option value="UNIT_001">UNIT_001 · Dairy</option>
                  )}
                </select>
              </div>
            </div>

            <div className="chart-data-caption">
              <span className="simulation-dot" />
              SIMULATED DATA · LAST 24 HOURS OF AVAILABLE READINGS
            </div>

            {readingsLoading && (
              <p className="monitor-empty">Loading historical readings...</p>
            )}

            {readingsError && !readingsLoading && (
              <p className="monitor-empty" role="alert">
                {readingsError}
              </p>
            )}

            {!readingsLoading &&
              !readingsError &&
              readings.length > 0 && (
                <>
                  <div className="monitor-chart">
                    <ResponsiveContainer width="100%" height="100%">
                      <AreaChart
                        data={readings}
                        margin={{
                          top: 12,
                          right: 16,
                          left: -12,
                          bottom: 0,
                        }}
                      >
                        <defs>
                          <linearGradient
                            id="temperatureFill"
                            x1="0"
                            y1="0"
                            x2="0"
                            y2="1"
                          >
                            <stop
                              offset="0%"
                              stopColor="#38BDF8"
                              stopOpacity={0.25}
                            />
                            <stop
                              offset="95%"
                              stopColor="#38BDF8"
                              stopOpacity={0}
                            />
                          </linearGradient>
                        </defs>

                        <CartesianGrid
                          stroke="#23364C"
                          strokeDasharray="4 5"
                          vertical={false}
                        />

                        <XAxis
                          dataKey="chartTime"
                          minTickGap={35}
                          tick={{ fill: '#94A3B8', fontSize: 11 }}
                          axisLine={false}
                          tickLine={false}
                        />

                        <YAxis
                          tick={{ fill: '#94A3B8', fontSize: 11 }}
                          axisLine={false}
                          tickLine={false}
                          tickFormatter={(value) => `${value}°`}
                          width={48}
                        />

                        <Tooltip
                          labelFormatter={(_, payload) => {
                            const timestamp =
                              payload?.[0]?.payload?.timestamp

                            return timestamp ? formatDate(timestamp) : ''
                          }}
                          contentStyle={{
                            background: '#111E33',
                            border: '1px solid #334155',
                            borderRadius: 10,
                            color: '#E0F2FE',
                          }}
                          labelStyle={{
                            color: '#E0F2FE',
                            marginBottom: 6,
                          }}
                          formatter={(value, name) => [
                            `${Number(value).toFixed(2)}°C`,
                            name === 'temperature_c'
                              ? 'Recorded temperature'
                              : 'Configured threshold',
                          ]}
                        />

                        <Area
                          type="monotone"
                          dataKey="temperature_c"
                          name="temperature_c"
                          stroke="#38BDF8"
                          strokeWidth={2}
                          fill="url(#temperatureFill)"
                          isAnimationActive={false}
                          dot={false}
                          activeDot={{ r: 4 }}
                        />

                        <Line
                          type="monotone"
                          dataKey="temperature_threshold_c"
                          name="temperature_threshold_c"
                          stroke="#FBBF24"
                          strokeWidth={1.5}
                          strokeDasharray="6 4"
                          dot={false}
                          activeDot={false}
                          isAnimationActive={false}
                        />
                      </AreaChart>
                    </ResponsiveContainer>
                  </div>

                  <div className="monitor-chart-legend">
                    <span>
                      <i className="legend-dairy" />
                      Recorded temperature
                    </span>
                    <span>
                      <i className="legend-threshold" />
                      Configured threshold
                    </span>
                    <span className="chart-sim-note">
                      Historical simulation · Not live
                    </span>
                  </div>

                  <p className="panel-footnote">
                    Showing {readings.length} readings returned by the API
                    for {selectedUnitId}. The threshold is the configured
                    temperature limit, not a spoilage prediction.
                  </p>
                </>
              )}

            {!readingsLoading &&
              !readingsError &&
              readings.length === 0 && (
                <p className="monitor-empty">
                  No historical readings are available for this unit.
                </p>
              )}
          </section>

          <section id="cold-chain-units" className="monitor-panel">
            <div className="monitor-panel-heading">
              <div>
                <h2>Cold-chain units</h2>
                <p>
                  Current status from the latest simulated readings
                </p>
              </div>
              <span className="monitor-section-count">
                {units.length} UNITS
              </span>
            </div>

            {loading && units.length === 0 ? (
              <p className="monitor-empty">Loading monitoring units...</p>
            ) : units.length === 0 ? (
              <p className="monitor-empty">
                No monitoring units are available. Check the IceQ API
                connection.
              </p>
            ) : (
              <div className="monitor-table-wrapper">
                <table className="monitor-table">
                  <thead>
                    <tr>
                      <th>UNIT</th>
                      <th>FOOD CATEGORY</th>
                      <th>TEMPERATURE</th>
                      <th>HUMIDITY</th>
                      <th>CONFIGURED LIMIT</th>
                      <th>STATUS</th>
                      <th />
                    </tr>
                  </thead>

                  <tbody>
                    {[...units]
                        .sort((a, b) =>
                            getUnitName(a).localeCompare(getUnitName(b))
                        )
                        .map((unit, index) => {
                      const unitId = getUnitName(unit)
                      const category = getUnitCategory(unit)
                      const status = getUnitStatus(unit)
                      const humidity = getUnitHumidity(unit)

                      return (
                        <tr key={unitId || index}>
                          <td>
                            <div className="monitor-unit-id">
                              <span className="monitor-unit-icon">
                                <Truck size={16} />
                              </span>
                              <div>
                                <strong>{unitId}</strong>
                                <small>Simulated monitoring unit</small>
                              </div>
                            </div>
                          </td>

                          <td>
                            <span className="monitor-category">
                              <span>{getFoodIcon(category)}</span>
                              {category}
                            </span>
                          </td>

                          <td>
                            <span className="monitor-temperature">
                              {formatTemperature(getUnitTemperature(unit))}
                            </span>
                          </td>

                          <td>{formatHumidity(humidity)}</td>

                          <td>
                            {formatTemperature(getUnitThreshold(unit))}
                          </td>

                          <td>
                            <span
                              className={`monitor-status status-${getStatusClass(status)}`}
                            >
                              <span className="monitor-status-dot" />
                              {formatStatus(status)}
                            </span>
                          </td>

                          <td>
                            <button
                              type="button"
                              className="monitor-row-action"
                              title={`Show ${unitId} temperature history`}
                              aria-label={`Show ${unitId} temperature history`}
                              onClick={() => {
                                setSelectedUnitId(unitId)
                                document
                                  .getElementById('temperature-trends')
                                  ?.scrollIntoView({ behavior: 'smooth' })
                              }}
                            >
                              <ChevronRight size={17} />
                            </button>
                          </td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              </div>
            )}

            <div className="monitor-panel-bottom">
              <span>
                <span className="simulation-dot" />
                All values are from simulated data
              </span>

              <button
                type="button"
                className="monitor-text-button"
                onClick={refreshDashboard}
                disabled={loading}
              >
                Refresh units
                <ArrowUpRight size={14} />
              </button>
            </div>
          </section>

          <section id="incident-history" className="monitor-panel">
            <div className="monitor-panel-heading">
              <div>
                <h2>Incident history</h2>
                <p>
                  Previously detected temperature excursions in the
                  simulated dataset
                </p>
              </div>
              <span className="monitor-section-count">
                {incidents.length} INCIDENTS
              </span>
            </div>

            {loading && incidents.length === 0 ? (
              <p className="monitor-empty">Loading incident history...</p>
            ) : incidents.length === 0 ? (
              <div className="monitor-empty-state">
                <ShieldCheck size={24} />
                <strong>No historical incidents found</strong>
                <p>
                  The API has not returned any incidents for this dataset.
                </p>
              </div>
            ) : (
              <div className="monitor-incident-list">
                {incidents.slice(0, 10).map((incident, index) => {
                  const incidentId = getIncidentId(incident, index)

                  return (
                    <article
                      className="monitor-incident"
                      key={incidentId}
                    >
                      <div className="monitor-incident-icon">
                        <AlertTriangle size={17} />
                      </div>

                      <div className="monitor-incident-main">
                        <div className="monitor-incident-title">
                          <strong>{incidentId}</strong>
                          <span className="monitor-status status-critical">
                            <span className="monitor-status-dot" />
                            HISTORICAL
                          </span>
                        </div>

                        <p>
                          {getIncidentUnit(incident)} · Temperature
                          excursion detected
                        </p>

                        <div className="monitor-incident-meta">
                          <span>
                            <Clock3 size={12} />
                            {formatDate(getIncidentStart(incident))}
                          </span>
                          {getIncidentEnd(incident) && (
                            <span>
                              to {formatDate(getIncidentEnd(incident))}
                            </span>
                          )}
                        </div>
                      </div>

                      <div className="monitor-incident-metric">
                        <span>Maximum temperature</span>
                        <strong>
                          {formatTemperature(getIncidentMaximum(incident))}
                        </strong>
                      </div>

                      <div className="monitor-incident-metric">
                        <span>Duration</span>
                        <strong>{getIncidentDuration(incident)}</strong>
                      </div>

                      <div className="monitor-incident-metric">
                        <span>Readings</span>
                        <strong>{getIncidentCount(incident)}</strong>
                      </div>
                    </article>
                  )
                })}
              </div>
            )}

            {incidents.length > 10 && (
              <div className="monitor-panel-bottom">
                <span>
                  Showing the latest 10 of {incidents.length} historical
                  incidents
                </span>
              </div>
            )}

            <div className="monitor-incident-note">
              <AlertTriangle size={15} />
              <p>
                These are historical incidents from simulated data, not
                current active alerts. Temperature excursions are identified
                using configured thresholds.
              </p>
            </div>
          </section>

          <footer className="monitor-footer">
            <div>
              <span className="monitor-footer-brand">IceQ</span>
              <span>Predictive Cooling. Absolute Control.</span>
            </div>

            <div className="monitor-footer-right">
              <span>
                <span className="simulation-dot" />
                SIMULATION MODE
              </span>
              <span>Software demonstration</span>
            </div>
          </footer>
        </div>
      </main>
    </div>
  )
}

export default MonitoringDashboard
