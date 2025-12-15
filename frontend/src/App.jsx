import { useMemo, useState } from 'react';
import { fetchUserByEmail, logLogin } from './api.js';
import './App.css';

const initialForm = {
  username: '',
  email: '',
  password: '',
};

function App() {
  const [form, setForm] = useState(initialForm);
  const [status, setStatus] = useState({ type: '', message: '' });
  const [isSubmitting, setIsSubmitting] = useState(false);

  const isFormValid = useMemo(
    () => form.username.trim() && form.email.trim() && form.password.trim(),
    [form]
  );

  const handleChange = (event) => {
    const { name, value } = event.target;
    setForm((current) => ({ ...current, [name]: value }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    if (!isFormValid || isSubmitting) return;

    setIsSubmitting(true);
    setStatus({ type: '', message: '' });

    try {
      const user = await fetchUserByEmail(form.email.trim());

      if (!user || user.username !== form.username.trim()) {
        setStatus({ type: 'error', message: 'No matching user found for the provided credentials.' });
        return;
      }

      if (user.password !== form.password.trim()) {
        setStatus({ type: 'error', message: 'Password is incorrect.' });
        return;
      }

      await logLogin({ username: form.username.trim(), email: form.email.trim() });

      setStatus({ type: 'success', message: 'Login successful and recorded.' });
      setForm(initialForm);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unexpected error occurred.';
      setStatus({ type: 'error', message: errorMessage });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <main className="page">
      <section className="card">
        <h1 className="title">Log in to continue</h1>
        <p className="hint">Enter your username, email, and password to record a login.</p>

        <form className="form" onSubmit={handleSubmit}>
          <label className="label">
            <span>Username</span>
            <input
              type="text"
              name="username"
              value={form.username}
              onChange={handleChange}
              autoComplete="username"
              placeholder="jane_doe"
              required
            />
          </label>

          <label className="label">
            <span>Email</span>
            <input
              type="email"
              name="email"
              value={form.email}
              onChange={handleChange}
              autoComplete="email"
              placeholder="jane@example.com"
              required
            />
          </label>

          <label className="label">
            <span>Password</span>
            <input
              type="password"
              name="password"
              value={form.password}
              onChange={handleChange}
              autoComplete="current-password"
              placeholder="••••••••"
              required
            />
          </label>

          <button className="submit" type="submit" disabled={!isFormValid || isSubmitting}>
            {isSubmitting ? 'Submitting…' : 'Log in'}
          </button>
        </form>

        {status.message && (
          <div className={`alert ${status.type}`} role={status.type === 'error' ? 'alert' : 'status'}>
            {status.message}
          </div>
        )}
      </section>
    </main>
  );
}

export default App;
