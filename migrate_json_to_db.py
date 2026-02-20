"""
Migration Script: JSON to SQLite
Converts existing listings.json to listings.db
Run this ONCE before switching to the database-based tracker.
"""

import json
import os
from pathlib import Path
from logger.logger import logger
from template_generator.db_manager import DatabaseManager


def migrate_json_to_db(json_file="data/listings.json", db_file="data/listings.db"):
    """
    Migrate listings from JSON to SQLite database.
    Handles duplicate IDs that appear in multiple bike categories.
    
    Args:
        json_file: Path to existing listings.json
        db_file: Path to new listings.db (will be created)
    """
    
    logger.info("=" * 60)
    logger.info("MIGRATION: JSON → SQLite")
    logger.info("=" * 60)
    
    # Check if JSON file exists
    if not Path(json_file).exists():
        logger.error(f"JSON file not found: {json_file}")
        return False
    
    # Load JSON data
    logger.info(f"Loading JSON data from {json_file}...")
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            listings_data = json.load(f)
        original_count = sum(len(v) for v in listings_data.values())
        logger.info(f"Loaded {original_count} listings from JSON")
    except Exception as e:
        logger.error(f"Failed to load JSON: {e}")
        return False
    
    # Remove old DB if it exists (start fresh)
    if Path(db_file).exists():
        logger.info(f"Removing existing database: {db_file}")
        os.remove(db_file)
    
    # Initialize database
    logger.info("Initializing SQLite database...")
    try:
        db = DatabaseManager(db_file)
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        return False
    
    # Migrate listings, tracking duplicates
    logger.info("Migrating listings to database...")
    
    try:
        cursor = db.conn.cursor()
        count = 0
        failed = 0
        duplicates = set()
        
        for bike_model, bike_listings in listings_data.items():
            for listing_id, listing in bike_listings.items():
                try:
                    # Check if this listing ID already exists
                    cursor.execute('SELECT id FROM listings WHERE id = ?', (listing_id,))
                    if cursor.fetchone():
                        duplicates.add(listing_id)
                        logger.debug(f"Skipping duplicate {listing_id} (already migrated from different bike category)")
                        continue
                    
                    # Validate required fields
                    if not listing.get('id'):
                        listing['id'] = listing_id
                    
                    title = listing.get('title', '')
                    price = listing.get('price', 'N/A')
                    url = listing.get('url', '')
                    search_term = listing.get('search_term', bike_model)
                    source = listing.get('source', 'Unknown')
                    
                    # Insert listing
                    cursor.execute('''
                        INSERT INTO listings 
                        (id, title, price, old_price, price_dropped, url, 
                         search_term, source, kilometers, location, found_date)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        listing_id,
                        title,
                        price,
                        listing.get('old_price'),
                        listing.get('price_dropped', False),
                        url,
                        search_term,
                        source,
                        listing.get('kilometers'),
                        listing.get('location'),
                        listing.get('found_date')
                    ))
                    
                    # Save price history
                    price_history = listing.get('price_history', [])
                    for entry in price_history:
                        try:
                            cursor.execute('''
                                INSERT OR IGNORE INTO price_history 
                                (listing_id, price, date)
                                VALUES (?, ?, ?)
                            ''', (listing_id, entry.get('price'), entry.get('date')))
                        except Exception as ph_err:
                            logger.debug(f"Price history error for {listing_id}: {ph_err}")
                    
                    count += 1
                    
                except Exception as item_err:
                    failed += 1
                    logger.warning(f"Failed to migrate {listing_id}: {item_err}")
                    continue
        
        db.conn.commit()
        logger.info(f"Migrated {count} listings successfully")
        if duplicates:
            logger.info(f"Skipped {len(duplicates)} duplicate IDs (same listing in multiple bike categories)")
            for dup_id in sorted(duplicates):
                logger.debug(f"  - {dup_id}")
        if failed:
            logger.info(f"Failed to migrate {failed} listings")
        
    except Exception as e:
        logger.error(f"Migration error: {e}")
        db.conn.rollback()
        db.close()
        return False
    
    # Verify migration
    logger.info("Verifying migration...")
    try:
        cursor.execute('SELECT COUNT(*) as cnt FROM listings')
        migrated_count = cursor.fetchone()['cnt']
        
        logger.info("=" * 60)
        logger.info("MIGRATION COMPLETE")
        logger.info("=" * 60)
        logger.info(f"Original entries (JSON): {original_count}")
        logger.info(f"  (includes {len(duplicates)} duplicates from multiple categories)")
        logger.info(f"Unique listings (DB):    {migrated_count}")
        logger.info(f"Expected unique count:   {original_count - len(duplicates)}")
        
        if migrated_count == (original_count - len(duplicates)):
            logger.info("Perfect migration - all unique listings transferred")
            db.close()
            return True
        elif migrated_count > 0:
            logger.info("Migration succeeded - listings in database")
            db.close()
            return True
        else:
            logger.error("No listings migrated")
            db.close()
            return False
            
    except Exception as e:
        logger.error(f"Verification failed: {e}")
        db.close()
        return False


def main():
    """Main entry point"""
    success = migrate_json_to_db()
    
    if success:
        logger.info("\nReady to use SQLite!")
        logger.info("Next steps:")
        logger.info("1. Update main.py to use DatabaseManager")
        logger.info("2. Test the tracker locally: python main.py")
        logger.info("3. Commit changes to GitHub")
    else:
        logger.error("\nMigration failed. Keep using JSON for now.")
    
    return success


if __name__ == "__main__":
    main()