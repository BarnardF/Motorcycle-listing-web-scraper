"""
Database Manager for Motorcycle Listings
Handles all SQLite operations - read, write, price tracking, etc.
Replaces JSON file storage with proper relational database.
Claude assisted - 20 Feb 2026
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from logger.logger import logger
from config.config import DATA_FILE

DB_FILE = "data/listings.db"


class DatabaseManager:
    """Manages all SQLite database operations for motorcycle listings"""
    
    def __init__(self, db_path=DB_FILE):
        self.db_path = db_path
        self.conn = None
        self.init_db()
    
    def init_db(self):
        """Initialize database and create tables if they don't exist"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            cursor = self.conn.cursor()
            
            # Create listings table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS listings (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    price TEXT,
                    old_price TEXT,
                    price_dropped BOOLEAN DEFAULT 0,
                    url TEXT NOT NULL,
                    search_term TEXT NOT NULL,
                    source TEXT NOT NULL,
                    kilometers TEXT,
                    location TEXT,
                    found_date TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create price_history table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS price_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    listing_id TEXT NOT NULL,
                    price TEXT NOT NULL,
                    date TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(listing_id) REFERENCES listings(id)
                        ON DELETE CASCADE
                )
            ''')
            
            # Create index for faster queries
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_listing_source 
                ON listings(source)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_listing_search_term 
                ON listings(search_term)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_price_history_listing 
                ON price_history(listing_id)
            ''')
            
            self.conn.commit()
            logger.debug("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    def save_listings(self, all_listings_dict):
        """
        Save listings from nested dict to database.
        
        Args:
            all_listings_dict: Dict organized by bike model
                              {bike_model: {listing_id: listing_data}}
        """
        try:
            cursor = self.conn.cursor()
            count = 0
            
            for bike_model, bike_listings in all_listings_dict.items():
                for listing_id, listing in bike_listings.items():
                    # Check if listing exists
                    cursor.execute('SELECT id FROM listings WHERE id = ?', (listing_id,))
                    exists = cursor.fetchone() is not None
                    
                    if exists:
                        # Update existing listing
                        cursor.execute('''
                            UPDATE listings SET
                                title = ?,
                                price = ?,
                                old_price = ?,
                                price_dropped = ?,
                                url = ?,
                                search_term = ?,
                                source = ?,
                                kilometers = ?,
                                location = ?,
                                found_date = ?,
                                updated_at = CURRENT_TIMESTAMP
                            WHERE id = ?
                        ''', (
                            listing.get('title'),
                            listing.get('price'),
                            listing.get('old_price'),
                            listing.get('price_dropped', False),
                            listing.get('url'),
                            listing.get('search_term'),
                            listing.get('source'),
                            listing.get('kilometers'),
                            listing.get('location'),
                            listing.get('found_date'),
                            listing_id
                        ))
                    else:
                        # Insert new listing
                        cursor.execute('''
                            INSERT INTO listings 
                            (id, title, price, old_price, price_dropped, url, 
                             search_term, source, kilometers, location, found_date)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            listing_id,
                            listing.get('title'),
                            listing.get('price'),
                            listing.get('old_price'),
                            listing.get('price_dropped', False),
                            listing.get('url'),
                            listing.get('search_term'),
                            listing.get('source'),
                            listing.get('kilometers'),
                            listing.get('location'),
                            listing.get('found_date')
                        ))
                    
                    # Save price history
                    price_history = listing.get('price_history', [])
                    for entry in price_history:
                        cursor.execute('''
                            INSERT OR IGNORE INTO price_history 
                            (listing_id, price, date)
                            VALUES (?, ?, ?)
                        ''', (listing_id, entry.get('price'), entry.get('date')))
                    
                    count += 1
            
            self.conn.commit()
            logger.info(f"Saved {count} listings to database")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save listings: {e}")
            self.conn.rollback()
            return False
    
    def get_all_listings(self):
        """
        Get all listings from database, organized by bike model.
        Returns format compatible with main.py processing.
        
        Returns:
            Dict: {bike_model: {listing_id: listing_data}}
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM listings')
            
            all_listings = {}
            
            for row in cursor.fetchall():
                listing_id = row['id']
                bike_model = row['search_term']
                
                # Get price history for this listing
                cursor.execute('''
                    SELECT price, date FROM price_history 
                    WHERE listing_id = ?
                    ORDER BY date ASC
                ''', (listing_id,))
                
                price_history = [
                    {'price': ph_row['price'], 'date': ph_row['date']}
                    for ph_row in cursor.fetchall()
                ]
                
                listing = {
                    'id': row['id'],
                    'title': row['title'],
                    'price': row['price'],
                    'old_price': row['old_price'],
                    'price_dropped': bool(row['price_dropped']),
                    'url': row['url'],
                    'search_term': row['search_term'],
                    'source': row['source'],
                    'kilometers': row['kilometers'],
                    'location': row['location'],
                    'found_date': row['found_date'],
                    'price_history': price_history
                }
                
                if bike_model not in all_listings:
                    all_listings[bike_model] = {}
                
                all_listings[bike_model][listing_id] = listing
            
            return all_listings
            
        except Exception as e:
            logger.error(f"Failed to get listings: {e}")
            return {}
    
    def get_listings_by_bike(self, bike_model):
        """Get all listings for a specific bike model"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT * FROM listings WHERE search_term = ?
            ''', (bike_model,))
            
            listings = {}
            for row in cursor.fetchall():
                listing_id = row['id']
                
                cursor.execute('''
                    SELECT price, date FROM price_history 
                    WHERE listing_id = ?
                    ORDER BY date ASC
                ''', (listing_id,))
                
                price_history = [
                    {'price': ph['price'], 'date': ph['date']}
                    for ph in cursor.fetchall()
                ]
                
                listings[listing_id] = {
                    'id': row['id'],
                    'title': row['title'],
                    'price': row['price'],
                    'old_price': row['old_price'],
                    'price_dropped': bool(row['price_dropped']),
                    'url': row['url'],
                    'search_term': row['search_term'],
                    'source': row['source'],
                    'kilometers': row['kilometers'],
                    'location': row['location'],
                    'found_date': row['found_date'],
                    'price_history': price_history
                }
            
            return listings
            
        except Exception as e:
            logger.error(f"Failed to get listings for {bike_model}: {e}")
            return {}
    
    def get_price_drops(self):
        """Get all listings with price drops"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM listings WHERE price_dropped = 1')
            
            listings = []
            for row in cursor.fetchall():
                listing_id = row['id']
                
                cursor.execute('''
                    SELECT price, date FROM price_history 
                    WHERE listing_id = ?
                    ORDER BY date ASC
                ''', (listing_id,))
                
                price_history = [
                    {'price': ph['price'], 'date': ph['date']}
                    for ph in cursor.fetchall()
                ]
                
                listings.append({
                    'id': row['id'],
                    'title': row['title'],
                    'price': row['price'],
                    'old_price': row['old_price'],
                    'price_dropped': True,
                    'url': row['url'],
                    'search_term': row['search_term'],
                    'source': row['source'],
                    'kilometers': row['kilometers'],
                    'location': row['location'],
                    'found_date': row['found_date'],
                    'price_history': price_history
                })
            
            return listings
            
        except Exception as e:
            logger.error(f"Failed to get price drops: {e}")
            return []
    
    def delete_listing(self, listing_id):
        """Delete a listing and its price history"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('DELETE FROM listings WHERE id = ?', (listing_id,))
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to delete listing {listing_id}: {e}")
            self.conn.rollback()
            return False
    
    def delete_listings_not_in(self, current_listing_ids):
        """
        Delete listings that are NOT in the current list.
        Used for stale listing cleanup.
        
        Args:
            current_listing_ids: Set of listing IDs to keep
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT id FROM listings')
            all_ids = set(row['id'] for row in cursor.fetchall())
            
            to_delete = all_ids - current_listing_ids
            
            for listing_id in to_delete:
                cursor.execute('DELETE FROM listings WHERE id = ?', (listing_id,))
            
            self.conn.commit()
            logger.info(f"Deleted {len(to_delete)} stale listings")
            return len(to_delete)
            
        except Exception as e:
            logger.error(f"Failed to clean stale listings: {e}")
            self.conn.rollback()
            return 0
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.debug("Database connection closed")
    
    def __del__(self):
        """Ensure connection is closed on object deletion"""
        self.close()