
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Kafka Pipeline with Monitoring Stack</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@300;400;600;800&display=swap');

        :root {
            --bg-dark: #0d1117;
            --bg-card: #161b22;
            --border: #30363d;
            --accent: #f97316;
            --accent-glow: rgba(249, 115, 22, 0.3);
            --text-primary: #e6edf3;
            --text-secondary: #8b949e;
            --success: #238636;
            --warning: #d29922;
            --danger: #da3633;
            --info: #58a6ff;
            --kafka: #231f20;
            --nginx: #009639;
            --prometheus: #e6522c;
            --grafana: #f46800;
            --loki: #0055b8;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', sans-serif;
            background: var(--bg-dark);
            color: var(--text-primary);
            line-height: 1.6;
            overflow-x: hidden;
        }

        /* Animated Background Grid */
        .bg-grid {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-image: 
                linear-gradient(rgba(249, 115, 22, 0.03) 1px, transparent 1px),
                linear-gradient(90deg, rgba(249, 115, 22, 0.03) 1px, transparent 1px);
            background-size: 50px 50px;
            pointer-events: none;
            z-index: 0;
            animation: gridMove 20s linear infinite;
        }

        @keyframes gridMove {
            0% { transform: translate(0, 0); }
            100% { transform: translate(50px, 50px); }
        }

        /* Floating Particles */
        .particles {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 1;
            overflow: hidden;
        }

        .particle {
            position: absolute;
            width: 4px;
            height: 4px;
            background: var(--accent);
            border-radius: 50%;
            opacity: 0.5;
            animation: float 15s infinite;
        }

        @keyframes float {
            0%, 100% { transform: translateY(100vh) rotate(0deg); opacity: 0; }
            10% { opacity: 0.5; }
            90% { opacity: 0.5; }
            100% { transform: translateY(-100vh) rotate(720deg); opacity: 0; }
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 40px 20px;
            position: relative;
            z-index: 2;
        }

        /* Hero Section */
        .hero {
            text-align: center;
            padding: 80px 0;
            position: relative;
        }

        .hero-badge {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: linear-gradient(135deg, rgba(249, 115, 22, 0.1), rgba(249, 115, 22, 0.05));
            border: 1px solid var(--accent);
            padding: 8px 16px;
            border-radius: 50px;
            font-size: 0.85rem;
            font-weight: 600;
            color: var(--accent);
            margin-bottom: 24px;
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0%, 100% { box-shadow: 0 0 0 0 var(--accent-glow); }
            50% { box-shadow: 0 0 20px 5px var(--accent-glow); }
        }

        .hero h1 {
            font-size: 4rem;
            font-weight: 800;
            background: linear-gradient(135deg, #fff 0%, var(--accent) 50%, #fff 100%);
            background-size: 200% auto;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            animation: shine 3s linear infinite;
            margin-bottom: 20px;
            letter-spacing: -2px;
        }

        @keyframes shine {
            to { background-position: 200% center; }
        }

        .hero-subtitle {
            font-size: 1.25rem;
            color: var(--text-secondary);
            max-width: 600px;
            margin: 0 auto 40px;
        }

        /* Architecture Diagram */
        .architecture {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 40px;
            margin: 60px 0;
            position: relative;
            overflow: hidden;
        }

        .architecture::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 2px;
            background: linear-gradient(90deg, transparent, var(--accent), transparent);
            animation: scan 3s linear infinite;
        }

        @keyframes scan {
            0% { transform: translateX(-100%); }
            100% { transform: translateX(100%); }
        }

        .arch-title {
            text-align: center;
            font-size: 1.5rem;
            font-weight: 700;
            margin-bottom: 40px;
            color: var(--text-primary);
        }

        .flow-diagram {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            align-items: center;
            gap: 20px;
            position: relative;
        }

        .service-node {
            background: linear-gradient(135deg, var(--bg-dark), var(--bg-card));
            border: 2px solid var(--border);
            border-radius: 12px;
            padding: 20px 30px;
            min-width: 140px;
            text-align: center;
            position: relative;
            transition: all 0.3s ease;
            cursor: pointer;
        }

        .service-node:hover {
            transform: translateY(-5px);
            border-color: var(--accent);
            box-shadow: 0 10px 40px var(--accent-glow);
        }

        .service-node.kafka { border-color: #666; }
        .service-node.nginx { border-color: var(--nginx); }
        .service-node.fluent { border-color: var(--info); }
        .service-node.loki { border-color: var(--loki); }
        .service-node.prometheus { border-color: var(--prometheus); }
        .service-node.grafana { border-color: var(--grafana); }

        .service-icon {
            font-size: 2rem;
            margin-bottom: 8px;
        }

        .service-name {
            font-weight: 700;
            font-size: 0.9rem;
        }

        .arrow {
            font-size: 1.5rem;
            color: var(--accent);
            animation: flow 1.5s ease-in-out infinite;
        }

        @keyframes flow {
            0%, 100% { opacity: 0.3; transform: translateX(0); }
            50% { opacity: 1; transform: translateX(5px); }
        }

        /* Stats Bar */
        .stats-bar {
            display: flex;
            justify-content: center;
            gap: 40px;
            margin: 40px 0;
            flex-wrap: wrap;
        }

        .stat {
            text-align: center;
            padding: 20px 30px;
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 12px;
            min-width: 120px;
        }

        .stat-number {
            font-size: 2.5rem;
            font-weight: 800;
            color: var(--accent);
            display: block;
        }

        .stat-label {
            font-size: 0.85rem;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        /* Code Sections */
        .section {
            margin: 60px 0;
        }

        .section-header {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 24px;
        }

        .section-icon {
            width: 48px;
            height: 48px;
            background: linear-gradient(135deg, var(--accent), #ea580c);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5rem;
        }

        .section h2 {
            font-size: 1.75rem;
            font-weight: 700;
        }

        /* Code Editor Style */
        .code-window {
            background: #1e1e1e;
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid var(--border);
            box-shadow: 0 20px 60px rgba(0,0,0,0.5);
        }

        .code-header {
            background: #2d2d2d;
            padding: 12px 16px;
            display: flex;
            align-items: center;
            gap: 8px;
            border-bottom: 1px solid #3d3d3d;
        }

        .window-btn {
            width: 12px;
            height: 12px;
            border-radius: 50%;
        }

        .window-btn.red { background: #ff5f56; }
        .window-btn.yellow { background: #ffbd2e; }
        .window-btn.green { background: #27c93f; }

        .code-title {
            margin-left: 12px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.85rem;
            color: #858585;
        }

        .code-content {
            padding: 20px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.9rem;
            line-height: 1.6;
            overflow-x: auto;
            max-height: 500px;
            overflow-y: auto;
        }

        .code-content pre {
            margin: 0;
            white-space: pre-wrap;
        }

        /* Syntax Highlighting */
        .comment { color: #6a9955; }
        .keyword { color: #569cd6; }
        .string { color: #ce9178; }
        .number { color: #b5cea8; }
        .function { color: #dcdcaa; }
        .variable { color: #9cdcfe; }
        .section-header-lua { color: #ffd700; }
        .bracket { color: #ffd700; }

        /* Feature Cards */
        .features-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 24px;
            margin: 40px 0;
        }

        .feature-card {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 30px;
            position: relative;
            overflow: hidden;
            transition: all 0.3s ease;
        }

        .feature-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 3px;
            background: linear-gradient(90deg, var(--accent), transparent);
            transform: scaleX(0);
            transform-origin: left;
            transition: transform 0.3s ease;
        }

        .feature-card:hover::before {
            transform: scaleX(1);
        }

        .feature-card:hover {
            transform: translateY(-5px);
            border-color: var(--accent);
        }

        .feature-icon {
            font-size: 2.5rem;
            margin-bottom: 16px;
        }

        .feature-title {
            font-size: 1.25rem;
            font-weight: 700;
            margin-bottom: 12px;
        }

        .feature-desc {
            color: var(--text-secondary);
            font-size: 0.95rem;
        }

        /* Alert Animation */
        .alert-demo {
            background: linear-gradient(135deg, rgba(218, 54, 51, 0.1), rgba(218, 54, 51, 0.05));
            border: 1px solid var(--danger);
            border-radius: 12px;
            padding: 20px;
            margin: 20px 0;
            animation: alertPulse 2s infinite;
        }

        @keyframes alertPulse {
            0%, 100% { box-shadow: 0 0 0 0 rgba(218, 54, 51, 0.4); }
            50% { box-shadow: 0 0 20px 5px rgba(218, 54, 51, 0.2); }
        }

        /* Terminal Effect */
        .terminal {
            background: #0c0c0c;
            border-radius: 12px;
            padding: 20px;
            font-family: 'JetBrains Mono', monospace;
            border: 1px solid var(--border);
        }

        .terminal-line {
            display: flex;
            gap: 12px;
            margin: 8px 0;
            opacity: 0;
            animation: typeIn 0.5s forwards;
        }

        .terminal-line:nth-child(1) { animation-delay: 0.5s; }
        .terminal-line:nth-child(2) { animation-delay: 1s; }
        .terminal-line:nth-child(3) { animation-delay: 1.5s; }
        .terminal-line:nth-child(4) { animation-delay: 2s; }

        @keyframes typeIn {
            to { opacity: 1; }
        }

        .prompt { color: var(--success); }
        .command { color: var(--text-primary); }
        .output { color: var(--text-secondary); }

        /* Footer */
        .footer {
            text-align: center;
            padding: 60px 0;
            border-top: 1px solid var(--border);
            margin-top: 80px;
        }

        .tech-stack {
            display: flex;
            justify-content: center;
            gap: 30px;
            flex-wrap: wrap;
            margin: 30px 0;
        }

        .tech-item {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 10px 20px;
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 8px;
            font-size: 0.9rem;
            transition: all 0.3s ease;
        }

        .tech-item:hover {
            border-color: var(--accent);
            transform: scale(1.05);
        }

        /* Responsive */
        @media (max-width: 768px) {
            .hero h1 { font-size: 2.5rem; }
            .flow-diagram { flex-direction: column; }
            .arrow { transform: rotate(90deg); }
            .stats-bar { flex-direction: column; align-items: center; }
        }

        /* Scrollbar */
        ::-webkit-scrollbar {
            width: 10px;
            height: 10px;
        }

        ::-webkit-scrollbar-track {
            background: var(--bg-dark);
        }

        ::-webkit-scrollbar-thumb {
            background: var(--border);
            border-radius: 5px;
        }

        ::-webkit-scrollbar-thumb:hover {
            background: var(--accent);
        }

        /* Copy Button */
        .copy-btn {
            position: absolute;
            top: 12px;
            right: 16px;
            background: rgba(255,255,255,0.1);
            border: none;
            color: var(--text-secondary);
            padding: 6px 12px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.8rem;
            transition: all 0.3s ease;
            opacity: 0;
        }

        .code-window:hover .copy-btn {
            opacity: 1;
        }

        .copy-btn:hover {
            background: var(--accent);
            color: white;
        }
    </style>
<base target="_blank">
</head>
<body>
    <div class="bg-grid"></div>
    <div class="particles" id="particles"></div>

    <div class="container">
        <!-- Hero Section -->
        <section class="hero">
            <div class="hero-badge">
                <span>🔥</span>
                <span>Production-Ready Monitoring Stack</span>
            </div>
            <h1>Kafka Pipeline</h1>
            <p class="hero-subtitle">
                Enterprise-grade observability stack with Fluent Bit log aggregation, 
                Loki storage, Prometheus metrics, and intelligent Lua parsing for real-time security monitoring.
            </p>

            <div class="stats-bar">
                <div class="stat">
                    <span class="stat-number">8</span>
                    <span class="stat-label">Services</span>
                </div>
                <div class="stat">
                    <span class="stat-number">15+</span>
                    <span class="stat-label">Alert Rules</span>
                </div>
                <div class="stat">
                    <span class="stat-number">∞</span>
                    <span class="stat-label">Scalability</span>
                </div>
            </div>
        </section>

        <!-- Architecture Diagram -->
        <div class="architecture">
            <h3 class="arch-title">🏗️ Data Flow Architecture</h3>
            <div class="flow-diagram">
                <div class="service-node nginx">
                    <div class="service-icon">🌐</div>
                    <div class="service-name">Nginx</div>
                </div>
                <div class="arrow">→</div>
                <div class="service-node fluent">
                    <div class="service-icon">📊</div>
                    <div class="service-name">Fluent Bit</div>
                </div>
                <div class="arrow">→</div>
                <div class="service-node loki">
                    <div class="service-icon">🔍</div>
                    <div class="service-name">Loki</div>
                </div>
                <div class="arrow">→</div>
                <div class="service-node kafka">
                    <div class="service-icon">🚀</div>
                    <div class="service-name">Kafka</div>
                </div>
                <div class="arrow">→</div>
                <div class="service-node prometheus">
                    <div class="service-icon">📈</div>
                    <div class="service-name">Prometheus</div>
                </div>
                <div class="arrow">→</div>
                <div class="service-node grafana">
                    <div class="service-icon">📊</div>
                    <div class="service-name">Grafana</div>
                </div>
            </div>
        </div>

        <!-- Quick Start -->
        <section class="section">
            <div class="section-header">
                <div class="section-icon">🚀</div>
                <h2>Quick Start</h2>
            </div>
            <div class="terminal">
                <div class="terminal-line">
                    <span class="prompt">$</span>
                    <span class="command">git clone https://github.com/yourusername/kafka-pipeline.git</span>
                </div>
                <div class="terminal-line">
                    <span class="prompt">$</span>
                    <span class="command">cd kafka-pipeline</span>
                </div>
                <div class="terminal-line">
                    <span class="prompt">$</span>
                    <span class="command">docker-compose up -d</span>
                </div>
                <div class="terminal-line">
                    <span class="output">✓ All services started successfully</span>
                </div>
            </div>
        </section>

        <!-- Features -->
        <section class="section">
            <div class="section-header">
                <div class="section-icon">⚡</div>
                <h2>Key Features</h2>
            </div>
            <div class="features-grid">
                <div class="feature-card">
                    <div class="feature-icon">🛡️</div>
                    <h3 class="feature-title">Brute Force Detection</h3>
                    <p class="feature-desc">Real-time detection of login attacks with automatic IP blocking and rate limiting alerts.</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">🔧</div>
                    <h3 class="feature-title">Lua Log Parsing</h3>
                    <p class="feature-desc">Custom Lua scripts for intelligent log parsing supporting FastAPI, Nginx, and Kafka logs.</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">📊</div>
                    <h3 class="feature-title">Multi-source Metrics</h3>
                    <p class="feature-desc">Unified metrics collection from Kafka Exporter, Nginx, Node Exporter, and Fluent Bit.</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">🔔</div>
                    <h3 class="feature-title">Smart Alerting</h3>
                    <p class="feature-desc">Prometheus Alertmanager integration with severity-based routing and data loss prevention.</p>
                </div>
            </div>
        </section>

        <!-- Fluent Bit Config -->
        <section class="section">
            <div class="section-header">
                <div class="section-icon">⚙️</div>
                <h2>Fluent Bit Configuration</h2>
            </div>
            <div class="code-window">
                <div class="code-header">
                    <div class="window-btn red"></div>
                    <div class="window-btn yellow"></div>
                    <div class="window-btn green"></div>
                    <span class="code-title">fluent-bit.conf</span>
                </div>
                <div class="code-content">
                    <pre><span class="section-header-lua">[SERVICE]</span>
    <span class="variable">Flush</span>        <span class="number">1</span>
    <span class="variable">Daemon</span>       <span class="keyword">Off</span>
    <span class="variable">Log_Level</span>    <span class="string">info</span>
    <span class="variable">Parsers_File</span> <span class="string">parsers.conf</span>
    <span class="variable">HTTP_Server</span>  <span class="keyword">On</span>
    <span class="variable">HTTP_Listen</span>  <span class="number">0.0.0.0</span>
    <span class="variable">HTTP_Port</span>    <span class="number">2020</span>

<span class="section-header-lua">[INPUT]</span>
    <span class="variable">Name</span>          <span class="string">tail</span>
    <span class="variable">Path</span>          <span class="string">/var/lib/docker/containers/*/*.log</span>
    <span class="variable">Parser</span>        <span class="string">docker</span>
    <span class="variable">Tag</span>           <span class="string">docker.*</span>
    <span class="variable">Docker_Mode</span>   <span class="keyword">On</span>
    <span class="variable">Buffer_Chunk_Size</span> <span class="number">1MB</span>
    <span class="variable">Buffer_Max_Size</span>   <span class="number">5MB</span>

<span class="section-header-lua">[FILTER]</span>
    <span class="variable">Name</span>   <span class="string">lua</span>
    <span class="variable">Match</span>  <span class="string">docker.*</span>
    <span class="variable">Script</span> <span class="string">/fluent-bit/etc/parse_logs.lua</span>
    <span class="variable">Call</span>   <span class="function">parse_log</span>

<span class="section-header-lua">[OUTPUT]</span>
    <span class="variable">Name</span>        <span class="string">loki</span>
    <span class="variable">Match</span>       <span class="string">docker.*</span>
    <span class="variable">Host</span>        <span class="string">loki</span>
    <span class="variable">Port</span>        <span class="number">3100</span>
    <span class="variable">Labels</span>      <span class="string">job=$job, service=$service, event_type=$event_type, client_ip=$client_ip</span>
    <span class="variable">Line_Format</span> <span class="string">json</span></pre>
                </div>
            </div>
        </section>

        <!-- Lua Parser -->
        <section class="section">
            <div class="section-header">
                <div class="section-icon">📝</div>
                <h2>Intelligent Lua Parser</h2>
            </div>
            <div class="code-window">
                <div class="code-header">
                    <div class="window-btn red"></div>
                    <div class="window-btn yellow"></div>
                    <div class="window-btn green"></div>
                    <span class="code-title">parse_logs.lua</span>
                </div>
                <div class="code-content">
                    <pre><span class="keyword">function</span> <span class="function">parse_log</span><span class="bracket">(</span><span class="variable">tag</span>, <span class="variable">timestamp</span>, <span class="variable">record</span><span class="bracket">)</span>
    <span class="keyword">local</span> <span class="variable">log</span> = <span class="variable">record</span>[<span class="string">"log"</span>]

    <span class="keyword">if</span> <span class="variable">log</span> == <span class="keyword">nil</span> <span class="keyword">then</span>
        <span class="variable">record</span>[<span class="string">"job"</span>] = <span class="string">"no-log"</span>
        <span class="keyword">return</span> <span class="number">1</span>, <span class="variable">timestamp</span>, <span class="variable">record</span>
    <span class="keyword">end</span>

    <span class="keyword">local</span> <span class="variable">log_str</span> = <span class="function">tostring</span><span class="bracket">(</span><span class="variable">log</span><span class="bracket">)</span>

    <span class="comment">-- ==========================================</span>
    <span class="comment">-- FastAPI Log Parsing</span>
    <span class="comment">-- ==========================================</span>
    <span class="keyword">if</span> <span class="function">string.find</span><span class="bracket">(</span><span class="variable">log_str</span>, <span class="string">'"service": "fastapi"'</span>, <span class="number">1</span>, <span class="keyword">true</span><span class="bracket">)</span> <span class="keyword">then</span>
        <span class="variable">record</span>[<span class="string">"job"</span>] = <span class="string">"fastapi"</span>
        <span class="variable">record</span>[<span class="string">"service"</span>] = <span class="string">"fastapi"</span>

        <span class="comment">-- Extract IP, Event, Username, Level, UserID, Role...</span>
        <span class="keyword">local</span> <span class="variable">ip</span> = <span class="function">string.match</span><span class="bracket">(</span><span class="variable">log_str</span>, <span class="string">'"ip": "([%d%.]+)"'</span><span class="bracket">)</span>
        <span class="keyword">if</span> <span class="variable">ip</span> <span class="keyword">then</span> <span class="variable">record</span>[<span class="string">"client_ip"</span>] = <span class="variable">ip</span> <span class="keyword">end</span>

        <span class="keyword">local</span> <span class="variable">event</span> = <span class="function">string.match</span><span class="bracket">(</span><span class="variable">log_str</span>, <span class="string">'"event": "([^"]+)"'</span><span class="bracket">)</span>
        <span class="keyword">if</span> <span class="variable">event</span> <span class="keyword">then</span> <span class="variable">record</span>[<span class="string">"event_type"</span>] = <span class="variable">event</span> <span class="keyword">end</span>

        <span class="comment">-- Security: Rate limiting detection</span>
        <span class="keyword">if</span> <span class="variable">event</span> == <span class="string">"login_blocked"</span> <span class="keyword">then</span>
            <span class="variable">record</span>[<span class="string">"rate_limited"</span>] = <span class="string">"true"</span>
        <span class="keyword">elseif</span> <span class="variable">event</span> == <span class="string">"login_failed"</span> <span class="keyword">or</span> <span class="variable">event</span> == <span class="string">"login_success"</span> <span class="keyword">then</span>
            <span class="variable">record</span>[<span class="string">"rate_limited"</span>] = <span class="string">"false"</span>
        <span class="keyword">end</span>

    <span class="comment">-- ==========================================</span>
    <span class="comment">-- Nginx Access Log Parsing</span>
    <span class="comment">-- ==========================================</span>
    <span class="keyword">elseif</span> <span class="function">string.match</span><span class="bracket">(</span><span class="variable">log_str</span>, <span class="string">"%d+%.%d+%.%d+%.%d+"</span><span class="bracket">)</span> <span class="keyword">and</span> 
           <span class="bracket">(</span><span class="function">string.find</span><span class="bracket">(</span><span class="variable">log_str</span>, <span class="string">"HTTP/"</span>, <span class="number">1</span>, <span class="keyword">true</span><span class="bracket">)</span><span class="bracket">)</span> <span class="keyword">then</span>

        <span class="variable">record</span>[<span class="string">"job"</span>] = <span class="string">"nginx"</span>
        <span class="variable">record</span>[<span class="string">"service"</span>] = <span class="string">"nginx"</span>

        <span class="keyword">local</span> <span class="variable">ip</span> = <span class="function">string.match</span><span class="bracket">(</span><span class="variable">log_str</span>, <span class="string">"(%d+%.%d+%.%d+%.%d+)"</span><span class="bracket">)</span>
        <span class="keyword">if</span> <span class="variable">ip</span> <span class="keyword">then</span> <span class="variable">record</span>[<span class="string">"client_ip"</span>] = <span class="variable">ip</span> <span class="keyword">end</span>

        <span class="keyword">local</span> <span class="variable">method</span>, <span class="variable">endpoint</span> = <span class="function">string.match</span><span class="bracket">(</span><span class="variable">log_str</span>, <span class="string">'"(%u+)%s+([^%s]+)%s+HTTP'</span><span class="bracket">)</span>
        <span class="keyword">if</span> <span class="variable">endpoint</span> <span class="keyword">then</span> <span class="variable">record</span>[<span class="string">"endpoint"</span>] = <span class="variable">endpoint</span> <span class="keyword">end</span>

        <span class="keyword">local</span> <span class="variable">status</span> = <span class="function">string.match</span><span class="bracket">(</span><span class="variable">log_str</span>, <span class="string">'"%s+(%d%d%d)%s'</span><span class="bracket">)</span>
        <span class="keyword">if</span> <span class="variable">status</span> <span class="keyword">then</span> 
            <span class="variable">record</span>[<span class="string">"status"</span>] = <span class="variable">status</span> 
            <span class="variable">record</span>[<span class="string">"http_status"</span>] = <span class="variable">status</span>
        <span class="keyword">end</span>

        <span class="comment">-- Error detection for 4xx/5xx</span>
        <span class="keyword">if</span> <span class="variable">status</span> <span class="keyword">then</span> 
            <span class="keyword">local</span> <span class="variable">code</span> = <span class="function">tonumber</span><span class="bracket">(</span><span class="variable">status</span><span class="bracket">)</span>
            <span class="keyword">if</span> <span class="variable">code</span> >= <span class="number">400</span> <span class="keyword">then</span> 
                <span class="variable">record</span>[<span class="string">"error"</span>] = <span class="variable">status</span>
            <span class="keyword">end</span>
        <span class="keyword">end</span>

    <span class="comment">-- ==========================================</span>
    <span class="comment">-- Kafka & Zookeeper Logs</span>
    <span class="comment">-- ==========================================</span>
    <span class="keyword">elseif</span> <span class="function">string.find</span><span class="bracket">(</span><span class="variable">log_str</span>, <span class="string">"kafka"</span>, <span class="number">1</span>, <span class="keyword">true</span><span class="bracket">)</span> <span class="keyword">then</span>
        <span class="variable">record</span>[<span class="string">"job"</span>] = <span class="string">"kafka"</span>
        <span class="variable">record</span>[<span class="string">"service"</span>] = <span class="string">"kafka"</span>
    <span class="keyword">else</span>
        <span class="variable">record</span>[<span class="string">"job"</span>] = <span class="string">"other"</span>
    <span class="keyword">end</span>

    <span class="keyword">return</span> <span class="number">1</span>, <span class="variable">timestamp</span>, <span class="variable">record</span>
<span class="keyword">end</span></pre>
                </div>
            </div>
        </section>

        <!-- Prometheus Rules -->
        <section class="section">
            <div class="section-header">
                <div class="section-icon">🔔</div>
                <h2>Alerting Rules</h2>
            </div>
            <div class="code-window">
                <div class="code-header">
                    <div class="window-btn red"></div>
                    <div class="window-btn yellow"></div>
                    <div class="window-btn green"></div>
                    <span class="code-title">rules.yml</span>
                </div>
                <div class="code-content">
                    <pre><span class="variable">groups</span>:
  - <span class="variable">name</span>: <span class="string">kafka_down</span>
    <span class="variable">rules</span>:
      - <span class="variable">alert</span>: <span class="string">KafkaDownFor10mins</span>
        <span class="variable">expr</span>: <span class="function">kafka_brokers</span> < <span class="number">1</span> <span class="keyword">or</span> <span class="function">absent</span><span class="bracket">(</span><span class="function">kafka_brokers</span><span class="bracket">)</span> == <span class="number">1</span>
        <span class="keyword">for</span>: <span class="number">15s</span>
        <span class="variable">labels</span>:
          <span class="variable">severity</span>: <span class="string">warning</span>
        <span class="variable">annotations</span>:
          <span class="variable">summary</span>: <span class="string">"Kafka is not up"</span>

  - <span class="variable">name</span>: <span class="string">kafka_smells_data_loss</span>
    <span class="variable">rules</span>:
      - <span class="variable">alert</span>: <span class="string">KafkaUnderReplicatedPartitions</span>
        <span class="variable">expr</span>: <span class="function">sum</span><span class="bracket">(</span><span class="function">kafka_topic_partition_under_replicated_partition</span><span class="bracket">)</span> > <span class="number">0</span>
        <span class="keyword">for</span>: <span class="number">10m</span>
        <span class="variable">labels</span>:
          <span class="variable">severity</span>: <span class="string">critical</span>
        <span class="variable">annotations</span>:
          <span class="variable">summary</span>: <span class="string">"Data Loss(maybe)"</span>
          <span class="variable">description</span>: <span class="string">"Detected partitions with fewer replicas than configured."</span>

  - <span class="variable">name</span>: <span class="string">Login_Brute_Force</span>
    <span class="variable">rules</span>:
      - <span class="variable">alert</span>: <span class="string">LoginBruteForce</span>
        <span class="variable">expr</span>: <span class="function">sum</span><span class="bracket">(</span><span class="function">rate</span><span class="bracket">(</span><span class="function">nginx_requests_total</span>{<span class="variable">job</span>=<span class="string">"nginx"</span>}[<span class="number">5s</span>]<span class="bracket">)</span><span class="bracket">)</span> <span class="keyword">by</span> <span class="bracket">(</span><span class="variable">ip</span><span class="bracket">)</span> > <span class="number">5</span>
        <span class="keyword">for</span>: <span class="number">10s</span>
        <span class="variable">labels</span>:
          <span class="variable">severity</span>: <span class="string">warning</span>
        <span class="variable">annotations</span>:
          <span class="variable">summary</span>: <span class="string">"A BruteForce Attack is being Attempted."</span>
          <span class="variable">description</span>: <span class="string">"No Worries. the ip is now blocked"</span></pre>
                </div>
            </div>
        </section>

        <!-- Services Table -->
        <section class="section">
            <div class="section-header">
                <div class="section-icon">🐳</div>
                <h2>Service Overview</h2>
            </div>
            <div class="code-window">
                <div class="code-header">
                    <div class="window-btn red"></div>
                    <div class="window-btn yellow"></div>
                    <div class="window-btn green"></div>
                    <span class="code-title">docker-compose.yml (Services)</span>
                </div>
                <div class="code-content">
                    <pre><span class="comment"># Core Infrastructure</span>
┌─────────────────┬─────────────┬─────────────────────────────────────┐
│ Service         │ Port        │ Description                         │
├─────────────────┼─────────────┼─────────────────────────────────────┤
│ <span class="keyword">Kafka</span>           │ 9092        │ Message broker & streaming          │
│ <span class="keyword">Zookeeper</span>       │ 2181        │ Cluster coordination                │
│ <span class="keyword">Kafka Exporter</span>  │ 9308        │ Metrics exporter for Prometheus     │
├─────────────────┼─────────────┼─────────────────────────────────────┤
│ <span class="keyword">Nginx</span>           │ 80/443      │ Reverse proxy & load balancer       │
│ <span class="keyword">Nginx Exporter</span>  │ 9113        │ stub_status metrics                 │
├─────────────────┼─────────────┼─────────────────────────────────────┤
│ <span class="keyword">Fluent Bit</span>      │ 2020        │ Log collector & processor           │
│ <span class="keyword">Loki</span>            │ 3100        │ Log aggregation storage             │
├─────────────────┼─────────────┼─────────────────────────────────────┤
│ <span class="keyword">Prometheus</span>      │ 9090        │ Metrics collection & alerting         │
│ <span class="keyword">Alertmanager</span>    │ 9093        │ Alert routing & management          │
│ <span class="keyword">Grafana</span>         │ 3000        │ Visualization dashboards            │
└─────────────────┴─────────────┴─────────────────────────────────────┘</pre>
                </div>
            </div>
        </section>

        <!-- Footer -->
        <footer class="footer">
            <h3>Built with Modern Observability Stack</h3>
            <div class="tech-stack">
                <div class="tech-item">🚀 Apache Kafka</div>
                <div class="tech-item">📊 Fluent Bit</div>
                <div class="tech-item">🔍 Grafana Loki</div>
                <div class="tech-item">📈 Prometheus</div>
                <div class="tech-item">🎨 Grafana</div>
                <div class="tech-item">🌐 Nginx</div>
            </div>
            <p style="color: var(--text-secondary); margin-top: 30px;">
                Designed for production environments with security-first approach.
            </p>
        </footer>
    </div>

    <script>
        // Create floating particles
        const particlesContainer = document.getElementById('particles');
        for (let i = 0; i < 20; i++) {
            const particle = document.createElement('div');
            particle.className = 'particle';
            particle.style.left = Math.random() * 100 + '%';
            particle.style.animationDelay = Math.random() * 15 + 's';
            particle.style.animationDuration = (15 + Math.random() * 10) + 's';
            particlesContainer.appendChild(particle);
        }
    </script>
</body>
</html>
