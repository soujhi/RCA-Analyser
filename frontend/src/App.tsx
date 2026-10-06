import { useEffect, useRef, useState, type ReactNode } from "react";
import LandingPage from "./LandingPage";

type Screen = 0 | 1 | 2 | 3 | 4 | 5;
type IconKind = "check" | "cross" | "question" | "info" | "arrow" | "download";
type CategoryName =
  | "Machine"
  | "Material"
  | "Method"
  | "Measurement"
  | "People"
  | "Environment";

const stepLabels = ["Input", "Data", "Timeline", "Evidence", "Hypotheses", "Report"];
const stepDescriptions = [
  "Choose a sample or import production data",
  "Validate structure, timing, and gaps",
  "Review the incident sequence",
  "Inspect and filter computed signals",
  "Compare ranked possible causes",
  "Prepare the engineering report",
];

const categories: Record<CategoryName, { short: string; className: string }> = {
  Machine: { short: "M", className: "machine" },
  Material: { short: "Ma", className: "material" },
  Method: { short: "Me", className: "method" },
  Measurement: { short: "Ms", className: "measurement" },
  People: { short: "P", className: "people" },
  Environment: { short: "E", className: "environment" },
};

const SAMPLE_DATASETS = [
  {
    title: "Clear cause",
    context: "Line 3 · Night shift",
    description: "Strong evidence points to sustained high oven temperature",
    file: "incident-line-3.csv",
    readings: "248",
    timeSpan: "8h 14m",
    timeRange: "02:00 to 10:14",
    cadence: "2 min",
    thingsToKnow: "1",
    warning: "3 rows are missing temperature readings.",
    warningDetail: "They remain in the timeline, but will not be used for temperature comparisons.",
    rows: [
      ["02:00", "178°C", "0.4", "0 min", "Line stable"],
      ["02:03", "181°C", "0.5", "0 min", "Defect onset"],
      ["02:07", "193°C", "1.8", "4 min", "Temperature warning"],
      ["02:11", "201°C", "3.8", "7 min", "Operator adjustment"],
      ["02:15", "204°C", "4.2", "0 min", "Peak temperature"],
      ["02:19", "203°C", "3.9", "6 min", "Short line stop"],
    ],
    callout: "Defects rose from 0.5 to 3.8 per row starting at 02:03. Oven temperature crossed 195°C operating threshold 4 minutes later.",
    stats: { defects: "183", downtime: "47 min", stops: "6", events: "3" },
    axis: ["02:00", "02:05", "02:10", "02:15", "02:20"],
    incidentOnset: "Incident begins · 02:03",
    defectBars: [8, 9, 12, 25, 48, 72, 80, 65, 70, 54, 45],
    downtimeBars: [0, 0, 10, 34, 0, 48, 15, 0, 36, 0, 20],
    events: [
      { time: "02:03", title: "Defect rise detected", detail: "Defects increased from 0.5 to 1.8 per reading.", log: "defect_rate=1.8  baseline=0.5  delta=+260%" },
      { time: "02:07", title: "Temperature warning", detail: "Oven temperature crossed the 195°C operating threshold.", log: "oven_temp=193°C  target=178°C  state=warning" },
      { time: "02:11", title: "Operator adjustment", detail: "Manual controller adjustment recorded by night shift.", log: "controller_offset=-4.0  actor=operator_17  mode=manual" },
      { time: "02:19", title: "Short line stop", detail: "Line stopped for 6 minutes after recurring defects.", log: "downtime=6m  reason=quality_hold  defects=3.9" },
    ],
    lanes: [
      { name: "Machine" as CategoryName, items: [{ text: "Oven temperature exceeded 195°C for 37 minutes.", id: "E-04" }, { text: "Temperature rose after defects had already increased.", id: "E-07" }] },
      { name: "Material" as CategoryName, items: [{ text: "Material lot M-442 entered the line at 02:42.", id: "E-11" }, { text: "The same lot ran without defects on Line 1.", id: "E-13" }] },
      { name: "Method" as CategoryName, items: [], empty: "Nothing recorded. Worth checking whether operating recipe changed." },
      { name: "Measurement" as CategoryName, items: [], empty: "Nothing recorded. Worth checking sensor calibration before trusting readings." },
      { name: "People" as CategoryName, items: [{ text: "The night-shift team recorded two manual adjustments.", id: "E-17" }] },
      { name: "Environment" as CategoryName, items: [], empty: "Nothing recorded. Worth checking ambient temperature and humidity." },
    ],
    verdict: { title: "Ranked", detail: "One candidate has strong support. Two alternatives remain possible, but the timeline weighs against them." },
    hypotheses: [
      { rank: "H1", category: "Machine" as CategoryName, title: "Oven temperature ran high", score: 0.95, description: "The strongest evidence points to sustained high oven temperature during the defect period.", against: "Defects began 4 minutes before temperature crossed 195°C.", unchecked: "Verify oven controller and sensor calibration." },
      { rank: "H2", category: "Material" as CategoryName, title: "Material lot M-442 varied", score: 0.38, description: "The material change overlaps with the event, but timing and comparison line weaken the case.", against: "It began 39 min after defects had already risen.", unchecked: "Run retained sample from lot M-442 under standard conditions." },
      { rank: "H3", category: "People" as CategoryName, title: "Manual adjustments amplified event", score: 0.21, description: "Adjustments appear in the record, but only after event was already underway.", against: "Both recorded adjustments happened after first sustained defect rise.", unchecked: "Review operator log and shift handover." },
    ],
    problem: "Defect rate increased from 0.5 to 3.8 per reading on Line 3 from 02:03, resulting in 47 minutes of downtime during the night shift.",
    whys: [
      ["Why did defects increase?", "Product was exposed to oven temperatures above the expected operating range."],
      ["Why was the oven temperature high?", "The controller did not return the oven to its target after the rise."],
      ["Why did the controller not recover?", "The available data does not record controller output or sensor calibration."],
      ["Why was that not detected sooner?", "No verified alert response is present in the event file."],
      ["What is the underlying cause?", "Not determinable from this data. Complete the verification actions below."],
    ],
    actions: [
      ["Verify oven controller output against a calibrated reference.", "Controls engineer", "Tomorrow", "H1"],
      ["Run retained lot M-442 under standard conditions.", "Quality lead", "Fri, 11 Oct", "H2"],
      ["Review shift handover and operator adjustments.", "Shift manager", "Fri, 11 Oct", "H3"],
    ]
  },
  {
    title: "Competing causes",
    context: "Line 1 · Day shift (Two suspects)",
    description: "Material batch switch and feeder frequency drop occurred together",
    file: "incident-line-1-day.csv",
    readings: "312",
    timeSpan: "6h 30m",
    timeRange: "09:00 to 15:30",
    cadence: "1 min",
    thingsToKnow: "2",
    warning: "2 rows have uncalibrated feeder frequency readings.",
    warningDetail: "Feeder speed values during the 09:34-09:40 window carry elevated measurement uncertainty.",
    rows: [
      ["09:15", "175°C", "0.2", "0 min", "Batch R-801 active"],
      ["09:30", "176°C", "1.2", "3 min", "Batch R-802 switchover"],
      ["09:34", "175°C", "3.1", "8 min", "Feeder speed drop"],
      ["09:42", "188°C", "4.5", "12 min", "Feeder jam & alarm"],
      ["09:50", "182°C", "4.1", "15 min", "Manual reset attempt"],
      ["10:05", "177°C", "3.8", "0 min", "Feeder cleared"],
    ],
    callout: "Defects rose from 0.2 to 4.5 per row starting at 09:30. Raw material batch R-802 switch and feeder frequency drop occurred simultaneously.",
    stats: { defects: "245", downtime: "62 min", stops: "8", events: "4" },
    axis: ["09:15", "09:30", "09:45", "10:00", "10:15"],
    incidentOnset: "Incident begins · 09:30",
    defectBars: [12, 18, 42, 65, 88, 92, 75, 68, 55, 60, 40],
    downtimeBars: [0, 0, 15, 40, 20, 55, 30, 0, 45, 0, 15],
    events: [
      { time: "09:30", title: "Batch R-802 introduced", detail: "New resin batch loaded into hopper at shift transition.", log: "batch_id=R-802  supplier=PolyChem  viscosity=high" },
      { time: "09:34", title: "Feeder frequency drop", detail: "Feeder 2 motor drive frequency dropped by 18%.", log: "feeder_freq=41.2Hz  nominal=50.0Hz  delta=-17.6%" },
      { time: "09:42", title: "Major feeder jam", detail: "Line tripped on motor overload torque sensor.", log: "torque=24.8Nm  max=18.0Nm  state=tripped" },
      { time: "10:05", title: "Line restarted", detail: "Feeder cleared; defect rate remained elevated at 3.8/row.", log: "downtime=23m  restart=manual  defects=3.8" },
    ],
    lanes: [
      { name: "Machine" as CategoryName, items: [{ text: "Feeder 2 drive frequency dropped 18% at 09:34.", id: "E-02" }, { text: "Feeder motor current spiked to 24A during jam.", id: "E-05" }] },
      { name: "Material" as CategoryName, items: [{ text: "Raw material batch R-802 loaded at 09:30.", id: "E-10" }, { text: "Batch R-802 viscosity measured 15% higher than nominal.", id: "E-12" }] },
      { name: "Method" as CategoryName, items: [{ text: "Changeover procedure step 4 skipped during shift transition.", id: "E-15" }] },
      { name: "Measurement" as CategoryName, items: [], empty: "Nothing unusual recorded for sensor calibration." },
      { name: "People" as CategoryName, items: [], empty: "No operator manual override recorded prior to incident." },
      { name: "Environment" as CategoryName, items: [], empty: "Ambient conditions remained stable throughout." },
    ],
    verdict: { title: "Cannot separate", detail: "Two suspects. Two factors changed simultaneously at onset; data cannot isolate the primary driver without lab testing." },
    hypotheses: [
      { rank: "H1", category: "Material" as CategoryName, title: "Material batch R-802 viscosity anomaly", score: 0.68, description: "Batch R-802 arrived with 15% higher viscosity, coinciding directly with defect spike at 09:30.", against: "Feeder motor frequency also dropped 18% four minutes later.", unchecked: "Perform rheology test on retained sample of Batch R-802." },
      { rank: "H2", category: "Machine" as CategoryName, title: "Feeder drive frequency drop", score: 0.64, description: "Feeder 2 speed drop caused irregular dosing, leading to product jams and defects.", against: "Batch switchover occurred 4 minutes prior to feeder frequency drop.", unchecked: "Inspect Feeder 2 VFD drive parameter logs." },
      { rank: "H3", category: "Method" as CategoryName, title: "Skipped changeover protocol step", score: 0.35, description: "Step 4 (purge cycle) was omitted during shift transition, leaving residual material.", against: "Purge omission usually resolves after 10 minutes of run time.", unchecked: "Audit shift transition checklist for Line 1." },
    ],
    problem: "Defects increased from 0.2 to 4.5 per row on Line 1 starting at 09:30 during batch R-802 introduction, causing 62 minutes of total downtime.",
    whys: [
      ["Why did defects increase?", "Raw material flow became inconsistent during batch R-802 introduction."],
      ["Why was flow inconsistent?", "Feeder 2 experienced speed drops while processing higher viscosity resin."],
      ["Why did Feeder 2 drop frequency?", "Drive motor current hit safety limits due to increased melt resistance."],
      ["Why was high viscosity material loaded?", "Certificate of Analysis was accepted without secondary rheology verification."],
      ["What is the underlying cause?", "Cannot separate material viscosity variation from feeder drive degradation without lab testing."],
    ],
    actions: [
      ["Perform rheology lab test on retained sample of Batch R-802.", "Quality Engineer", "Today, 17:00", "H1"],
      ["Inspect Feeder 2 VFD drive motor and gear reducer.", "Maintenance Tech", "Tomorrow, 09:00", "H2"],
      ["Verify shift changeover purge compliance logs.", "Shift Supervisor", "Tomorrow, 12:00", "H3"],
    ]
  },
  {
    title: "Unclear incident",
    context: "Line 2 · Evening shift (No parameter drop)",
    description: "Transient defect spike resolved without physical sensor deviations",
    file: "incident-line-2-evening.csv",
    readings: "160",
    timeSpan: "4h 00m",
    timeRange: "14:00 to 18:00",
    cadence: "1.5 min",
    thingsToKnow: "0",
    warning: "No physical parameter deviations detected during incident window.",
    warningDetail: "All temperature, pressure, and speed channels recorded within nominal operating band.",
    rows: [
      ["14:00", "180°C", "0.1", "0 min", "Line running smooth"],
      ["14:30", "180°C", "0.2", "0 min", "Routine check"],
      ["15:15", "179°C", "0.1", "0 min", "Normal operation"],
      ["15:45", "181°C", "2.1", "5 min", "Transient defect warning"],
      ["16:15", "180°C", "0.3", "0 min", "Defects auto-resolved"],
      ["17:00", "180°C", "0.1", "0 min", "Line stable"],
    ],
    callout: "Transient defect spike of 2.1 per row observed at 15:45. Sensor signals remained nominal across all physical parameters.",
    stats: { defects: "64", downtime: "12 min", stops: "2", events: "1" },
    axis: ["14:00", "15:00", "16:00", "17:00", "18:00"],
    incidentOnset: "Incident begins · 15:45",
    defectBars: [5, 4, 6, 8, 42, 58, 24, 12, 8, 5, 4],
    downtimeBars: [0, 0, 0, 0, 25, 10, 0, 0, 0, 0, 0],
    events: [
      { time: "15:45", title: "Transient defect spike", detail: "Defect counter jumped from 0.1 to 2.1 per row.", log: "defects=2.1  baseline=0.1  duration=30m" },
      { time: "15:50", title: "Short inspection stop", detail: "Line paused for 5 minutes for visual quality verification.", log: "downtime=5m  inspector=QC_04  finding=no_part_defect" },
      { time: "16:10", title: "Optical sensor lens cleaned", detail: "Operator wiped optical defect counter lens.", log: "action=lens_clean  sensor=OPT_02  status=ok" },
      { time: "16:15", title: "Defect count returned to baseline", detail: "Defects dropped back to 0.3/row following lens wipe.", log: "defects=0.3  baseline=0.1  status=normal" },
    ],
    lanes: [
      { name: "Machine" as CategoryName, items: [{ text: "All machine sensors reported within ±1% nominal tolerance.", id: "E-01" }] },
      { name: "Material" as CategoryName, items: [], empty: "No material or lot changes recorded during evening shift." },
      { name: "Method" as CategoryName, items: [], empty: "Standard recipe parameters maintained without alteration." },
      { name: "Measurement" as CategoryName, items: [{ text: "Optical defect counter lens cleaned at 16:10.", id: "E-22" }] },
      { name: "People" as CategoryName, items: [], empty: "No operator adjustments logged during incident." },
      { name: "Environment" as CategoryName, items: [{ text: "Ambient humidity rose 8% due to HVAC cycle at 15:40.", id: "E-30" }] },
    ],
    verdict: { title: "Cannot determine", detail: "Cannot determine. No single parameter shows statistical correlation with the transient defect spike. Physical inspection required." },
    hypotheses: [
      { rank: "H1", category: "Measurement" as CategoryName, title: "Optical sensor lens contamination", score: 0.32, description: "Dust accumulation on optical lens caused false defect readings until cleaned at 16:10.", against: "No optical fault code was logged prior to manual cleaning.", unchecked: "Check optical sensor calibration and clean log." },
      { rank: "H2", category: "Environment" as CategoryName, title: "Transient ambient humidity fluctuation", score: 0.28, description: "HVAC cycle caused an 8% humidity bump, potentially affecting surface static.", against: "Humidity stayed within overall allowable plant envelope (45-55%).", unchecked: "Correlate HVAC cycling logs with line static sensors." },
      { rank: "H3", category: "Machine" as CategoryName, title: "Unrecorded micro-stop / material glitch", score: 0.25, description: "A brief unrecorded mechanical hesitation may have caused temporary part misalignment.", against: "Drive encoders recorded continuous speed throughout.", unchecked: "Inspect belt alignment and guide rail wear." },
    ],
    problem: "Transient defect spike of 2.1 per row recorded on Line 2 at 15:45 without associated sensor alarms, resulting in 12 minutes of downtime.",
    whys: [
      ["Why did defects increase?", "Optical quality counter registered elevated defect counts from 15:45 to 16:15."],
      ["Why did optical counter register defects?", "Lens surface accumulated dust particle film prior to manual cleaning."],
      ["Why did dust accumulate on sensor?", "Enclosure positive-pressure air purge line was turned off."],
      ["Why was purge line off?", "Maintenance valve was closed during prior preventive maintenance."],
      ["What is the underlying cause?", "Cannot determine with certainty without bench-testing optical sensor response."],
    ],
    actions: [
      ["Perform bench calibration and sensitivity test on Optical Sensor OPT_02.", "Automation Engineer", "Tomorrow, 10:00", "H1"],
      ["Check positive-pressure air purge line valve setting on sensor enclosure.", "Maintenance Lead", "Today, 18:00", "H1"],
      ["Correlate plant HVAC humidity cycles against optical sensor noise floor.", "Facilities Engineer", "Fri, 11 Oct", "H2"],
    ]
  }
];

function Icon({ kind, size = 18 }: { kind: IconKind; size?: number }) {
  if (kind === "arrow") {
    return (
      <svg aria-hidden="true" width={size} height={size} viewBox="0 0 24 24" fill="none">
        <path d="m9 18 6-6-6-6" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    );
  }
  if (kind === "download") {
    return (
      <svg aria-hidden="true" width={size} height={size} viewBox="0 0 24 24" fill="none">
        <path d="M12 3v12m0 0 4-4m-4 4-4-4M5 19h14" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    );
  }
  const glyph = kind === "check" ? "M8 12.5 10.7 15 16 9" : kind === "cross" ? "m9 9 6 6m0-6-6 6" : "";
  return (
    <svg aria-hidden="true" width={size} height={size} viewBox="0 0 24 24" fill="none">
      <circle cx="12" cy="12" r="8.5" stroke="currentColor" strokeWidth="1.6" strokeDasharray={kind === "question" ? "2.5 2.5" : undefined} />
      {kind === "info" && (
        <>
          <path d="M12 10.8v5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
          <circle cx="12" cy="7.7" r="1" fill="currentColor" />
        </>
      )}
      {kind === "question" && <text x="12" y="16" textAnchor="middle" fill="currentColor" fontSize="12" fontWeight="600">?</text>}
      {glyph && <path d={glyph} stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />}
    </svg>
  );
}

function Heading({ level = 2, children, className = "" }: { level?: 1 | 2 | 3; children: ReactNode; className?: string }) {
  const Tag = `h${level}` as const;
  return <Tag className={className}>{children}</Tag>;
}

function Button({
  children,
  variant = "secondary",
  onClick,
  className = "",
  disabled = false,
}: {
  children: ReactNode;
  variant?: "primary" | "secondary" | "sample" | "ghost";
  onClick?: () => void;
  className?: string;
  disabled?: boolean;
}) {
  return (
    <button type="button" className={`button ${variant} ${className}`} onClick={onClick} disabled={disabled}>
      {children}
    </button>
  );
}

function Navigation({ screen, onNavigate }: { screen: Screen; onNavigate: (screen: Screen) => void }) {
  return (
    <nav className="navigation" aria-label="RCA progress">
      <div className="brand" aria-label="RCA Analyzer">
        <span className="brand-mark" aria-hidden="true">
          <svg width="19" height="19" viewBox="0 0 20 20" fill="none">
            <path d="M4.5 5.5h11M4.5 10h7M4.5 14.5h9" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" />
            <circle cx="15.5" cy="10" r="1.5" fill="currentColor" />
          </svg>
        </span>
        <span>RCA Analyzer</span>
      </div>
      <div className="steps">
        {stepLabels.map((step, index) => (
          <button
            type="button"
            key={step}
            className={`step ${index === screen ? "current" : index < screen ? "done" : ""}`}
            onClick={() => onNavigate(index as Screen)}
            aria-current={index === screen ? "step" : undefined}
          >
            <span className="step-number">{index < screen ? "✓" : index + 1}</span>
            <span>{step}</span>
          </button>
        ))}
      </div>
    </nav>
  );
}

function Notice() {
  return (
    <div className="notice">
      <Icon kind="info" />
      <p>
        <strong>Hypotheses only.</strong> Engineering validation is required before any action. This tool never controls equipment and never declares a confirmed root cause. <span>Synthetic demo data. Fictional equipment and figures.</span>
      </p>
    </div>
  );
}

function Stat({ value, label }: { value: string; label: string }) {
  return (
    <div className="stat-card">
      <strong>{value}</strong>
      <span>{label}</span>
    </div>
  );
}

function CategoryChip({ name }: { name: CategoryName }) {
  const category = categories[name];
  return (
    <span className={`category-chip ${category.className}`}>
      <b>{category.short}</b>
      {name}
    </span>
  );
}

function Point({ kind, children }: { kind: "for" | "against" | "unchecked"; children: ReactNode }) {
  const icon = kind === "for" ? "check" : kind === "against" ? "cross" : "question";
  return (
    <li className={`point ${kind}`}>
      <Icon kind={icon} />
      <span>{children}</span>
    </li>
  );
}

function ScreenHeader({ eyebrow, title, description }: { eyebrow: string; title: string; description?: string }) {
  return (
    <header className="screen-header">
      <span className="eyebrow">{eyebrow}</span>
      <Heading level={1}>{title}</Heading>
      {description && <p>{description}</p>}
    </header>
  );
}

function ScreenActions({ onBack, onNext, nextLabel }: { onBack: () => void; onNext: () => void; nextLabel: string }) {
  return (
    <div className="screen-actions">
      <Button onClick={onBack}>Back</Button>
      <Button variant="primary" onClick={onNext}>
        {nextLabel}
        <Icon kind="arrow" />
      </Button>
    </div>
  );
}

function StartScreen({ onNext }: { onNext: (sampleIndex: number) => void }) {
  const [selectedSample, setSelectedSample] = useState(0);
  const [file, setFile] = useState<File | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [analysisStep, setAnalysisStep] = useState(0);

  const analysisStages = ["Reading data", "Building timeline", "Comparing evidence", "Ranking hypotheses", "Generating report"];
  const beginAnalysis = () => {
    if (analyzing) return;
    setAnalyzing(true);
    setAnalysisStep(0);
    analysisStages.forEach((_, index) => {
      window.setTimeout(() => setAnalysisStep(index), index * 380);
    });
    window.setTimeout(() => onNext(selectedSample), analysisStages.length * 380 + 250);
  };
  return (
    <>
      <section className="hero">
        <span className="eyebrow">Root cause analysis</span>
        <Heading level={1}>Analyze production incidents and identify the strongest evidence.</Heading>
        <p>Start with a sample investigation or import production data. The analyzer builds a timeline, tests possible causes, and prepares an engineering-ready report.</p>
      </section>
      <div className="start-grid">
      <section className="section sample-section">
        <div className="section-heading">
          <div><span className="section-kicker">Fast start</span><Heading level={2}>Sample incidents</Heading></div>
          <p>Fictional production events</p>
        </div>
        <div className="sample-list">
          {SAMPLE_DATASETS.map((sample, index) => (
            <button type="button" className={`sample-row ${selectedSample === index ? "selected" : ""}`} key={sample.title} onClick={() => setSelectedSample(index)}>
              <span className="sample-index">{String(index + 1).padStart(2, "0")}</span>
              <span className="sample-copy">
                <strong>{sample.title}</strong>
                <small>{sample.context}</small>
                <span>{sample.description}</span>
              </span>
              <span className="sample-action">{selectedSample === index ? "Selected" : "Select"} <Icon kind="arrow" /></span>
            </button>
          ))}
        </div>
        <div className="sample-footer">
          <span>Sample {String(selectedSample + 1).padStart(2, "0")} selected</span>
          <Button variant="primary" onClick={beginAnalysis}>Load incident <Icon kind="arrow" /></Button>
        </div>
      </section>
      <section className="section import-section">
        <div className="section-heading">
          <div><span className="section-kicker">Production data</span><Heading level={2}>Import incident</Heading></div>
        </div>
        <div
          className={`upload-panel ${file ? "has-file" : ""} ${dragActive ? "drag-active" : ""}`}
          onDragOver={(event) => { event.preventDefault(); setDragActive(true); }}
          onDragLeave={() => setDragActive(false)}
          onDrop={(event) => {
            event.preventDefault();
            setDragActive(false);
            const droppedFile = event.dataTransfer.files[0];
            if (droppedFile?.name.toLowerCase().endsWith(".csv")) setFile(droppedFile);
          }}
        >
          {!file ? (
            <>
              <div className="upload-copy">
                <span className="upload-icon"><svg aria-hidden="true" width="20" height="20" viewBox="0 0 24 24" fill="none"><path d="M12 15V4m0 0L8 8m4-4 4 4M5 14v5h14v-5" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" /></svg></span>
                <div><strong>Drop CSV here</strong><small>CSV · Up to 25 MB</small></div>
              </div>
              <label className="file-button">Browse files<input type="file" accept=".csv" onChange={(event) => setFile(event.target.files?.[0] ?? null)} /></label>
            </>
          ) : (
            <div className="file-ready">
              <span className="file-check"><Icon kind="check" /></span>
              <div><strong>{file.name}</strong><small>{Math.max(file.size / 1024 / 1024, 0.1).toFixed(1)} MB · CSV</small></div>
              <label className="text-action">Replace<input type="file" accept=".csv" onChange={(event) => setFile(event.target.files?.[0] ?? null)} /></label>
              <button type="button" className="text-action danger" onClick={() => setFile(null)}>Remove</button>
            </div>
          )}
        </div>
        <div className="import-footer">
          <div><span className={file ? "ready-dot active" : "ready-dot"}></span><span>{file ? "Ready to analyze" : "No file selected"}</span></div>
          <Button variant="primary" onClick={beginAnalysis} disabled={!file}>Analyze incident <Icon kind="arrow" /></Button>
        </div>
      </section>
      </div>
      {analyzing && (
        <div className="analysis-overlay" role="status" aria-live="polite">
          <div className="analysis-progress">
            <div className="progress-heading"><span>Analyzing incident</span><strong>{Math.round(((analysisStep + 1) / analysisStages.length) * 100)}%</strong></div>
            <div className="progress-track"><span style={{ width: `${((analysisStep + 1) / analysisStages.length) * 100}%` }} /></div>
            <div className="progress-stages">
              {analysisStages.map((stage, index) => <span key={stage} className={index < analysisStep ? "done" : index === analysisStep ? "active" : ""}>{index < analysisStep ? "✓" : "·"} {stage}</span>)}
            </div>
          </div>
        </div>
      )}
    </>
  );
}

function DataScreen({ data, onBack, onNext }: { data: typeof SAMPLE_DATASETS[0]; onBack: () => void; onNext: () => void }) {
  return (
    <>
      <Notice />
      <ScreenHeader eyebrow="Step 2 of 6 · Data check" title="Is the data ready?" description="We checked the structure, timing, and gaps before using any values as evidence." />
      <div className="stats-grid">
        <Stat value={data.readings} label="readings" />
        <Stat value={data.timeSpan} label="time span" />
        <Stat value={data.cadence} label="between readings" />
        <Stat value={data.thingsToKnow} label="things to know" />
      </div>
      <div className="status-card warning">
        <Icon kind="info" />
        <div><strong>{data.warning}</strong><p>{data.warningDetail}</p></div>
      </div>
      <section className="card table-card">
        <div className="card-header">
          <div><span className="section-kicker">First {data.rows.length} of {data.readings} rows</span><Heading level={2}>Data preview</Heading></div>
          <span className="file-badge">{data.file}</span>
        </div>
        <div className="table-wrap">
          <table>
            <thead><tr><th>Time</th><th>Parameter</th><th>Defects</th><th>Downtime</th><th>Note / Event</th></tr></thead>
            <tbody>{data.rows.map((row) => <tr key={row[0]}>{row.map((cell, i) => <td key={i}>{cell}</td>)}</tr>)}</tbody>
          </table>
        </div>
      </section>
      <ScreenActions onBack={onBack} onNext={onNext} nextLabel="Continue to timeline" />
    </>
  );
}

function TimelineChart({ data }: { data: typeof SAMPLE_DATASETS[0] }) {
  return (
    <div className="timeline-chart" role="img" aria-label={`Timeline showing oven temperature, defects per reading, and downtime from ${data.axis[0]} to ${data.axis[data.axis.length - 1]}`}>
      <div className="chart-labels">
        <span>Primary parameter <b>°C / Hz</b></span>
        <span>Defects per reading</span>
        <span>Downtime <b>min</b></span>
      </div>
      <div className="chart-canvas">
        <div className="incident-line"><span>{data.incidentOnset}</span></div>
        <svg viewBox="0 0 800 360" preserveAspectRatio="none" aria-hidden="true">
          <g className="grid-lines"><path d="M0 90H800M0 210H800M0 330H800" /></g>
          <path className="temp-line" d="M0 78 C80 76 120 72 170 70 S245 44 290 38 S420 30 500 34 S660 37 800 31" />
          <g className="defect-bars">
            {data.defectBars.map((height, i) => (
              <rect key={i} x={i * 72 + 14} y={204 - height} width="34" height={height} rx="3" />
            ))}
          </g>
          <g className="downtime-bars">
            {data.downtimeBars.map((height, i) => (
              <rect key={i} x={i * 72 + 14} y={325 - height} width="34" height={height} rx="3" />
            ))}
          </g>
          <g className="note-markers"><path d="M291 16l6 6-6 6-6-6zM507 16l6 6-6 6-6-6z" /></g>
        </svg>
        <div className="chart-axis">{data.axis.map((t) => <span key={t}>{t}</span>)}</div>
      </div>
    </div>
  );
}

function TimelineScreen({ data, onBack, onNext }: { data: typeof SAMPLE_DATASETS[0]; onBack: () => void; onNext: () => void }) {
  const [selectedEvent, setSelectedEvent] = useState(0);
  return (
    <>
      <Notice />
      <ScreenHeader eyebrow="Step 3 of 6 · Timeline" title="What happened" description="The event is aligned around the first sustained rise in defects." />
      <div className="finding-callout">
        <span className="finding-icon"><Icon kind="arrow" /></span>
        <p>{data.callout}</p>
      </div>
      <div className="stats-grid">
        <Stat value={data.stats.defects} label="defects in total" />
        <Stat value={data.stats.downtime} label="downtime" />
        <Stat value={data.stats.stops} label="stops" />
        <Stat value={data.stats.events} label="recurring events" />
      </div>
      <section className="card chart-card">
        <div className="card-header">
          <div><span className="section-kicker">{data.context}</span><Heading level={2}>Event timeline</Heading></div>
          <span className="legend-note"><i></i> Operator note</span>
        </div>
        <TimelineChart data={data} />
        <div className="event-explorer">
          <div className="event-list" aria-label="Timeline events">
            {data.events.map((event, index) => (
              <button type="button" key={event.time} className={selectedEvent === index ? "active" : ""} onClick={() => setSelectedEvent(index)}>
                <time>{event.time}</time><span><strong>{event.title}</strong><small>{event.detail}</small></span>
              </button>
            ))}
          </div>
          <div className="event-detail">
            <div><span className="log-level">Event detail</span><button type="button" title="Copy event log" onClick={() => navigator.clipboard?.writeText(data.events[selectedEvent].log)}>Copy</button></div>
            <strong>{data.events[selectedEvent].title}</strong>
            <p>{data.events[selectedEvent].detail}</p>
            <code>{data.events[selectedEvent].time}:00&nbsp; {data.events[selectedEvent].log}</code>
          </div>
        </div>
      </section>
      <ScreenActions onBack={onBack} onNext={onNext} nextLabel="Sort the evidence" />
    </>
  );
}

function EvidenceScreen({ data, onBack, onNext }: { data: typeof SAMPLE_DATASETS[0]; onBack: () => void; onNext: () => void }) {
  const [query, setQuery] = useState("");
  const [scope, setScope] = useState<"all" | "signals" | "empty">("all");
  const [selected, setSelected] = useState<{ text: string; id: string; category: CategoryName } | null>(null);
  const searchRef = useRef<HTMLInputElement>(null);
  useEffect(() => {
    const handleShortcut = (event: KeyboardEvent) => {
      if (event.key === "/" && document.activeElement?.tagName !== "INPUT" && document.activeElement?.tagName !== "TEXTAREA") {
        event.preventDefault();
        searchRef.current?.focus();
      }
      if (event.key === "Escape") setSelected(null);
    };
    window.addEventListener("keydown", handleShortcut);
    return () => window.removeEventListener("keydown", handleShortcut);
  }, []);
  const visibleLanes = data.lanes.filter((lane) => {
    const matchesScope = scope === "all" || (scope === "signals" ? lane.items.length > 0 : lane.items.length === 0);
    const normalizedQuery = query.trim().toLowerCase();
    const matchesQuery =
      !normalizedQuery ||
      lane.name.toLowerCase().includes(normalizedQuery) ||
      lane.items.some((item) => item.text.toLowerCase().includes(normalizedQuery) || item.id.toLowerCase().includes(normalizedQuery));
    return matchesScope && matchesQuery;
  });
  return (
    <>
      <Notice />
      <ScreenHeader eyebrow="Step 4 of 6 · Evidence" title="The evidence, sorted" description="Six places a cause can hide. Empty lanes are shown on purpose." />
      <div className="evidence-toolbar">
        <label className="search-field">
          <svg aria-hidden="true" width="16" height="16" viewBox="0 0 20 20" fill="none"><circle cx="8.5" cy="8.5" r="5.5" stroke="currentColor" strokeWidth="1.6" /><path d="m13 13 4 4" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" /></svg>
          <input ref={searchRef} value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search evidence or ID" />
          <kbd>/</kbd>
        </label>
        <div className="filter-group" aria-label="Filter evidence">
          {(["all", "signals", "empty"] as const).map((filter) => (
            <button type="button" key={filter} className={scope === filter ? "active" : ""} onClick={() => setScope(filter)}>
              {filter === "all" ? "All lanes" : filter === "signals" ? "With signals" : "Empty"}
            </button>
          ))}
        </div>
      </div>
      <div className="lane-grid">
        {visibleLanes.map((lane) => (
          <section className={`lane-card ${lane.items.length ? "" : "empty"}`} key={lane.name}>
            <div className="lane-header"><CategoryChip name={lane.name} /><span>{lane.items.length} {lane.items.length === 1 ? "signal" : "signals"}</span></div>
            {lane.items.length ? (
              <div className="evidence-list">
                {lane.items.map((item) => (
                  <button type="button" className="evidence-row" key={item.id} onClick={() => setSelected({ ...item, category: lane.name })}>
                    <span className="computed">computed</span>
                    <p>{item.text}</p>
                    <small>{item.id}</small>
                  </button>
                ))}
              </div>
            ) : (
              <div className="empty-state"><span>—</span><p>{lane.empty}</p></div>
            )}
          </section>
        ))}
      </div>
      {visibleLanes.length === 0 && <div className="no-results"><strong>No evidence found</strong><span>Try another search or clear the current filter.</span></div>}
      <ScreenActions onBack={onBack} onNext={onNext} nextLabel="Open the Evidence Court" />
      {selected && (
        <div className="panel-layer" role="presentation" onMouseDown={() => setSelected(null)}>
          <aside className="detail-panel" role="dialog" aria-modal="true" aria-label={`Evidence ${selected.id}`} onMouseDown={(event) => event.stopPropagation()}>
            <div className="panel-header">
              <div><span className="mono-label">{selected.id}</span><Heading level={2}>Evidence detail</Heading></div>
              <button type="button" className="icon-button" onClick={() => setSelected(null)} aria-label="Close evidence detail">×</button>
            </div>
            <div className="panel-content">
              <CategoryChip name={selected.category} />
              <div className="detail-section"><span>Observation</span><p>{selected.text}</p></div>
              <div className="detail-grid">
                <div><span>Source</span><strong>Incident timeline</strong></div>
                <div><span>Method</span><strong>Computed</strong></div>
                <div><span>Confidence</span><strong className="success-text">High</strong></div>
                <div><span>Analysis run</span><strong className="mono-value">RUN-248A</strong></div>
              </div>
              <div className="detail-section"><span>How this is used</span><p>This signal is evaluated against timing and competing explanations in Evidence Court.</p></div>
            </div>
            <div className="panel-footer"><Button onClick={() => setSelected(null)}>Close</Button><Button variant="primary" onClick={() => { setSelected(null); onNext(); }}>View in Evidence Court</Button></div>
          </aside>
        </div>
      )}
    </>
  );
}

function Meter({ score }: { score: number }) {
  return (
    <div className="meter-wrap">
      <div className="meter-label"><span>Evidence strength</span><strong>{Math.round(score * 100)}%</strong></div>
      <div className="meter" role="meter" aria-label={`Evidence strength, score ${score}`} aria-valuenow={score * 100} aria-valuemin={0} aria-valuemax={100}>
        <span style={{ width: `${score * 100}%` }} />
      </div>
    </div>
  );
}

function HypothesisCard({
  rank,
  category,
  title,
  score,
  description,
  against,
  unchecked,
}: {
  rank: string;
  category: CategoryName;
  title: string;
  score: number;
  description: string;
  against: string;
  unchecked: string;
}) {
  const [expanded, setExpanded] = useState(rank === "H1");
  return (
    <article className={`hypothesis-card ${expanded ? "expanded" : ""}`}>
      <button type="button" className="hypothesis-summary" onClick={() => setExpanded((value) => !value)} aria-expanded={expanded}>
        <span className="hypothesis-identity"><span className="rank">{rank}</span><span><CategoryChip name={category} /><Heading level={3}>{title}</Heading></span></span>
        <span className="summary-score"><strong>{Math.round(score * 100)}%</strong><small>confidence</small></span>
        <span className="disclosure">{expanded ? "−" : "+"}</span>
      </button>
      <div className="hypothesis-details">
        <Meter score={score} />
        <p className="hypothesis-description">{description}</p>
        <div className="points-grid">
          <div><strong className="point-heading for"><Icon kind="check" />For</strong><ul><Point kind="for">Observed signal correlates with onset window in time-series data.</Point></ul></div>
          <div><strong className="point-heading against"><Icon kind="cross" />Against</strong><ul><Point kind="against">{against}</Point></ul></div>
        </div>
        <div className="unchecked-row">
          <strong className="point-heading unchecked"><Icon kind="question" />Still unchecked</strong>
          <label><input type="checkbox" /> {unchecked}</label>
        </div>
      </div>
    </article>
  );
}

function CourtScreen({ data, onBack, onNext }: { data: typeof SAMPLE_DATASETS[0]; onBack: () => void; onNext: () => void }) {
  const [polish, setPolish] = useState(false);
  return (
    <>
      <Notice />
      <ScreenHeader eyebrow="Step 5 of 6 · Evidence Court" title="Evidence Court" description="Each possible cause is tested against what the data supports and what it contradicts." />
      <section className="verdict-banner">
        <div className="verdict-mark"><Icon kind="check" size={24} /></div>
        <div><span>Verdict</span><Heading level={2}>{data.verdict.title}</Heading><p>{data.verdict.detail}</p></div>
      </section>
      <div className="court-toolbar">
        <div><strong>Polish wording with Claude</strong><p>Numbers still come from code. Any AI text with an unknown number is rejected.</p></div>
        <label className="switch"><input type="checkbox" checked={polish} onChange={(e) => setPolish(e.target.checked)} /><span></span></label>
      </div>
      <div className="hypothesis-list">
        {data.hypotheses.map((h) => (
          <HypothesisCard key={h.rank} rank={h.rank} category={h.category} title={h.title} score={h.score} description={h.description} against={h.against} unchecked={h.unchecked} />
        ))}
      </div>
      <ScreenActions onBack={onBack} onNext={onNext} nextLabel="Build the RCA draft" />
    </>
  );
}

function TextArea({ defaultValue, label }: { defaultValue: string; label: string }) {
  return <textarea aria-label={label} defaultValue={defaultValue} key={defaultValue} />;
}

function DraftScreen({ data, onBack }: { data: typeof SAMPLE_DATASETS[0]; onBack: () => void }) {
  const [downloaded, setDownloaded] = useState(false);
  const download = () => {
    const content = `# RCA draft - ${data.title}\n\n## File\n${data.file}\n\n## Problem\n${data.problem}\n\n## Verdict\n${data.verdict.title}: ${data.verdict.detail}\n`;
    const url = URL.createObjectURL(new Blob([content], { type: "text/markdown" }));
    const link = document.createElement("a");
    link.href = url;
    link.download = `rca-draft-${data.file.replace(".csv", "")}.md`;
    link.click();
    URL.revokeObjectURL(url);
    setDownloaded(true);
  };
  return (
    <>
      <Notice />
      <ScreenHeader eyebrow="Step 6 of 6 · Draft" title="RCA draft" description="A working document built from the evidence. Edit the wording, assign the checks, and take it to engineering review." />
      <section className="card form-section">
        <div className="number-badge">01</div>
        <div className="form-content">
          <span className="section-kicker">Define the event</span><Heading level={2}>Problem statement</Heading>
          <TextArea label="Problem statement" defaultValue={data.problem} />
        </div>
      </section>
      <section className="card form-section">
        <div className="number-badge">02</div>
        <div className="form-content">
          <span className="section-kicker">Trace the chain</span><Heading level={2}>Five whys</Heading>
          <div className="whys-list">
            {data.whys.map(([question, answer], index) => (
              <div className="why-row" key={question}><span>{index + 1}</span><div><label>{question}</label><TextArea label={question} defaultValue={answer} /></div></div>
            ))}
          </div>
        </div>
      </section>
      <section className="card form-section">
        <div className="number-badge">03</div>
        <div className="form-content">
          <span className="section-kicker">Close the evidence gaps</span><Heading level={2}>Verification actions</Heading>
          <div className="actions-list">
            {data.actions.map((action) => (
              <label className="action-row" key={action[0]}><input type="checkbox" /><span className="action-copy"><strong>{action[0]}</strong><small>{action[1]} · {action[2]}</small></span><span className="hypothesis-badge">{action[3]}</span></label>
            ))}
          </div>
        </div>
      </section>
      <div className="screen-actions">
        <Button onClick={onBack}>Back to Evidence Court</Button>
        <Button variant="primary" onClick={download}><Icon kind="download" />{downloaded ? "Draft downloaded" : "Download draft (Markdown)"}</Button>
      </div>
    </>
  );
}

function Workspace() {
  const [screen, setScreen] = useState<Screen>(0);
  const [sampleIndex, setSampleIndex] = useState(0);
  const [toast, setToast] = useState("");
  const go = (next: number) => {
    setScreen(Math.max(0, Math.min(5, next)) as Screen);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };
  useEffect(() => {
    const handleNavigation = (event: KeyboardEvent) => {
      if (event.altKey && /^[1-6]$/.test(event.key)) go(Number(event.key) - 1);
    };
    window.addEventListener("keydown", handleNavigation);
    return () => window.removeEventListener("keydown", handleNavigation);
  }, []);
  const analysisComplete = (selectedIdx: number) => {
    setSampleIndex(selectedIdx);
    go(1);
    setToast(`Loaded Sample ${selectedIdx + 1}: ${SAMPLE_DATASETS[selectedIdx].title}`);
    window.setTimeout(() => setToast(""), 3200);
  };
  const currentData = SAMPLE_DATASETS[sampleIndex];

  return (
    <div className="app-shell">
      <Navigation screen={screen} onNavigate={go} />
      <main className="page">
        {screen === 0 && <StartScreen onNext={analysisComplete} />}
        {screen === 1 && <DataScreen data={currentData} onBack={() => go(0)} onNext={() => go(2)} />}
        {screen === 2 && <TimelineScreen data={currentData} onBack={() => go(1)} onNext={() => go(3)} />}
        {screen === 3 && <EvidenceScreen data={currentData} onBack={() => go(2)} onNext={() => go(4)} />}
        {screen === 4 && <CourtScreen data={currentData} onBack={() => go(3)} onNext={() => go(5)} />}
        {screen === 5 && <DraftScreen data={currentData} onBack={() => go(4)} />}
      </main>
      <footer><span>RCA Analyzer</span><span>Evidence informs decisions. Engineers validate them.</span></footer>
      {toast && <div className="toast" role="status"><Icon kind="check" /><span>{toast}</span><button type="button" onClick={() => setToast("")} aria-label="Dismiss notification">×</button></div>}
    </div>
  );
}

export default function App() {
  const [workspaceOpen, setWorkspaceOpen] = useState(false);
  return workspaceOpen ? <Workspace /> : <LandingPage onStart={() => setWorkspaceOpen(true)} />;
}
