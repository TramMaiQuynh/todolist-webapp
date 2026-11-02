import React from 'react';
import { Link } from 'react-router-dom';
import Button from '../components/Button';
import Brand from '../components/Brand';

const HomePage = () => {
  return (
    <div className="landing-page">
      <header className="landing-nav">
        <Link to="/" aria-label="Daymark home"><Brand /></Link>
        <nav aria-label="Account">
          <Link className="landing-signin" to="/login">Sign in</Link>
          <Button />
        </nav>
      </header>

      <main>
        <section className="landing-hero">
          <div className="hero-copy">
            <span className="eyebrow"><span className="eyebrow-dot" /> A calmer way to get things done</span>
            <h1>Make room for what <em>matters.</em></h1>
            <p className="hero-description">
              A thoughtful place for your tasks, plans and everyday progress. Keep the important things in view, one day at a time.
            </p>
            <div className="hero-actions">
              <Button />
              <span className="hero-note">Free to use · Easy to return to</span>
            </div>
            <div className="hero-values" aria-label="Product highlights">
              <span><b>01</b> Clear priorities</span>
              <span><b>02</b> Gentle structure</span>
              <span><b>03</b> Your pace</span>
            </div>
          </div>

          <div className="hero-art" aria-label="A preview of a focused task list">
            <div className="art-glow" />
            <div className="preview-card">
              <div className="preview-topline">
                <span className="preview-date">MONDAY, 9:41 AM</span>
                <span className="preview-avatar">A</span>
              </div>
              <p className="preview-greeting">A fresh start.</p>
              <h2>Today <span>03</span></h2>
              <div className="preview-task is-done">
                <span className="preview-check">✓</span>
                <span>Clear the little things</span>
                <small>DONE</small>
              </div>
              <div className="preview-task">
                <span className="preview-check" />
                <span>Make a plan for the week</span>
                <small>FOCUS</small>
              </div>
              <div className="preview-task">
                <span className="preview-check" />
                <span>Take a proper lunch break</span>
                <small>PERSONAL</small>
              </div>
              <div className="preview-footer"><span className="preview-progress"><i /></span><span>1 of 3 complete</span></div>
            </div>
            <div className="art-note"><span className="art-note-star">✳</span><span>One thing<br />at a time.</span></div>
            <div className="art-orbit orbit-one" />
            <div className="art-orbit orbit-two" />
          </div>
        </section>

        <section className="landing-bottom">
          <span>LESS NOISE. MORE MEANING.</span>
          <p>Keep your days moving, without making them feel busier.</p>
        </section>
      </main>
    </div>
  );
};

export default HomePage;
