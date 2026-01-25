import schedule
import time
import subprocess
from datetime import datetime
import holidays
import os

# ============================================================================
# CONFIGURATION
# ============================================================================

# US Holidays
us_holidays = holidays.US()

# Scripts to run
DATA_UPDATE_SCRIPT = "nba_data_daily_update.py"
EDGE_FINDER_SCRIPT = "find_edges_v2_TELEGRAM.py"

# ============================================================================
# GIT SYNC FUNCTIONS
# ============================================================================

def git_push_updates():
    """Push updated CSV files to GitHub"""
    try:
        token = os.getenv('GIT_TOKEN', '')
        user = os.getenv('GIT_USER', '')
        email = os.getenv('GIT_EMAIL', '')
        
        if token and user:
            os.system(f'git config --global user.name "{user}"')
            os.system(f'git config --global user.email "{email}"')
            os.system('git add *.csv nba_data/*.csv results_history.csv edges_*.csv')
            os.system('git commit -m "Update NBA data [automated]"')
            os.system(f'git push https://{token}@github.com/{user}/nba-dashboard.git main')
            print("✅ Pushed updates to GitHub")
        else:
            print("⚠️ Git credentials not configured")
    except Exception as e:
        print(f"❌ Git push failed: {e}")

# ============================================================================
# JOB FUNCTIONS
# ============================================================================

def run_data_update():
    """Run the data update script"""
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
    except subprocess.TimeoutExpired:
        print("⏱️ Data update timed out after 5 minutes")
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
    except subprocess.TimeoutExpired:
        print("⏱️ Edge finder timed out after 5 minutes")
    except Exception as e:
        print(f"❌ Error running edge finder: {e}")
    
    print(f"{'='*70}\n")
    
    # Push results to GitHub after edge finder completes
    git_push_updates()

def is_weekend():
    """Check if today is Saturday or Sunday"""
    return datetime.now().weekday() >= 5

def is_holiday():
    """Check if today is a US national holiday"""
    today = datetime.now().date()
    return today in us_holidays

def should_run_at_morning():
    """Determine if we should run in the morning today"""
    return is_weekend() or is_holiday()

def daily_check():
    """Daily check to determine when to schedule today's run"""
    current_time = datetime.now().strftime('%Y-%m-%d %I:%M %p')
    day_type = "Weekend" if is_weekend() else "Holiday" if is_holiday() else "Weekday"
    
    print(f"\n{'='*70}")
    print(f"📅 Daily Check - {current_time}")
    print(f"{'='*70}")
    print(f"Day Type: {day_type}")
    
    schedule.clear('daily_run')
    
    if should_run_at_morning():
        data_time = "10:00 AM"
        edge_time = "11:00 AM"
        print(f"⏰ Data Update: {data_time}")
        print(f"⏰ Edge Finder: {edge_time}")
        schedule.every().day.at("10:00").do(run_data_update).tag('daily_run')
        schedule.every().day.at("11:00").do(run_edge_finder).tag('daily_run')
    else:
        data_time = "4:00 PM"
        edge_time = "5:00 PM"
        print(f"⏰ Data Update: {data_time}")
        print(f"⏰ Edge Finder: {edge_time}")
        schedule.every().day.at("16:00").do(run_data_update).tag('daily_run')
        schedule.every().day.at("17:00").do(run_edge_finder).tag('daily_run')
    
    if is_holiday():
        holiday_name = us_holidays.get(datetime.now().date())
        print(f"🎉 Holiday: {holiday_name}")
    
    print(f"{'='*70}\n")

# ============================================================================
# MAIN SCHEDULER
# ============================================================================

def main():
    """Main scheduler loop"""
    print("\n" + "="*70)
    print("🏀 NBA AUTOMATED WORKFLOW SCHEDULER")
    print("="*70)
    print("\nSchedule:")
    print("  • Weekdays:")
    print("    - 4:00 PM: Data Update")
    print("    - 5:00 PM: Edge Finder")
    print("  • Weekends:")
    print("    - 10:00 AM: Data Update")
    print("    - 11:00 AM: Edge Finder")
    print("  • Holidays:")
    print("    - 10:00 AM: Data Update")
    print("    - 11:00 AM: Edge Finder")
    print("\n" + "="*70 + "\n")
    
    # Run daily check at midnight
    schedule.every().day.at("00:01").do(daily_check)
    
    # Run initial check
    daily_check()
    
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
