
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ShieldCheck, ArrowLeft } from 'lucide-react'
import logo from './assets/iceq-logo.png'
import './Login.css'

function Login() {
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')

  function handleLogin(event) {
    event.preventDefault()

    if (!email.trim() || !password.trim()) {
      alert('Please enter your email and password.')
      return
    }

    // Prototype login only — not production authentication.
    navigate('/dashboard')
  }

  return (
    <main className="login-page">
      <button
        className="login-back"
        onClick={() => navigate('/')}
        type="button"
      >
        <ArrowLeft size={18} />
        Back to Home
      </button>

      <section className="login-card">
        <img className="login-logo" src={logo} alt="IceQ logo" />

        <div className="login-icon">
          <ShieldCheck size={26} />
        </div>

        <p className="login-eyebrow">ICEQ CONTROL CENTER</p>
        <h1>Welcome back.</h1>
        <p className="login-description">
          Sign in to access your cold-chain monitoring dashboard.
        </p>

        <form onSubmit={handleLogin}>
          <label htmlFor="email">Email address</label>
          <input
            id="email"
            type="email"
            placeholder="you@company.com"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            required
          />

          <label htmlFor="password">Password</label>
          <input
            id="password"
            type="password"
            placeholder="Enter your password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            required
          />

          <button className="login-submit" type="submit">
            Access Dashboard
          </button>
        </form>

        <p className="login-demo-note">
          Demo prototype · Monitoring data is simulated
        </p>
        <p className="login-signup-prompt">
            Don't have an account?{' '}
            <button
                type="button"
                onClick={() => navigate('/signup')}
            >
                Create account
            </button>
        </p>
      </section>
    </main>
  )
}

export default Login
