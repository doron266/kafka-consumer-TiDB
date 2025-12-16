import { useMemo, useState } from 'react'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'

const initialForm = {
  username: '',
  email: '',
  password: '',
}

const formFields = [
  { name: 'username', label: 'Username', type: 'text', placeholder: 'Enter username' },
  { name: 'email', label: 'Email', type: 'email', placeholder: 'Enter email address' },
  { name: 'password', label: 'Password', type: 'password', placeholder: 'Enter password' },
]

export default function App() {
  const [form, setForm] = useState(initialForm)
  const [status, setStatus] = useState({ type: 'idle', message: '' })
  const [isSubmitting, setIsSubmitting] = useState(false)

  const isDisabled = useMemo(
    () => !form.username.trim() || !form.email.trim() || !form.password.trim() || isSubmitting,
    [form, isSubmitting],
  )

  // Sync the form state with user input as they type.
  const handleChange = (event) => {
    const { name, value } = event.target
    setForm((prev) => ({ ...prev, [name]: value }))
  }

  // Clear any prior form submission messages before the next action.
  const resetStatus = () => setStatus({ type: 'idle', message: '' })

  // Verify that fetched credentials match what the user entered.
  const validateCredentials = (user) => {
    const usernameMatches = user.username === form.username
    const emailMatches = user.email === form.email
    const passwordMatches = user.password === form.password
    return usernameMatches && emailMatches && passwordMatches
  }

  // Retrieve the server-side user record for the provided email.
  const fetchUser = async () => {
    const response = await fetch(`${API_BASE_URL}/users?email=${encodeURIComponent(form.email)}`)
    if (!response.ok) {
      throw new Error('User not found or service unavailable.')
    }
    return response.json()
  }

  // Record the login attempt for auditing and analytics.
  const recordLogin = async () => {
    await fetch(`${API_BASE_URL}/logins/add`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ username: form.username, email: form.email }),
    })
  }

  // Submit the sign-in form, validate credentials, and handle errors gracefully.
  const handleSubmit = async (event) => {
    event.preventDefault()
    resetStatus()
    setIsSubmitting(true)

    try {
      const user = await fetchUser()
      if (!validateCredentials(user)) {
        setStatus({ type: 'error', message: 'Username, email, or password did not match.' })
        setIsSubmitting(false)
        return
      }

      await recordLogin()
      setStatus({ type: 'success', message: 'Login successful. Welcome back!' })
      setForm(initialForm)
    } catch (error) {
      setStatus({ type: 'error', message: error.message || 'Login failed.' })
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="page">
      <section className="panel">
        <div className="header">
          <div>
            <p className="eyebrow">Kafka Consumer Portal</p>
            <h1>Sign in to continue</h1>
          </div>
          <span className="badge">v1</span>
        </div>

        <form className="form" onSubmit={handleSubmit}>
          {formFields.map((field) => (
            <label key={field.name} className="field">
              <span>{field.label}</span>
              <input
                name={field.name}
                type={field.type}
                placeholder={field.placeholder}
                value={form[field.name]}
                onChange={handleChange}
                onFocus={resetStatus}
                required
              />
            </label>
          ))}

          <button type="submit" className="submit" disabled={isDisabled}>
            {isSubmitting ? 'Signing in…' : 'Sign in'}
          </button>
        </form>

        {status.message ? (
          <div className={`status status-${status.type}`} role="status">
            {status.message}
          </div>
        ) : null}

        <p className="hint">
          The form checks existing users through <code>/api/users?email=</code> and logs successful attempts to
          <code>/api/logins/add</code>.
        </p>
      </section>
    </div>
  )
}
