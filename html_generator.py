"""
HTML Report Generator for Motorcycle Listings
Generates a beautiful static HTML page for GitHub Pages
Created with ai(Claude) - 1 Nov 2025
"""
from datetime import datetime
from logger.logger import logger
import os


def generate_html_report(all_listings, bikes_tracked, output_file="docs/index.html"):
    """
    Generate a beautiful HTML report of motorcycle listings
    
    Args:
        all_listings: List of all listings found
        bikes_tracked: List of bike models being tracked
        output_file: Path to output HTML file
    """
    try:
        # Ensure docs directory exists
        os.makedirs("docs", exist_ok=True)
        
        # Group listings by bike model
        listings_by_bike = {}
        for listing in all_listings:
            bike = listing['search_term']
            if bike not in listings_by_bike:
                listings_by_bike[bike] = []
            listings_by_bike[bike].append(listing)
        
        # Group by source
        listings_by_source = {}
        for listing in all_listings:
            source = listing['source']
            if source not in listings_by_source:
                listings_by_source[source] = []
            listings_by_source[source].append(listing)
        
        # Generate timestamp in South African format
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        
        # Build HTML with embedded styles and JavaScript
        html = generate_html_template(
            all_listings, 
            bikes_tracked, 
            listings_by_bike, 
            listings_by_source, 
            timestamp
        )
        
        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        logger.info(f"Generated HTML report: {output_file}")
        logger.info(f" - Total listings: {len(all_listings)}")
        logger.info(f" - Bikes with listings: {len(listings_by_bike)}")
        logger.info(f" - Sources: {len(listings_by_source)}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error generating HTML report: {e}")
        return False


def generate_html_template(all_listings, bikes_tracked, listings_by_bike, listings_by_source, timestamp):
    """Generate the complete HTML template"""
    
    sources_count = len(listings_by_source)
    
    html = f"""<!DOCTYPE HTML>
<html>
<head>
    <title>Motorcycle Listings Tracker</title>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1, user-scalable=no" />
    <link rel="stylesheet" href="styles.css">
    <link href="https://fonts.googleapis.com/css?family=Roboto:100,300,400,100italic,300italic" rel="stylesheet">
</head>

<body>
    <section class="wrapper">
        <div class="container">
            <header class="major">
                <h1>🏍️ Motorcycle Listings Tracker</h1>
                <p>Tracking {len(bikes_tracked)} motorcycle models across South African websites</p>
            </header>

            <!-- Statistics -->
            <div class="stats">
                <div class="stat-box">
                    <span class="stat-number">{len(all_listings)}</span>
                    <span class="stat-label">Total Listings</span>
                </div>
                <div class="stat-box">
                    <span class="stat-number">{len(bikes_tracked)}</span>
                    <span class="stat-label">Bikes Tracked</span>
                </div>
                <div class="stat-box">
                    <span class="stat-number">{sources_count}</span>
                    <span class="stat-label">Sources</span>
                </div>
            </div>

            <!-- View Toggle Buttons -->
            <div class="view-toggle">
                <button class="toggle-btn active" onclick="showView('bike')">📋 By Bike Model</button>
                <button class="toggle-btn" onclick="showView('source')">🏪 By Source</button>
            </div>
"""

    # Generate both views
    html += generate_bike_view(listings_by_bike)
    html += generate_source_view(listings_by_source)

    # Footer
    html += f"""
            <div class="timestamp">
                Last updated: {timestamp}
            </div>
        </div>
    </section>

    <script>
        function showView(viewType) {{
            // Hide all views
            document.querySelectorAll('.view-container').forEach(el => {{
                el.classList.add('hidden');
            }});

            // Show selected view
            document.getElementById(viewType + '-view').classList.remove('hidden');

            // Update button states
            document.querySelectorAll('.toggle-btn').forEach(btn => {{
                btn.classList.remove('active');
            }});
            
            event.target.classList.add('active');
        }}
    </script>
</body>

</html>
"""
    
    return html


def generate_bike_view(listings_by_bike):
    """Generate the bike-grouped view"""
    html = '<div id="bike-view" class="view-container">\n'
    
    if not listings_by_bike:
        html += '<div class="no-listings"><p>No listings found yet. Run the tracker to populate this page!</p></div>\n'
    else:
        for bike, listings in listings_by_bike.items():
            html += f"""
            <div class="table-section">
                <div class="table-header">
                    <h2>{bike}</h2>
                    <span class="listing-count">{len(listings)} listing(s)</span>
                </div>
                <table>
                    <thead>
                        <tr>
                            <th>Source</th>
                            <th>Title</th>
                            <th>Price</th>
                            <th>Kilometers</th>
                            <th>Location</th>
                            <th>Link</th>
                        </tr>
                    </thead>
                    <tbody>
"""
            for listing in listings:
                kilometers = listing.get('kilometers', 'N/A')
                condition = listing.get('condition', 'N/A')
                if kilometers == "N/A" and condition != "N/A":
                    kilometers = condition  # Fallback to condition if kilometers not available
                location = listing.get('location', 'N/A')
                html += f"""
                        <tr>
                            <td class="source">{listing['source']}</td>
                            <td class="bike-name">{listing['title']}</td>
                            <td class="price">{listing['price']}{"<span class='badge'>Price dropped!</span>" if listing.get('price_dropped') else ""}</td>

                            <td class="kilometers">{kilometers}</td>
                            <td class="location">{location}</td>
                            <td><a href="{listing['url']}" target="_blank" class="view-link">View →</a></td>
                        </tr>
"""
            html += """
                    </tbody>
                </table>
            </div>
"""
    
    html += '</div>\n'
    return html



def generate_source_view(listings_by_source):
    """Generate the source-grouped view"""
    html = '<div id="source-view" class="view-container hidden">\n'
    
    if not listings_by_source:
        html += '<div class="no-listings"><p>No listings found yet. Run the tracker to populate this page!</p></div>\n'
    else:
        for source, listings in listings_by_source.items():
            html += f"""
            <div class="table-section">
                <div class="table-header">
                    <h2>{source}</h2>
                    <span class="listing-count">{len(listings)} listing(s)</span>
                </div>
                <table>
                    <thead>
                        <tr>
                            <th>Bike Model</th>
                            <th>Title</th>
                            <th>Price</th>
                            <th>Kilometers</th>
                            <th>Location</th>
                            <th>Link</th>
                        </tr>
                    </thead>
                    <tbody>
"""
            for listing in listings:
                kilometers = listing.get('kilometers', 'N/A')
                condition = listing.get('condition', 'N/A')
                if kilometers == "N/A" and condition != "N/A":
                    kilometers = condition  # Fallback to condition if kilometers not available
                location = listing.get('location', 'N/A')
                html += f"""
                        <tr>
                            <td class="bike-name">{listing['search_term']}</td>
                            <td>{listing['title']}</td>
                            <td class="price">{listing['price']}{" <span class='badge'>Price dropped!</span>" if listing.get('price_dropped') else ""}</td>
                            <td class="kilometers">{kilometers}</td>
                            <td class="location">{location}</td>
                            <td><a href="{listing['url']}" target="_blank" class="view-link">View →</a></td>
                        </tr>
"""
            html += """
                    </tbody>
                </table>
            </div>
"""
    
    html += '</div>\n'
    return html
