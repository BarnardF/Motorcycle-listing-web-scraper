"""
Test script for price tracking functionality
Simulates multiple runs to test price drops without actual scraping
AI(Claude) generated test scenarios - 7 Nov 2025
"""
import json
import os
from datetime import datetime
from template_generator.html_generator import generate_html_report


# Mock data for testing
def create_mock_listing(listing_id, title, price, search_term, source, old_price=None, price_dropped=False):
    """Create a mock listing for testing"""
    listing = {
        'id': listing_id,
        'title': title,
        'price': price,
        'price_history': [{
            'date': datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            'price': price
        }],
        'url': f'https://example.com/listing/{listing_id}',
        'search_term': search_term,
        'source': source,
        'found_date': datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
        'kilometers': '5,000 km',
        'location': 'Johannesburg',
        'condition': 'Used'
    }
    
    if old_price:
        listing['old_price'] = old_price
        listing['price_dropped'] = price_dropped
        listing['price_history'].insert(0, {
            'date': '01-11-2025 10:00:00',
            'price': old_price
        })
    
    return listing


def test_scenario_1_first_run():
    """Test Scenario 1: First run - no previous data"""
    print("\n" + "="*70)
    print("TEST SCENARIO 1: First Run (No Previous Data)")
    print("="*70)
    
    listings = [
        create_mock_listing('at_12345', '2024 Honda Rebel 500', 'R 85,000', 'Honda Rebel 500', 'AutoTrader'),
        create_mock_listing('at_12346', '2023 Honda Rebel 500', 'R 75,000', 'Honda Rebel 500', 'AutoTrader'),
        create_mock_listing('gt_54321', '2024 Triumph Scrambler 400', 'R 95,000', 'Triumph Scrambler 400', 'Gumtree'),
    ]
    
    # Save as "previous" data for next test
    previous_data = {
        'Honda Rebel 500': {
            'at_12345': listings[0],
            'at_12346': listings[1]
        },
        'Triumph Scrambler 400': {
            'gt_54321': listings[2]
        }
    }
    
    with open('test_listings.json', 'w') as f:
        json.dump(previous_data, f, indent=2)
    
    # Generate HTML
    bikes = ['Honda Rebel 500', 'Triumph Scrambler 400']
    generate_html_report(listings, bikes, "docs/test_index.html")
    
    print("✓ Created 3 initial listings")
    print("✓ Saved to test_listings.json")
    print("✓ Generated docs/test_index.html")
    print("\nExpected Result: 3 listings, no price drops")
    

def test_scenario_2_price_drops():
    """Test Scenario 2: Second run - some prices dropped"""
    print("\n" + "="*70)
    print("TEST SCENARIO 2: Second Run (Price Drops Detected)")
    print("="*70)
    
    # Load previous data
    with open('test_listings.json', 'r') as f:
        previous = json.load(f)
    
    # Simulate current run with price changes
    listings = [
        # Price dropped from R 85,000 to R 79,000
        create_mock_listing('at_12345', '2024 Honda Rebel 500', 'R 79,000', 'Honda Rebel 500', 'AutoTrader', 
                          old_price='R 85,000', price_dropped=True),
        
        # No price change
        create_mock_listing('at_12346', '2023 Honda Rebel 500', 'R 75,000', 'Honda Rebel 500', 'AutoTrader'),
        
        # Price dropped from R 95,000 to R 89,500
        create_mock_listing('gt_54321', '2024 Triumph Scrambler 400', 'R 89,500', 'Triumph Scrambler 400', 'Gumtree',
                          old_price='R 95,000', price_dropped=True),
        
        # New listing (not a price drop, just new)
        create_mock_listing('at_12347', '2025 BMW G 310 GS', 'R 105,000', 'BMW G 310 GS', 'AutoTrader'),
    ]
    
    # Simulate price comparison logic
    print("\nSimulating Price Comparison Logic:")
    print("-" * 70)
    
    for listing in listings:
        if listing.get('price_dropped'):
            old = listing['old_price'].replace('R', '').replace(',', '').replace(' ', '').strip()
            new = listing['price'].replace('R', '').replace(',', '').replace(' ', '').strip()
            drop = int(old) - int(new)
            print(f"💰 PRICE DROP: {listing['title']}")
            print(f"   {listing['old_price']} → {listing['price']} (Save R{drop:,}!)")
            print(f"   Source: {listing['source']}")
    
    # Generate HTML
    bikes = ['Honda Rebel 500', 'Triumph Scrambler 400', 'BMW G 310 GS']
    generate_html_report(listings, bikes, "docs/test_index.html")
    
    print("\n✓ Processed 4 listings (1 new, 2 price drops, 1 unchanged)")
    print("✓ Generated docs/test_index.html")
    print("\nExpected Result:")
    print("  - Total listings: 4")
    print("  - Price drops: 2")
    print("  - Price Drops tab should show Honda Rebel and Triumph Scrambler")


def test_scenario_3_mixed_changes():
    """Test Scenario 3: Complex scenario with various changes"""
    print("\n" + "="*70)
    print("TEST SCENARIO 3: Complex Scenario (Multiple Changes)")
    print("="*70)
    
    listings = [
        # Multiple price drops on same bike
        create_mock_listing('at_12345', '2024 Honda Rebel 500', 'R 75,000', 'Honda Rebel 500', 'AutoTrader', 
                          old_price='R 79,000', price_dropped=True),
        
        # Price increased (not a drop)
        create_mock_listing('at_12346', '2023 Honda Rebel 500', 'R 78,000', 'Honda Rebel 500', 'AutoTrader'),
        
        # Big price drop
        create_mock_listing('gt_54321', '2024 Triumph Scrambler 400', 'R 79,999', 'Triumph Scrambler 400', 'Gumtree',
                          old_price='R 89,500', price_dropped=True),
        
        # Small price drop
        create_mock_listing('at_12347', '2025 BMW G 310 GS', 'R 103,500', 'BMW G 310 GS', 'AutoTrader',
                          old_price='R 105,000', price_dropped=True),
        
        # Brand new listing
        create_mock_listing('gt_98765', '2024 Kawasaki Ninja 400', 'R 92,000', 'Kawasaki Ninja 400', 'Gumtree'),
    ]
    
    print("\nPrice Changes Detected:")
    print("-" * 70)
    
    drop_count = 0
    for listing in listings:
        if listing.get('price_dropped'):
            old = listing['old_price'].replace('R', '').replace(',', '').replace(' ', '').strip()
            new = listing['price'].replace('R', '').replace(',', '').replace(' ', '').strip()
            drop = int(old) - int(new)
            drop_count += 1
            print(f"💰 {listing['title']}: {listing['old_price']} → {listing['price']} (-R{drop:,})")
    
    # Generate HTML
    bikes = ['Honda Rebel 500', 'Triumph Scrambler 400', 'BMW G 310 GS', 'Kawasaki Ninja 400']
    generate_html_report(listings, bikes, "docs/test_index.html")
    
    print(f"\n✓ Processed 5 listings")
    print(f"✓ Price drops detected: {drop_count}")
    print("✓ Generated docs/test_index.html")
    print("\nExpected Result:")
    print("  - Total listings: 5")
    print("  - Price drops: 3")
    print("  - Honda Rebel dropped twice (from R85k → R79k → R75k)")


def run_all_tests():
    """Run all test scenarios"""
    print("\n" + "="*70)
    print("MOTORCYCLE TRACKER - PRICE TRACKING TEST SUITE")
    print("="*70)
    
    try:
        # Ensure docs directory exists
        os.makedirs("docs", exist_ok=True)
        
        # Run test scenarios
        test_scenario_1_first_run()
        input("\n▶ Press Enter to run Scenario 2 (Price Drops)...")
        
        test_scenario_2_price_drops()
        input("\n▶ Press Enter to run Scenario 3 (Complex Changes)...")
        
        test_scenario_3_mixed_changes()
        
        print("\n" + "="*70)
        print("✅ ALL TESTS COMPLETE")
        print("="*70)
        print("\n📊 View Results:")
        print("   Open: docs/test_index.html in your browser")
        print("\n🔍 What to Check:")
        print("   1. All three tabs work (By Bike, By Source, Price Drops)")
        print("   2. Price Drops tab shows only listings with drops")
        print("   3. Old prices have strikethrough styling")
        print("   4. Price drop rows have green background")
        print("   5. Statistics show correct counts")
        
        # Cleanup
        print("\n🧹 Cleanup:")
        if os.path.exists('test_listings.json'):
            os.remove('test_listings.json')
            print("   ✓ Removed test_listings.json")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()
