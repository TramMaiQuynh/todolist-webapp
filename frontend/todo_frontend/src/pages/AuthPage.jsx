import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';
import { errorMessage, fieldErrors } from '../api/errors';
import Brand from '../components/Brand';

const CONFIG = {
  login: {
    title: 'Sign in',
    submit: 'Sign in',
    alt: { text: "Don't have an account?", to: '/register', label: 'Create one' },
  },
  register: {
    title: 'Create your account',
    submit: 'Sign up',
    alt: { text: 'Already registered?', to: '/login', label: 'Sign in' },
  },
};

const AuthPage = ({ mode }) => {
  const { login, register } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const config = CONFIG[mode];
  const [values, setValues] = useState({ login: '', username: '', email: '', password: '' });
  const [errors, setErrors] = useState({});
  const [formError, setFormError] = useState('');
  const [busy, setBusy] = useState(false);

  const onChange = (e) => setValues((prev) => ({ ...prev, [e.target.name]: e.target.value }));

  const submit = async (e) => {
    e.preventDefault();
    setBusy(true);
    setErrors({});
    setFormError('');
    try {
      if (mode === 'login') {
        await login({ login: values.login, password: values.password });
      } else {
        await register({ username: values.username, email: values.email, password: values.password });
      }
      navigate(location.state?.from?.pathname || '/app', { replace: true });
    } catch (err) {
      const fields = fieldErrors(err);
      setErrors(fields);
      if (!Object.keys(fields).length || fields.non_field_errors) {
        setFormError(errorMessage(err));
      }
    } finally {
      setBusy(false);
    }
  };

  // Hàm render (không phải component) để input không bị mount lại mỗi lần gõ
  const renderField = ({ name, label, type = 'text', autoComplete }) => (
    <label className="field" key={name}>
      <span>{label}</span>
      <input name={name} type={type} value={values[name]} onChange={onChange} required
             autoComplete={autoComplete} />
      {errors[name] && <span className="field-error" role="alert">{errors[name]}</span>}
    </label>
  );

  return (
    <main className="auth-page">
      <Link to="/" className="auth-brand"><Brand /></Link>
      <div className="auth-shell">
        <aside className="auth-aside">
          <span className="auth-aside-mark" aria-hidden="true">✳</span>
          <p className="eyebrow">A CLEARER KIND OF PRODUCTIVITY</p>
          <h2>One thing at a time.</h2>
          <p>Your plans, priorities and everyday progress — all in one calm place.</p>
          <div className="auth-aside-lines"><span /><span /><span /></div>
        </aside>
        <form className="auth-card" onSubmit={submit}>
        <h1>{config.title}</h1>
        <p className="auth-intro">{mode === 'login' ? 'Welcome back. Pick up where you left off.' : 'Create an account and make today yours.'}</p>
        {mode === 'login' ? (
          renderField({ name: 'login', label: 'Username or email', autoComplete: 'username' })
        ) : (
          <>
            {renderField({ name: 'username', label: 'Username', autoComplete: 'username' })}
            {renderField({ name: 'email', label: 'Email', type: 'email', autoComplete: 'email' })}
          </>
        )}
        {renderField({
          name: 'password',
          label: 'Password',
          type: 'password',
          autoComplete: mode === 'login' ? 'current-password' : 'new-password',
        })}
        {mode === 'register' && <small className="hint">At least 8 characters, not too common.</small>}
        {formError && <p className="notice error" role="alert">{formError}</p>}
        <button type="submit" className="btn primary" disabled={busy}>
          {busy ? 'Please wait…' : config.submit}
        </button>
        <p className="muted">{config.alt.text} <Link to={config.alt.to}>{config.alt.label}</Link></p>
        </form>
      </div>
      <Link className="auth-back" to="/">← Back to home</Link>
    </main>
  );
};

export default AuthPage;
