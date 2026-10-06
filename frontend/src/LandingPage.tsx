import { useEffect, useState } from "react";
import "./landing.css";

type LandingPageProps = {
  onStart: () => void;
};

const investigationStages = [
  { label: "Incident detected", value: "API latency", metric: "+420%" },
  { label: "Evidence found", value: "3 correlated signals", metric: "00:12" },
  { label: "Likely root cause", value: "DB pool exhaustion", metric: "87%" },
];

const timelineEvents = [
  { time: "10:42", title: "Deployment", detail: "Connection pool configuration changed", code: "deploy.api@8f4a2" },
  { time: "10:47", title: "Connection usage ↑", detail: "Pool utilization reaches 82%", code: "active_connections=82" },
  { time: "10:51", title: "Database errors", detail: "Pool timeout errors begin", code: "db.pool.timeout +4.2×" },
  { time: "10:54", title: "Incident detected", detail: "Latency crosses the alert threshold", code: "p95_latency=1840ms" },
];

const evidenceItems = [
  { text: "Connection errors increased 4.2×", event: 2 },
  { text: "Pool utilization reached 98%", event: 1 },
  { text: "Error spike followed deployment", event: 0 },
];

function Arrow() {
  return (
    <svg aria-hidden="true" width="17" height="17" viewBox="0 0 20 20" fill="none">
      <path d="M4 10h11m-4-4 4 4-4 4" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

function SignalMark({ muted = false }: { muted?: boolean }) {
  return (
    <svg aria-hidden="true" width="16" height="16" viewBox="0 0 20 20" fill="none">
      <circle cx="10" cy="10" r="7" stroke="currentColor" strokeWidth="1.4" />
      {!muted && <path d="m6.7 10.2 2.1 2 4.5-4.6" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />}
    </svg>
  );
}

export default function LandingPage({ onStart }: LandingPageProps) {
  const [scrolled, setScrolled] = useState(false);
  const [activeStage, setActiveStage] = useState(0);
  const [activeStep, setActiveStep] = useState(0);
  const [activeTimeline, setActiveTimeline] = useState(2);
  const [activeEvidence, setActiveEvidence] = useState(0);
  const [mobileNav, setMobileNav] = useState(false);

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 20);
    handleScroll();
    window.addEventListener("scroll", handleScroll, { passive: true });

    const revealObserver = new IntersectionObserver(
      (entries) => entries.forEach((entry) => entry.isIntersecting && entry.target.classList.add("is-visible")),
      { threshold: 0.14 },
    );
    document.querySelectorAll(".landing-reveal").forEach((element) => revealObserver.observe(element));

    const stageTimer = window.setInterval(() => {
      setActiveStage((current) => (current + 1) % investigationStages.length);
    }, 1900);

    return () => {
      window.removeEventListener("scroll", handleScroll);
      revealObserver.disconnect();
      window.clearInterval(stageTimer);
    };
  }, []);

  const chooseEvidence = (index: number) => {
    setActiveEvidence(index);
    setActiveTimeline(evidenceItems[index].event);
  };

  const scrollTo = (id: string) => {
    document.getElementById(id)?.scrollIntoView({ behavior: "smooth" });
    setMobileNav(false);
  };

  return (
    <div className="landing">
      <header className={`landing-nav ${scrolled ? "scrolled" : ""}`}>
        <div className="landing-container nav-content">
          <button type="button" className="landing-wordmark" onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}>
            <span>RCA</span><strong>Analyzer</strong>
          </button>
          <button type="button" className="mobile-menu" onClick={() => setMobileNav((value) => !value)} aria-label="Toggle navigation">
            <span></span><span></span>
          </button>
          <nav className={mobileNav ? "open" : ""}>
            <button type="button" onClick={() => scrollTo("product")}>Product</button>
            <button type="button" onClick={() => scrollTo("how-it-works")}>How it works</button>
            <button type="button" onClick={() => scrollTo("evidence")}>Evidence</button>
            <button type="button" onClick={() => scrollTo("about")}>About</button>
          </nav>
          <div className="nav-actions">
            <button type="button" className="nav-sign-in">Sign in</button>
            <button type="button" className="landing-button small" onClick={onStart}>Start investigating <Arrow /></button>
          </div>
        </div>
      </header>

      <main>
        <section className="landing-hero" id="product">
          <div className="hero-grid-texture" aria-hidden="true"></div>
          <div className="landing-container hero-layout">
            <div className="hero-copy landing-reveal">
              <span className="landing-eyebrow"><i></i> Root cause analysis</span>
              <h1>Find out<br />what actually<br /><em>broke.</em></h1>
              <p>Turn production events into evidence-backed root cause hypotheses — without guessing.</p>
              <div className="hero-actions">
                <button type="button" className="landing-button" onClick={onStart}>Start an investigation <Arrow /></button>
                <button type="button" className="landing-button secondary" onClick={() => scrollTo("how-it-works")}>Explore how it works</button>
              </div>
              <div className="hero-trust">
                <span>Evidence first</span><span>Explainable results</span><span>Engineering validated</span>
              </div>
            </div>

            <div className="investigation-visual landing-reveal" aria-label="Live root cause investigation preview">
              <div className="visual-header">
                <div><span className="live-dot"></span><span>Investigation running</span></div>
                <code>RCA-0241</code>
              </div>
              <div className="visual-canvas">
                <div className="incident-source">
                  <span>Production incident</span>
                  <strong>Checkout API degradation</strong>
                  <div><code>10:54:12 UTC</code><b>Investigating</b></div>
                </div>
                <div className="investigation-path" aria-hidden="true"><span></span><i></i><span></span></div>
                <div className="stage-stack">
                  {investigationStages.map((stage, index) => (
                    <button
                      type="button"
                      className={`investigation-stage ${activeStage === index ? "active" : ""} ${activeStage > index ? "complete" : ""}`}
                      key={stage.label}
                      onClick={() => setActiveStage(index)}
                    >
                      <span className="stage-index">0{index + 1}</span>
                      <span className="stage-copy"><small>{stage.label}</small><strong>{stage.value}</strong></span>
                      <code>{stage.metric}</code>
                    </button>
                  ))}
                </div>
                <div className="signal-stream" aria-hidden="true">
                  {[18, 26, 20, 38, 31, 56, 68, 52, 76, 62, 84, 79].map((height, index) => <i key={index} style={{ height: `${height}%`, animationDelay: `${index * 70}ms` }}></i>)}
                </div>
              </div>
              <div className="visual-footer">
                <span><i></i> 248 events analyzed</span>
                <span>Completed in 12.4s</span>
              </div>
            </div>
          </div>
        </section>

        <section className="problem-section landing-section landing-reveal">
          <div className="landing-container">
            <div className="problem-heading">
              <span className="section-number">01 / Signal</span>
              <h2>Production tells you <em>what</em> happened.<br />Not <strong>why.</strong></h2>
            </div>
            <div className="signal-layout">
              <div className="signal-metrics">
                <div><span>Latency</span><strong>↑ 420%</strong><small>p95 · 1,840ms</small></div>
                <div><span>Error rate</span><strong>↑ 38%</strong><small>5xx responses</small></div>
                <div><span>Database load</span><strong>98%</strong><small>pool utilization</small></div>
              </div>
              <div className="signal-connector"><span></span><i></i></div>
              <div className="cause-prompt"><span>Next question</span><strong>Now find<br />the cause.</strong><button type="button" onClick={onStart}>Investigate <Arrow /></button></div>
            </div>
          </div>
        </section>

        <section className="how-section landing-section" id="how-it-works">
          <div className="landing-container">
            <div className="section-intro landing-reveal">
              <span className="section-number">02 / Method</span>
              <h2>From incident<br />to explanation.</h2>
              <p>A structured investigation that keeps evidence, timing, and competing explanations connected.</p>
            </div>
            <div className="method-workbench landing-reveal">
              <div className="method-steps">
                {[
                  ["Ingest", "Bring in production events.", "Normalize logs, metrics, notes, and operational context."],
                  ["Trace", "Build the incident timeline.", "Align every signal around the first sustained deviation."],
                  ["Compare", "Evaluate competing hypotheses.", "Test what supports and contradicts each possible cause."],
                  ["Explain", "Surface the strongest evidence.", "Produce a traceable conclusion with verification actions."],
                ].map(([title, summary, detail], index) => (
                  <button type="button" key={title} className={activeStep === index ? "active" : ""} onMouseEnter={() => setActiveStep(index)} onFocus={() => setActiveStep(index)} onClick={() => setActiveStep(index)}>
                    <span>0{index + 1}</span><div><strong>{title}</strong><p>{summary}</p><small>{detail}</small></div><Arrow />
                  </button>
                ))}
              </div>
              <div className={`method-visual method-${activeStep}`}>
                <div className="method-visual-top"><span>Analysis pipeline</span><code>STEP 0{activeStep + 1}</code></div>
                <div className="pipeline">
                  {["events.csv", "timeline", "evidence", "hypothesis"].map((item, index) => (
                    <div key={item} className={index <= activeStep ? "active" : ""}><span>{index < activeStep ? "✓" : index + 1}</span><code>{item}</code></div>
                  ))}
                  <i style={{ width: `${activeStep * 33.333}%` }}></i>
                </div>
                <div className="method-output">
                  <span>Current operation</span>
                  <strong>{["Reading 248 production events", "Correlating signals by time", "Scoring three explanations", "Preparing evidence-backed report"][activeStep]}</strong>
                  <div><i></i><i></i><i></i><i></i><i></i></div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section className="evidence-section landing-section" id="evidence">
          <div className="landing-container evidence-layout">
            <div className="evidence-copy landing-reveal">
              <span className="section-number">03 / Evidence-first AI</span>
              <h2>AI shouldn't just give you an answer.</h2>
              <p>It should show<br /><strong>you why.</strong></p>
              <span className="evidence-note">Every conclusion links back to an observable signal, its source, and its place in the incident timeline.</span>
            </div>
            <div className="result-panel landing-reveal">
              <div className="result-header"><span>Root cause analysis</span><code>RCA-0241</code></div>
              <div className="result-primary">
                <span>Likely root cause</span><strong>Database connection<br />pool exhaustion</strong>
                <div><span>Confidence</span><b>87%</b><i><em></em></i></div>
              </div>
              <div className="result-evidence">
                <span>Supporting evidence</span>
                {evidenceItems.map((item, index) => (
                  <button type="button" key={item.text} className={activeEvidence === index ? "active" : ""} onClick={() => chooseEvidence(index)}>
                    <SignalMark /><span><strong>{item.text}</strong><small>Connected to event at {timelineEvents[item.event].time}</small></span><Arrow />
                  </button>
                ))}
              </div>
              <div className="result-contradiction"><SignalMark muted /><span><small>Contradicting evidence</small><strong>No network degradation detected</strong></span></div>
            </div>
          </div>
        </section>

        <section className="timeline-section landing-section">
          <div className="landing-container">
            <div className="section-intro timeline-intro landing-reveal">
              <span className="section-number">04 / Timeline</span>
              <h2>See the sequence.<br />Follow the signal.</h2>
              <p>Evidence only makes sense in time. Move through the incident to inspect what changed, and when.</p>
            </div>
            <div className="landing-timeline landing-reveal">
              <div className="timeline-line" aria-hidden="true"></div>
              {timelineEvents.map((event, index) => (
                <button type="button" key={event.time} className={activeTimeline === index ? "active" : ""} onMouseEnter={() => setActiveTimeline(index)} onFocus={() => setActiveTimeline(index)} onClick={() => setActiveTimeline(index)}>
                  <time>{event.time}</time><i></i><span><strong>{event.title}</strong><small>{event.detail}</small><code>{event.code}</code></span>
                </button>
              ))}
            </div>
            <div className="timeline-detail landing-reveal">
              <span>Selected event · {timelineEvents[activeTimeline].time}</span>
              <strong>{timelineEvents[activeTimeline].title}</strong>
              <p>{timelineEvents[activeTimeline].detail}</p>
              <code>{timelineEvents[activeTimeline].code}</code>
            </div>
          </div>
        </section>

        <section className="principles-section landing-section" id="about">
          <div className="landing-container">
            <div className="principles-header landing-reveal"><span className="section-number">05 / Why RCA Analyzer</span><h2>Built for the questions<br />that follow an incident.</h2></div>
            <div className="principles">
              {[
                ["Evidence over guesswork", "Every hypothesis is backed by observable signals."],
                ["Competing causes", "Compare multiple explanations instead of locking onto the first one."],
                ["Traceable decisions", "See how the system reached its conclusion."],
              ].map(([title, body], index) => (
                <div className="landing-reveal" key={title}><span>0{index + 1}</span><svg aria-hidden="true" viewBox="0 0 120 42"><path d={index === 0 ? "M2 31 28 20l22 7 25-19 43 6" : index === 1 ? "M2 21h27l20-12 21 25 23-18h25" : "M2 33 28 10l27 21 28-20 35 8"} /></svg><h3>{title}</h3><p>{body}</p></div>
              ))}
            </div>
          </div>
        </section>

        <section className="final-cta landing-section">
          <div className="landing-container landing-reveal">
            <span className="landing-eyebrow"><i></i> Begin the investigation</span>
            <h2>Your next incident<br />already has a story.</h2>
            <p>Start with the data. Follow the evidence.</p>
            <button type="button" className="landing-button cream" onClick={onStart}>Start an investigation <Arrow /></button>
          </div>
        </section>
      </main>

      <footer className="landing-footer">
        <div className="landing-container">
          <div><div className="landing-wordmark"><span>RCA</span><strong>Analyzer</strong></div><p>Root cause analysis for production systems.</p></div>
          <nav><button type="button" onClick={() => scrollTo("product")}>Product</button><button type="button" onClick={() => scrollTo("how-it-works")}>How it works</button><button type="button">Documentation</button><button type="button">GitHub</button><button type="button">Contact</button></nav>
          <span>© 2026 RCA Analyzer</span>
        </div>
      </footer>
    </div>
  );
}
