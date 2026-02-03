"""Simple FastAPI dashboard for SuperOptiX observability.

Provides a lightweight web UI for viewing agent metrics, optimization history,
and protocol usage without requiring external services.
"""

import logging
from typing import Optional

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.responses import HTMLResponse, JSONResponse
    from fastapi.staticfiles import StaticFiles
    from fastapi.middleware.cors import CORSMiddleware

    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

from superoptix.observability.local_storage import LocalObservabilityStorage

logger = logging.getLogger(__name__)

if FASTAPI_AVAILABLE:
    app = FastAPI(
        title="SuperOptiX Observability Dashboard",
        description="Lightweight observability dashboard for SuperOptiX agents",
        version="1.0.0",
    )

    # Enable CORS for development
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Global storage instance
    storage: Optional[LocalObservabilityStorage] = None

    def get_storage() -> LocalObservabilityStorage:
        """Get or create storage instance."""
        global storage
        if storage is None:
            storage = LocalObservabilityStorage()
        return storage

    @app.get("/", response_class=HTMLResponse)
    async def dashboard_home():
        """Render dashboard home page."""
        html_content = """
		<!DOCTYPE html>
		<html>
		<head>
			<title>SuperOptiX Observability Dashboard</title>
			<style>
				body {
					font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
					margin: 0;
					padding: 20px;
					background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
					min-height: 100vh;
				}
				.container {
					max-width: 1400px;
					margin: 0 auto;
					background: white;
					border-radius: 12px;
					box-shadow: 0 10px 40px rgba(0,0,0,0.3);
					padding: 30px;
				}
				h1 {
					color: #667eea;
					margin-bottom: 10px;
				}
				.subtitle {
					color: #666;
					margin-bottom: 30px;
				}
				.metrics-grid {
					display: grid;
					grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
					gap: 20px;
					margin-bottom: 30px;
				}
				.metric-card {
					background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
					color: white;
					padding: 20px;
					border-radius: 8px;
					box-shadow: 0 4px 6px rgba(0,0,0,0.1);
				}
				.metric-value {
					font-size: 36px;
					font-weight: bold;
					margin: 10px 0;
				}
				.metric-label {
					font-size: 14px;
					opacity: 0.9;
				}
				.section {
					margin-bottom: 30px;
				}
				.section h2 {
					color: #333;
					border-bottom: 2px solid #667eea;
					padding-bottom: 10px;
				}
				table {
					width: 100%;
					border-collapse: collapse;
				}
				th, td {
					padding: 12px;
					text-align: left;
					border-bottom: 1px solid #ddd;
				}
				th {
					background: #f5f5f5;
					font-weight: 600;
				}
				tr:hover {
					background: #f9f9f9;
				}
				.refresh-btn {
					background: #667eea;
					color: white;
					border: none;
					padding: 10px 20px;
					border-radius: 6px;
					cursor: pointer;
					font-size: 16px;
				}
				.refresh-btn:hover {
					background: #5568d3;
				}
			</style>
		</head>
		<body>
			<div class="container">
				<h1>🚀 SuperOptiX Observability Dashboard</h1>
				<p class="subtitle">Real-time monitoring for your agentic AI systems</p>
				
				<div id="metrics-container">
					<div class="metrics-grid" id="metrics-grid">
						<!-- Metrics will be loaded here -->
					</div>
				</div>
				
				<div class="section">
					<h2>📊 Recent Agent Runs</h2>
					<table id="runs-table">
						<thead>
							<tr>
								<th>Agent</th>
								<th>Framework</th>
								<th>Accuracy</th>
								<th>Cost (USD)</th>
								<th>Tokens</th>
								<th>Latency (ms)</th>
								<th>Time</th>
							</tr>
						</thead>
						<tbody id="runs-tbody">
							<!-- Runs will be loaded here -->
						</tbody>
					</table>
				</div>
				
				<div class="section">
					<h2>🧬 GEPA Optimizations</h2>
					<table id="opts-table">
						<thead>
							<tr>
								<th>Agent</th>
								<th>Optimizer</th>
								<th>Initial</th>
								<th>Final</th>
								<th>Improvement</th>
								<th>Iterations</th>
								<th>Time</th>
							</tr>
						</thead>
						<tbody id="opts-tbody">
							<!-- Optimizations will be loaded here -->
						</tbody>
					</table>
				</div>
				
				<div class="section">
					<h2>🔌 Protocol Usage</h2>
					<table id="protocols-table">
						<thead>
							<tr>
								<th>Agent</th>
								<th>Protocol</th>
								<th>Server</th>
								<th>Tools Discovered</th>
								<th>Success Rate</th>
								<th>Avg Latency</th>
							</tr>
						</thead>
						<tbody id="protocols-tbody">
							<!-- Protocol usage will be loaded here -->
						</tbody>
					</table>
				</div>
				
				<button class="refresh-btn" onclick="loadData()">🔄 Refresh Data</button>
			</div>
			
			<script>
				async function loadData() {
					try {
						const response = await fetch('/api/dashboard');
						const data = await response.json();
						
						// Update metrics cards
						const metricsGrid = document.getElementById('metrics-grid');
						metricsGrid.innerHTML = `
							<div class="metric-card">
								<div class="metric-label">Total Cost</div>
								<div class="metric-value">$${(data.cost_summary.total_cost_usd || 0).toFixed(2)}</div>
							</div>
							<div class="metric-card">
								<div class="metric-label">Total Tokens</div>
								<div class="metric-value">${(data.cost_summary.total_tokens || 0).toLocaleString()}</div>
							</div>
							<div class="metric-card">
								<div class="metric-label">Optimizations</div>
								<div class="metric-value">${data.optimization_summary.total_optimizations || 0}</div>
							</div>
							<div class="metric-card">
								<div class="metric-label">Avg Improvement</div>
								<div class="metric-value">${((data.optimization_summary.avg_improvement || 0) * 100).toFixed(1)}%</div>
							</div>
						`;
						
						// Update runs table
						const runsTbody = document.getElementById('runs-tbody');
						runsTbody.innerHTML = data.recent_runs.map(run => `
							<tr>
								<td>${run.agent_name}</td>
								<td>${run.framework}</td>
								<td>${run.accuracy ? (run.accuracy * 100).toFixed(1) + '%' : 'N/A'}</td>
								<td>${run.cost_usd ? '$' + run.cost_usd.toFixed(4) : 'N/A'}</td>
								<td>${run.tokens_used || 'N/A'}</td>
								<td>${run.latency_ms ? run.latency_ms.toFixed(0) : 'N/A'}</td>
								<td>${new Date(run.timestamp).toLocaleString()}</td>
							</tr>
						`).join('');
						
						// Update optimizations table
						const optsTbody = document.getElementById('opts-tbody');
						optsTbody.innerHTML = data.recent_optimizations.map(opt => `
							<tr>
								<td>${opt.agent_name}</td>
								<td>${opt.optimizer}</td>
								<td>${opt.initial_score.toFixed(3)}</td>
								<td>${opt.final_score.toFixed(3)}</td>
								<td>+${opt.improvement.toFixed(3)}</td>
								<td>${opt.iterations}</td>
								<td>${new Date(opt.timestamp).toLocaleString()}</td>
							</tr>
						`).join('');
						
						// Update protocols table
						const protocolsTbody = document.getElementById('protocols-tbody');
						protocolsTbody.innerHTML = data.recent_protocol_usage.map(proto => {
							const toolsUsed = JSON.parse(proto.tools_used || '[]');
							return `
								<tr>
									<td>${proto.agent_name}</td>
									<td>${proto.protocol_type}</td>
									<td>${proto.server_uri}</td>
									<td>${proto.tools_discovered} (${toolsUsed.length} used)</td>
									<td>${proto.tool_success_rate ? (proto.tool_success_rate * 100).toFixed(1) + '%' : 'N/A'}</td>
									<td>${proto.avg_latency_ms ? proto.avg_latency_ms.toFixed(0) + 'ms' : 'N/A'}</td>
								</tr>
							`;
						}).join('');
						
					} catch (error) {
						console.error('Error loading data:', error);
					}
				}
				
				// Load data on page load
				loadData();
				
				// Auto-refresh every 10 seconds
				setInterval(loadData, 10000);
			</script>
		</body>
		</html>
		"""
        return html_content

    @app.get("/api/dashboard")
    async def get_dashboard_data():
        """Get comprehensive dashboard data."""
        try:
            storage = get_storage()
            data = storage.get_dashboard_data()
            return JSONResponse(content=data)
        except Exception as e:
            logger.error(f"Error getting dashboard data: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/api/runs")
    async def get_runs(
        agent_name: Optional[str] = None, limit: int = 50, offset: int = 0
    ):
        """Get agent runs."""
        try:
            storage = get_storage()
            runs = storage.get_agent_runs(
                agent_name=agent_name, limit=limit, offset=offset
            )
            return JSONResponse(content=runs)
        except Exception as e:
            logger.error(f"Error getting runs: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/api/optimizations")
    async def get_optimizations(
        agent_name: Optional[str] = None,
        optimizer: Optional[str] = None,
        limit: int = 50,
    ):
        """Get optimization runs."""
        try:
            storage = get_storage()
            opts = storage.get_optimizations(
                agent_name=agent_name, optimizer=optimizer, limit=limit
            )
            return JSONResponse(content=opts)
        except Exception as e:
            logger.error(f"Error getting optimizations: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/api/protocols")
    async def get_protocols(
        agent_name: Optional[str] = None,
        protocol_type: Optional[str] = None,
        limit: int = 50,
    ):
        """Get protocol usage."""
        try:
            storage = get_storage()
            protocols = storage.get_protocol_usage(
                agent_name=agent_name, protocol_type=protocol_type, limit=limit
            )
            return JSONResponse(content=protocols)
        except Exception as e:
            logger.error(f"Error getting protocols: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/api/cost/summary")
    async def get_cost_summary(agent_name: Optional[str] = None, days: int = 30):
        """Get cost summary."""
        try:
            storage = get_storage()
            summary = storage.get_cost_summary(agent_name=agent_name, days=days)
            return JSONResponse(content=summary)
        except Exception as e:
            logger.error(f"Error getting cost summary: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.on_event("shutdown")
    def shutdown_event():
        """Cleanup on shutdown."""
        global storage
        if storage:
            storage.close()

    def start_dashboard(host: str = "127.0.0.1", port: int = 8000):
        """Start the dashboard server.

        Args:
                host: Host to bind to
                port: Port to bind to
        """
        import uvicorn

        logger.info(f"Starting SuperOptiX dashboard at http://{host}:{port}")
        print(f"\n🚀 SuperOptiX Observability Dashboard")
        print(f"   URL: http://{host}:{port}")
        print(f"   Press Ctrl+C to stop\n")

        uvicorn.run(app, host=host, port=port, log_level="info")

else:
    logger.warning("FastAPI not available - install with: pip install fastapi uvicorn")

    def start_dashboard(host: str = "127.0.0.1", port: int = 8000):
        """Stub function when FastAPI not available."""
        print("❌ FastAPI not available")
        print("   Install with: pip install fastapi uvicorn")
        print("   Then run: super observe dashboard")


if __name__ == "__main__":
    start_dashboard()
