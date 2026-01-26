def main():
    """Main scheduler loop"""
    print("\n" + "="*70)
    print("🏀 NBA AUTOMATED WORKFLOW SCHEDULER")
    print("="*70)
    print("\nSchedule (All times in UTC, converted from EST):")
    print("  • EVERY DAY:")
    print("    - 08:00 UTC (3:00 AM EST): Results Tracker")
    print("\n  • WEEKDAYS:")
    print("    - 21:00 UTC (4:00 PM EST): Data Update")
    print("    - 22:00 UTC (5:00 PM EST): Edge Finder")
    print("\n  • WEEKENDS & HOLIDAYS:")
    print("    - 15:00 UTC (10:00 AM EST): Data Update")
    print("    - 16:00 UTC (11:00 AM EST): Edge Finder")
    print("\n" + "="*70 + "\n")

    # Results tracker at 3 AM EST (8 AM UTC) EVERY DAY
    schedule.every().day.at("08:00").do(run_results_tracker)

    # Daily check at 12:01 AM EST (5:01 AM UTC)
    schedule.every().day.at("05:01").do(daily_check)

    # Run initial check
    daily_check()

    print("✅ Scheduler is running... Press Ctrl+C to stop\n")

    try:
        while True:
            schedule.run_pending()
            time.sleep(60)
    except KeyboardInterrupt:
        print("\n\n👋 Scheduler stopped by user")
