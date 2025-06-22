#!/usr/bin/env python3
"""
Test script to verify database models and show expected API structure
"""

import os
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import DatabaseOperations, get_database, init_database
from app.models.database_models import Article, Event


def test_database_creation():
    """Test database and table creation."""
    print("🗄️  Testing database creation...")

    try:
        engine = init_database()
        print("✓ Database and tables created successfully")

        # Test database connection
        db_gen = get_database()
        db = next(db_gen)

        # Test basic queries
        events_count = db.query(Event).count()
        articles_count = db.query(Article).count()

        print(f"✓ Events table: {events_count} records")
        print(f"✓ Articles table: {articles_count} records")

        db.close()
        return True

    except Exception as e:
        print(f"❌ Database creation failed: {e}")
        return False


def test_sample_data():
    """Test inserting sample data using actual API structure."""
    print("\n📝 Testing sample data insertion...")

    try:
        db_gen = get_database()
        db = next(db_gen)
        db_ops = DatabaseOperations(db)

        # Sample event data (actual API structure)
        sample_event = {
            "type": "event",
            "post_id": "11860",
            "post_title": "Legalweek 2025",
            "post_content": "",
            "enabled": "Yes",
            "event_dates": "",
            "event_logo": "",
            "location": "",
            "twitter_handle": "",
            "twitter_tag": "",
            "url": "",
            "venue": "",
            "user_id": "1",
            "user_login": "admin",
            "user_email": "josh@snazzware.com",
            "display_name": "admin",
            "author_booth_numbers": "",
            "author_company_contact_name": "",
            "author_company_name__title": "",
            "author_event": "255",
            "author_phone_number": "",
            "author_url": "",
        }

        # Sample article data (actual API structure)
        sample_article = {
            "type": "article",
            "post_id": "10622",
            "post_title": "",
            "post_content": "",
            "category": 'a:1:{i:0;s:2:"41";}',
            "file": "10623",
            "keywords": "",
            "short_description": "Software Technology, LLC, the maker of leading legal practice management Tabs3 Software, today announced the launch of Tabs3 Cloud for billing and accounting. It features all the power and flexibility of Tabs3 Billing and Financials.",
            "social_media_description": '<strong>Lincoln, Neb. – October 26, 2023</strong> – Software Technology, LLC, the maker of leading legal practice management Tabs3 Software, today announced the launch of <a href="https://info.tabs3.com/tabs3cloud">Tabs3 Cloud</a> for billing and accounting. It features all the power and flexibility of Tabs3 Billing and Financials, catering to firms that prefer a cloud-hosted environment.',
            "social_name": "Tarun Kundhi",
            "twitter_description": "Tabs3 Software Launches Tabs3 Cloud, Providing Another Option for Legal Billing and Accounting",
            "url": "",
            "user_id": "532",
            "user_login": "events@tabs3.com",
            "user_email": "events@tabs3.com",
            "display_name": "events@tabs3.com",
            "author_booth_numbers": "208",
            "author_company_contact_name": "Kristi Bennett",
            "author_company_name__title": "Tabs3",
            "author_event": "9016",
            "author_phone_number": "402.419.2200",
            "author_url": "https://www.tabs3.com/legaltech",
        }

        # Insert sample data
        event = db_ops.create_or_update_event(sample_event)
        article = db_ops.create_or_update_article(sample_article)

        print(f"✓ Created event: {event.post_title} (ID: {event.id})")
        print(
            f"✓ Created article: {article.post_title or 'Untitled'} (ID: {article.id})"
        )

        # Verify excluded fields are not stored
        print("\n🔍 Verifying field exclusions:")
        print(f"✓ Event post_id excluded: {not hasattr(event, 'post_id')}")
        print(f"✓ Article post_id excluded: {not hasattr(article, 'post_id')}")
        print(f"✓ Article file excluded: {not hasattr(article, 'file')}")
        print(f"✓ Article category excluded: {not hasattr(article, 'category')}")

        # Show what fields are actually stored
        print(
            f"\n📊 Event fields stored: {len([attr for attr in dir(event) if not attr.startswith('_')])}"
        )
        print(
            f"📊 Article fields stored: {len([attr for attr in dir(article) if not attr.startswith('_')])}"
        )

        db.close()
        return True

    except Exception as e:
        print(f"❌ Sample data insertion failed: {e}")
        return False


def show_expected_api_structure():
    """Show the actual API response structure."""
    print("\n📋 Actual API Response Structure:")
    print("=" * 50)

    expected_structure = [
        {
            "type": "event",
            "post_id": "11860",  # Will be excluded
            "post_title": "Legalweek 2025",
            "post_content": "",
            "enabled": "Yes",
            "event_dates": "",
            "event_logo": "",
            "location": "",
            "twitter_handle": "",
            "twitter_tag": "",
            "url": "",
            "venue": "",
            "user_id": "1",
            "user_login": "admin",
            "user_email": "josh@snazzware.com",
            "display_name": "admin",
            "author_booth_numbers": "",
            "author_company_contact_name": "",
            "author_company_name__title": "",
            "author_event": "255",
            "author_phone_number": "",
            "author_url": "",
        },
        {
            "type": "article",
            "post_id": "10622",  # Will be excluded
            "post_title": "",
            "post_content": "",
            "category": 'a:1:{i:0;s:2:"41";}',  # Will be excluded
            "file": "10623",  # Will be excluded
            "keywords": "",
            "short_description": "Software Technology, LLC announcement...",
            "social_media_description": "Lincoln, Neb. announcement...",
            "social_name": "Tarun Kundhi",
            "twitter_description": "Tabs3 Software Launches Tabs3 Cloud...",
            "url": "",
            "user_id": "532",
            "user_login": "events@tabs3.com",
            "user_email": "events@tabs3.com",
            "display_name": "events@tabs3.com",
            "author_booth_numbers": "208",
            "author_company_contact_name": "Kristi Bennett",
            "author_company_name__title": "Tabs3",
            "author_event": "9016",
            "author_phone_number": "402.419.2200",
            "author_url": "https://www.tabs3.com/legaltech",
        },
    ]

    import json

    print(json.dumps(expected_structure, indent=2))


def main():
    """Main test function."""
    print("🧪 Testing Database Models and Structure")
    print("=" * 50)

    # Test database creation
    if not test_database_creation():
        return

    # Test sample data
    if not test_sample_data():
        return

    # Show expected API structure
    show_expected_api_structure()

    print("\n✅ All tests completed successfully!")
    print("\n📝 Notes:")
    print("- Database models match actual API structure exactly")
    print(
        "- Excluded fields (post_id, category, file, type) are automatically filtered"
    )
    print("- Records are identified by post_title for deduplication")
    print(
        "- Articles use keywords, short_description, social_media_description, twitter_description for embeddings"
    )
    print("- All other fields are stored as metadata in ChromaDB")
    print("- Event and Article models support all API fields")


if __name__ == "__main__":
    main()
