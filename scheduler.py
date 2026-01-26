import schedule
import time
import subprocess
from datetime import datetime
import os

# ============================================================================
# CONFIGURATION
# ============================================================================

# Scripts to run
RESULTS_TRACKER_SCRIPT = "track_results.py"
DATA_UPDATE_SCRIPT = "daily_data_update.py"
EDGE_FINDER_SCRIPT = "find_edges_v2_TELEGRAM.py"

# ============================================================================
# JOB FUNCTIONS
# ============================================================================

def run_results_tracker():
    """Run the results tracker script"""
    current_time = datetime.now().strftime('%Y-%m-%d %I:%M %p')
    print(f"\n{'='*70}")
    print(f"📈 Running Results Tracker at {current_time}")
    print(f"{'='*70}")

    try:
        result = subprocess.run(
            ['python', RESULTS_TRACKER_SCRIPT],
            capture_output=True,
            text=True,
            timeout=300
        )

        if result.returncode == 0:
            print("✅ Results tracker completed successfully!")
            print(result.stdout)
        else:
            print("❌ Results tracker failed!")
            print(result.stderr)
    except Exception as e:
        print(f"❌ Error running results tracker: {e}")

    print(f"{'='*70}\n")

def run_data_update():
    """Run the daily data update script"""
    current_time = datetime.now().strftime('%Y-%m-%d %I:%M %p')
    print(f"\n{'='*70}")
    print(f"📊 Running Data Update at {current_time}")
    print(f"{'='*70}")

    try:
        result = subprocess.run(
            ['python', DATA_UPDATE_SCRIPT],
            capture_output=True,
            text=True,
            timeout=300
        )

        if result.returncode == 0:
            print("✅ Data update completed successfully!")
            print(result.stdout)
        else:
            print("❌ Data update failed!")
            print(result.stderr)
    except Exception as e:
        print(f"❌ Error running data update: {e}")

    print(f"{'='*70}\n")

def run_edge_finder():
    """Run the edge finder script"""
    current_time = datetime.now().strftime('%Y-%m-%d %I:%M %p')
    print(f"\n{'='*70}")
    print(f"🏀 Running Edge Finder at {current_time}")
    print(f"{'='*70}")

    try:
        result = subprocess.run(
            ['python', EDGE_FINDER_SCRIPT],
            capture_output=True,
            text=True,
            timeout=300
        )

        if result.returncode == 0:
            print("✅ Edge finder completed successfully!")
            print(result.stdout)
        else:
            print("❌ Edge finder failed!")
            print(result.stderr)
    except Exception as e:
        print(f"❌ Error running edge finder: {e}")

    print(f"{'='*70}\n")

# ============================================================================
# MAIN SCHEDULER
# ============================================================================

def main():
    """Main scheduler loop"""
    print("\n" + "="*70)
    print("🏀 NBA AUTOMATED WORKFLOW SCHEDULER")
    print("="*70)
    print("\nSchedule (All times in UTC, converted from EST):")
    print("  • EVERY DAY:")
    print("    - 08:00 UTC (3:00 AM EST): Results Tracker")
    print("    - 21:00 UTC (4:00 PM EST): Data Update")
    print("    - 22:00 UTC (5:00 PM EST): Edge Finder")
    print("\n" + "="*70 + "\n")

    # Results tracker at 3 AM EST (8 AM UTC) EVERY DAY
    schedule.every().day.at("08:00").do(run_results_tracker)

    # Data update at 4 PM EST (21 PM UTC) EVERY DAY
    schedule.every().day.at("21:00").do(run_data_update)

    # Edge finder at 5 PM EST (22 PM UTC) EVERY DAY
    schedule.every().day.at("22:00").do(run_edge_finder)

    print("✅ Scheduler is running... Press Ctrl+C to stop\n")

    try:
        while True:
            schedule.run_pending()
            time.sleep(60)
    except KeyboardInterrupt:
        print("\n\n👋 Scheduler stopped by user")
        print("="*70 + "\n")

if __name__ == "__main__":
    main()
