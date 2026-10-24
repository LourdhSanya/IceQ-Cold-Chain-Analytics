
import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { UserRoundPlus, ArrowLeft } from 'lucide-react'
import logo from './assets/iceq-logo.png'
import './Signup.css'

function Signup() {
  const navigate = useNavigate()

  const [formData, setFormData] = useState({
    fullName: '',
    company: '',
    email: '',
    password: '',
    confirmPassword: '',
  })

  const [error, setError] = useState('')

  function handleChange(event) {
    const { name, value } = event.target

    setFormData((previousData) => ({
      ...previousData,
      [name]: value,
    }))

    setError('')
  }

  function handleSignup(event) {
    event.preventDefault()
    setError('')

    if (
      !formData.fullName.trim() ||
      !formData.company.trim() ||
      !formData.email.trim() ||
      !formData.password ||
      !formData.confirmPassword
    ) {
      setError('Please complete all fields.')
      return
    }

    if (formData.password.length < 8) {
      setError('Password must contain at least 8 characters.')
      return
    }

    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match.')
      return
    }

    // Frontend prototype only. No account is saved yet.
    alert('Registration form validated! Account creation will be connected later.')
    navigate('/login')
  }

  return (
    <main className="signup-page">
      <button
        className="signup-back"
        type="button"
        onClick={() => navigate('/')}
      >
        <ArrowLeft size={18} />
        Back to Home
      </button>

      <section className="signup-card">
        <img className="signup-logo" src={logo} alt="IceQ logo" />

        <div className="signup-icon">
          <UserRoundPlus size={26} />
        </div>

        <p className="signup-eyebrow">ICEQ CONTROL CENTER</p>
        <h1>Create your account.</h1>

        <p className="signup-description">
          Get ready to explore smarter cold-chain monitoring.
        </p>

        <form onSubmit={handleSignup}>
          <label htmlFor="fullName">Full name</label>
          <input
            id="fullName"
            name="fullName"
            type="text"
            placeholder="Your full name"
            value={formData.fullName}
            onChange={handleChange}
            autoComplete="name"
            required
          />

          <label htmlFor="company">Company name</label>
          <input
            id="company"
            name="company"
            type="text"
            placeholder="Your organisation"
            value={formData.company}
            onChange={handleChange}
            autoComplete="organization"
            required
          />

          <label htmlFor="signupEmail">Business email</label>
          <input
            id="signupEmail"
            name="email"
            type="email"
            placeholder="you@company.com"
            value={formData.email}
            onChange={handleChange}
            autoComplete="email"
            required
          />

          <label htmlFor="signupPassword">Password</label>
          <input
            id="signupPassword"
            name="password"
            type="password"
            placeholder="At least 8 characters"
            value={formData.password}
            onChange={handleChange}
            autoComplete="new-password"
            minLength={8}
            required
          />

          <label htmlFor="confirmPassword">Confirm password</label>
          <input
            id="confirmPassword"
            name="confirmPassword"
            type="password"
            placeholder="Re-enter your password"
            value={formData.confirmPassword}
            onChange={handleChange}
            autoComplete="new-password"
            required
          />

          {error && (
            <p className="signup-error" role="alert">
              {error}
            </p>
          )}

          <button className="signup-submit" type="submit">
            Create Account
          </button>
        </form>

        <p className="signup-login-link">
          Already have an account? <Link to="/login">Sign in</Link>
        </p>

        <p className="signup-demo-note">
          Demo prototype · Account creation is not connected yet
        </p>
      </section>
    </main>
  )
}

export default Signup
