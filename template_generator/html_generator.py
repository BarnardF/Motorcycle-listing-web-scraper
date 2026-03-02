"""
HTML Report Generator with Horizontal Filter Bar
Generates a beautiful static HTML page for GitHub Pages
Works completely client-side (no backend needed)
Created with ai(Claude) - Dec 2025
"""
from datetime import datetime
from logger.logger import logger
import os
import json


def generate_html_report(all_listings, bikes_tracked, output_file="docs/index.html"):
    """
    Generate a beautiful HTML report of motorcycle listings with filters
    
    Args:
        all_listings: List of all listings found
        bikes_tracked: List of bike models being tracked
        output_file: Path to output HTML file
    """
    try:
        # Ensure docs directory exists
        os.makedirs("docs", exist_ok=True)
        
        # Group listings by search term (bike model)
        listings_by_bike = {}
        for listing in all_listings:
            bike = listing.get('search_term', 'Unknown')
            if bike not in listings_by_bike:
                listings_by_bike[bike] = []
            listings_by_bike[bike].append(listing)
        
        # Group by source
        listings_by_source = {}
        for listing in all_listings:
            source = listing.get('source', 'Unknown')
            if source not in listings_by_source:
                listings_by_source[source] = []
            listings_by_source[source].append(listing)
        
        # Get all unique sources
        all_sources = sorted(list(listings_by_source.keys()))
        
        # Generate timestamp
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        # Build HTML
        html = generate_html_template(
            all_listings, 
            bikes_tracked, 
            listings_by_bike, 
            listings_by_source, 
            all_sources,
            timestamp
        )
        
        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        logger.info(f"Generated HTML report: {output_file}")
        logger.info(f" - Total listings: {len(all_listings)}")
        logger.info(f" - Bikes with listings: {len(listings_by_bike)}")
        logger.info(f" - Sources: {len(all_sources)}")
        
        price_drops = sum(1 for listing in all_listings if listing.get('price_dropped'))
        if price_drops > 0:
            logger.info(f" - Price drops detected: {price_drops}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error generating HTML report: {e}")
        return False


def generate_html_template(all_listings, bikes_tracked, listings_by_bike, listings_by_source, all_sources, timestamp):
    """Generate dashboard-style HTML template"""

    sources_count = len(listings_by_source)
    price_drops_count = sum(1 for listing in all_listings if listing.get('price_dropped'))

    listings_json = json.dumps(all_listings)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Motorcycle Tracker Dashboard</title>
  <link rel="stylesheet" href="style.css">
</head>

<body>

  <h1>Motorcycle Tracker</h1>
  <p class="meta">Tracking {len(bikes_tracked)} models • Last updated: {timestamp}</p>

  <div class="stats">
    <div class="stat">
        <div class="num">{len(all_listings)}</div>
        <div class="lbl">Total Listings</div>
    </div>
    <div class="stat">
        <div class="num">{len(bikes_tracked)}</div>
        <div class="lbl">Bike Models</div>
    </div>
    <div class="stat">
        <div class="num">{sources_count}</div>
        <div class="lbl">Sources</div>
    </div>
    <div class="stat">
        <div class="num">{price_drops_count}</div>
        <div class="lbl">Price Drops</div>
    </div>
  </div>

  <div class="controls">
      <button class="btn active" onclick="showView('bike')">By Bike</button>
      <button class="btn" onclick="showView('source')">By Source</button>
      <button class="btn" onclick="showView('drops')">Price Drops</button>
  </div>

  <div id="bike-view" class="view-container"></div>
  <div id="source-view" class="view-container hidden"></div>
  <div id="drops-view" class="view-container hidden"></div>

  <div class="timestamp">
      Last updated: {timestamp}
  </div>

<script>
const allListings = {listings_json};
let filteredListings = [...allListings];

document.addEventListener('DOMContentLoaded', function() {{
    updateBikeView();
}});

function showView(viewType) {{
    document.querySelectorAll('.view-container').forEach(el => el.classList.add('hidden'));
    document.getElementById(viewType + '-view').classList.remove('hidden');

    document.querySelectorAll('.btn').forEach(btn => btn.classList.remove('active'));
    event.target.classList.add('active');

    updateTableDisplay();
}}

function updateTableDisplay() {{
    const activeView = document.querySelector('.view-container:not(.hidden)');
    const viewType = activeView?.id.replace('-view','') || 'bike';

    if (viewType === 'bike') updateBikeView();
    else if (viewType === 'source') updateSourceView();
    else if (viewType === 'drops') updateDropsView();
}}

function updateBikeView() {{
    const container = document.getElementById('bike-view');
    const byBike = {{}};

    filteredListings.forEach(listing => {{
        const bike = listing.search_term;
        if (!byBike[bike]) byBike[bike] = [];
        byBike[bike].push(listing);
    }});

    container.innerHTML = '';

    for (const [bike, listings] of Object.entries(byBike)) {{
        container.innerHTML += generateTableSection(bike, listings, 'bike');
    }}
}}

function updateSourceView() {{
    const container = document.getElementById('source-view');
    const bySource = {{}};

    filteredListings.forEach(listing => {{
        const source = listing.source;
        if (!bySource[source]) bySource[source] = [];
        bySource[source].push(listing);
    }});

    container.innerHTML = '';

    for (const [source, listings] of Object.entries(bySource)) {{
        container.innerHTML += generateTableSection(source, listings, 'source');
    }}
}}

function updateDropsView() {{
    const container = document.getElementById('drops-view');
    const drops = filteredListings.filter(l => l.price_dropped);

    container.innerHTML = '';
    container.innerHTML += generateDropsTable(drops);
}}

function generateTableSection(title, listings, type) {{
    let html = `
    <div class="table-section">
        <div class="table-header">
            <h2>${{title}}</h2>
            <span class="listing-count">${{listings.length}} listing(s)</span>
        </div>
        <table>
            <thead>
                <tr>
                    <th>${{type === 'bike' ? 'Source' : 'Bike Model'}}</th>
                    <th>Title</th>
                    <th>Price</th>
                    <th>Kilometers</th>
                    <th>Location</th>
                    <th>Link</th>
                </tr>
            </thead>
            <tbody>
    `;

    listings.forEach(listing => {{
        const priceDisplay = listing.price_dropped && listing.old_price
            ? `<span class='old-price'>${{listing.old_price}}</span> ${{listing.price}}`
            : listing.price;

        html += `
            <tr class="${{listing.price_dropped ? 'price-drop-row' : ''}}">
                <td>${{type === 'bike' ? listing.source : listing.search_term}}</td>
                <td>${{listing.title}}</td>
                <td class="price">${{priceDisplay}}</td>
                <td>${{listing.kilometers}}</td>
                <td>${{listing.location}}</td>
                <td><a href="${{listing.url}}" target="_blank" class="view-link">View →</a></td>
            </tr>
        `;
    }});

    html += `</tbody></table></div>`;
    return html;
}}

function generateDropsTable(listings) {{
    return generateTableSection("Price Drops", listings, "drops");
}}
</script>

</body>
</html>
"""
    return html


def generate_bike_view(listings_by_bike):
    """Generate the bike-grouped view container"""
    html = '<div id="bike-view" class="view-container">\n'
    if not listings_by_bike:
        html += '<div class="no-listings"><p>No listings found yet. Run the tracker to populate this page!</p></div>\n'
    html += '</div>\n'
    return html


def generate_source_view(listings_by_source):
    """Generate the source-grouped view container"""
    html = '<div id="source-view" class="view-container hidden">\n'
    if not listings_by_source:
        html += '<div class="no-listings"><p>No listings found yet. Run the tracker to populate this page!</p></div>\n'
    html += '</div>\n'
    return html


def generate_price_drops_view(all_listings):
    """Generate the price drops view container"""
    html = '<div id="drops-view" class="view-container hidden">\n'
    price_drops = [l for l in all_listings if l.get('price_dropped')]
    if not price_drops:
        html += '<div class="no-listings"><p>No price drops detected yet. Keep tracking to find deals!</p></div>\n'
    html += '</div>\n'
    return html