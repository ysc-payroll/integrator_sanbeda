"""
San Beda Integration Tool - Reset Database Script
Clears all data from the database
"""

import os
from pathlib import Path

def reset_database():
    """Delete the database file to start fresh"""
    print("=" * 60)
    print("San Beda Integration Tool - Reset Database")
    print("=" * 60)

    db_path = Path(__file__).parent / "database" / "sanbeda_integration.db"

    if db_path.exists():
        print(f"\nFound database at: {db_path}")
        response = input("\n⚠️  This will DELETE all data. Continue? (yes/no): ")

        if response.lower() in ['yes', 'y']:
            os.remove(db_path)
            print("\n✓ Database deleted successfully!")
            print("\nThe database will be recreated when you run the app.")
            print("To add demo data, run: python seed_data.py")
        else:
            print("\n✗ Reset cancelled.")
    else:
        print("\n✓ No database found. Nothing to reset.")
        print("\nTo create a database with demo data, run: python seed_data.py")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    reset_database()
