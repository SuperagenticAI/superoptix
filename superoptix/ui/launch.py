import subprocess
import sys
import time
from pathlib import Path


def launch_streamlit(agent_name: str):
    """Launch Streamlit with graceful shutdown handling."""
    ui_path = Path(__file__).parent / "agent_designer.py"

    print("\n✨ Launching Streamlit UI...")
    process = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", str(ui_path), "--", agent_name]
    )

    try:
        # Wait for process to complete or be terminated
        process.wait()

        # If process completed successfully
        if process.returncode == 0:
            print("\n✅ Playbook generated successfully!")
            print("🛑 Streamlit server stopped.")
        else:
            print("\n❌ Error: Streamlit server terminated unexpectedly.")

    except KeyboardInterrupt:
        # Handle manual interruption
        process.terminate()
        print("\n🛑 Streamlit server stopped by user.")

    finally:
        # Ensure process is cleaned up
        if process.poll() is None:
            process.kill()
            time.sleep(1)  # Give process time to clean up
