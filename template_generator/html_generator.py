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
    """Generate the complete HTML template with horizontal filters"""
    
    sources_count = len(listings_by_source)
    price_drops_count = sum(1 for listing in all_listings if listing.get('price_dropped'))
    
    # Convert listings to JSON for JavaScript
    listings_json = json.dumps(all_listings)
    
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

            <!-- Compact Stats Header -->
            <div class="compact-stats">
                <div class="compact-stat">
                    <span class="compact-stat-number" id="total-listings">{len(all_listings)}</span>
                    <span class="compact-stat-label">Listings</span>
                </div>
                <div class="compact-stat">
                    <span class="compact-stat-number">{len(bikes_tracked)}</span>
                    <span class="compact-stat-label">Bikes</span>
                </div>
                <div class="compact-stat">
                    <span class="compact-stat-number">{sources_count}</span>
                    <span class="compact-stat-label">Sources</span>
                </div>
                <div class="compact-stat">
                    <span class="compact-stat-number">{price_drops_count}</span>
                    <span class="compact-stat-label">Price Drops</span>
                </div>
            </div>

            <!-- Control Bar (View toggles + Filters) -->
            <div class="control-bar">
                <!-- Filter Buttons -->
                <div class="filter-controls">
                    <button class="filter-btn" onclick="toggleFilterPanel('sources')">Sources</button>
                    <button class="filter-btn" onclick="toggleFilterPanel('price')">Price Range</button>
                    <button class="filter-btn" onclick="toggleFilterPanel('km')">Kilometers</button>
                    <button class="filter-btn" onclick="toggleFilterPanel('sort')">Sort By</button>
                    <button class="filter-btn clear-all" onclick="clearAllFilters()">Reset</button>
                </div>

                <!-- Results Count -->
                <div class="results-display">
                    <span id="filtered-count">{len(all_listings)}</span> / {len(all_listings)}
                </div>
            </div>

            <!-- Collapsible Filter Panels -->
            <div class="filter-panels">
                <!-- Sources Filter -->
                <div class="filter-panel-item" id="sources-panel">
                    <div class="filter-panel-header">
                        <h4>Filter by Sources</h4>
                        <button class="filter-close-btn" onclick="toggleFilterPanel('sources')">✕</button>
                    </div>
                    <div class="filter-panel-content">
                        <div class="filter-checkboxes" id="source-filters">
"""
    
    # Add source checkboxes
    for source in all_sources:
        html += f"""
                            <label class="checkbox-label">
                                <input type="checkbox" class="source-checkbox" value="{source}" checked onchange="applyFilters()">
                                <span>{source}</span>
                            </label>
"""
    
    html += f"""
                        </div>
                    </div>
                </div>

                <!-- Price Range Filter -->
                <div class="filter-panel-item" id="price-panel">
                    <div class="filter-panel-header">
                        <h4>Price Range (R)</h4>
                        <button class="filter-close-btn" onclick="toggleFilterPanel('price')">✕</button>
                    </div>
                    <div class="filter-panel-content">
                        <div class="range-inputs">
                            <input type="number" id="price-min" class="range-input" placeholder="Min" value="0" onchange="applyFilters()">
                            <span class="range-dash">-</span>
                            <input type="number" id="price-max" class="range-input" placeholder="Max" value="999999" onchange="applyFilters()">
                        </div>
                        <input type="range" id="price-slider-min" class="slider" min="0" max="500000" value="0" oninput="updatePriceMin(this.value)">
                        <input type="range" id="price-slider-max" class="slider" min="0" max="500000" value="500000" oninput="updatePriceMax(this.value)">
                        <div class="slider-values">
                            <span>R<span id="price-display-min">0</span></span> - <span>R<span id="price-display-max">500000</span></span>
                        </div>
                    </div>
                </div>

                <!-- Kilometers Range Filter -->
                <div class="filter-panel-item" id="km-panel">
                    <div class="filter-panel-header">
                        <h4>Kilometers Range</h4>
                        <button class="filter-close-btn" onclick="toggleFilterPanel('km')">✕</button>
                    </div>
                    <div class="filter-panel-content">
                        <div class="range-inputs">
                            <input type="number" id="km-min" class="range-input" placeholder="Min" value="0" onchange="applyFilters()">
                            <span class="range-dash">-</span>
                            <input type="number" id="km-max" class="range-input" placeholder="Max" value="999999" onchange="applyFilters()">
                        </div>
                        <input type="range" id="km-slider-min" class="slider" min="0" max="500000" value="0" oninput="updateKmMin(this.value)">
                        <input type="range" id="km-slider-max" class="slider" min="0" max="500000" value="500000" oninput="updateKmMax(this.value)">
                        <div class="slider-values">
                            <span><span id="km-display-min">0</span> km</span> - <span><span id="km-display-max">500000</span> km</span>
                        </div>
                    </div>
                </div>

                <!-- Sort & Views Filter -->
                <div class="filter-panel-item" id="sort-panel">
                    <div class="filter-panel-header">
                        <h4>Sort By & Views</h4>
                        <button class="filter-close-btn" onclick="toggleFilterPanel('sort')">✕</button>
                    </div>
                    <div class="filter-panel-content">
                        <label class="filter-label-small">Sort By</label>
                        <select id="sort-select" class="filter-select" onchange="applyFilters()">
                            <option value="none">Default</option>
                            <option value="price-asc">Price: Low to High</option>
                            <option value="price-desc">Price: High to Low</option>
                            <option value="km-asc">Kilometers: Low to High</option>
                            <option value="km-desc">Kilometers: High to Low</option>
                            <option value="newest">Newest Listings First</option>
                        </select>
                        
                        <label class="filter-label-small" style="margin-top: 1.2em;">View By</label>
                        <div class="filter-checkboxes">
                            <label class="checkbox-label">
                                <input type="radio" name="view-type" value="bike" checked onchange="showView('bike')">
                                <span>By Bike Model</span>
                            </label>
                            <label class="checkbox-label">
                                <input type="radio" name="view-type" value="source" onchange="showView('source')">
                                <span>By Source</span>
                            </label>
                            <label class="checkbox-label">
                                <input type="radio" name="view-type" value="drops" onchange="showView('drops')">
                                <span>Price Drops Only</span>
                            </label>
                        </div>
                    </div>
                </div>

            <!-- Listings Area -->
            <div class="listings-area">
"""

    # Generate views
    html += generate_bike_view(listings_by_bike)
    html += generate_source_view(listings_by_source)
    html += generate_price_drops_view(all_listings)

    # Close listings area
    html += """
            </div>

            <div class="timestamp">
                Last updated: """ + timestamp + """
            </div>
        </div>
    </section>

    <script>
        // Store all listings
        const allListings = """ + listings_json + """;
        let filteredListings = [...allListings];

        // Initialize on page load
        document.addEventListener('DOMContentLoaded', function() {
            applyFilters();
        });

        function showView(viewType) {
            document.querySelectorAll('.view-container').forEach(el => el.classList.add('hidden'));
            document.getElementById(viewType + '-view').classList.remove('hidden');
            document.querySelector(`input[name="view-type"][value="${viewType}"]`).checked = true;
            applyFilters();
        }

        function toggleFilterPanel(panelType) {
            const panelId = panelType + '-panel';
            const panel = document.getElementById(panelId);
            const isOpen = panel.classList.contains('open');
            
            // Close all panels
            document.querySelectorAll('.filter-panel-item').forEach(p => p.classList.remove('open'));
            
            // Open clicked panel if it was closed
            if (!isOpen) {
                panel.classList.add('open');
            }
        }

        function updatePriceMin(value) {
            document.getElementById('price-min').value = value;
            document.getElementById('price-display-min').textContent = parseInt(value).toLocaleString();
            applyFilters();
        }

        function updatePriceMax(value) {
            document.getElementById('price-max').value = value;
            document.getElementById('price-display-max').textContent = parseInt(value).toLocaleString();
            applyFilters();
        }

        function updateKmMin(value) {
            document.getElementById('km-min').value = value;
            document.getElementById('km-display-min').textContent = parseInt(value).toLocaleString();
            applyFilters();
        }

        function updateKmMax(value) {
            document.getElementById('km-max').value = value;
            document.getElementById('km-display-max').textContent = parseInt(value).toLocaleString();
            applyFilters();
        }

        function applyFilters() {
            // Get filter values
            const selectedSources = Array.from(document.querySelectorAll('.source-checkbox:checked')).map(cb => cb.value);
            const priceMin = parseInt(document.getElementById('price-min').value) || 0;
            const priceMax = parseInt(document.getElementById('price-max').value) || 999999;
            const kmMin = parseInt(document.getElementById('km-min').value) || 0;
            const kmMax = parseInt(document.getElementById('km-max').value) || 999999;
            const sortBy = document.getElementById('sort-select').value;

            // Filter listings
            filteredListings = allListings.filter(listing => {
                // Check source
                if (!selectedSources.includes(listing.source)) return false;

                // Parse price (remove R and spaces)
                const priceStr = listing.price.replace(/[R\\s,]/g, '');
                const price = parseInt(priceStr) || 0;
                if (price < priceMin || price > priceMax) return false;

                // Parse kilometers
                let km = 0;
                const kmStr = listing.kilometers.replace(/[km\\s,]/g, '');
                if (kmStr && !isNaN(kmStr)) {
                    km = parseInt(kmStr);
                }
                if (km < kmMin || km > kmMax) return false;

                return true;
            });

            // Sort listings
            if (sortBy === 'price-asc') {
                filteredListings.sort((a, b) => {
                    const priceA = parseInt(a.price.replace(/[R\\s,]/g, '')) || 0;
                    const priceB = parseInt(b.price.replace(/[R\\s,]/g, '')) || 0;
                    return priceA - priceB;
                });
            } else if (sortBy === 'price-desc') {
                filteredListings.sort((a, b) => {
                    const priceA = parseInt(a.price.replace(/[R\\s,]/g, '')) || 0;
                    const priceB = parseInt(b.price.replace(/[R\\s,]/g, '')) || 0;
                    return priceB - priceA;
                });
            } else if (sortBy === 'km-asc') {
                filteredListings.sort((a, b) => {
                    const kmA = parseInt(a.kilometers.replace(/[km\\s,]/g, '')) || 0;
                    const kmB = parseInt(b.kilometers.replace(/[km\\s,]/g, '')) || 0;
                    return kmA - kmB;
                });
            } else if (sortBy === 'km-desc') {
                filteredListings.sort((a, b) => {
                    const kmA = parseInt(a.kilometers.replace(/[km\\s,]/g, '')) || 0;
                    const kmB = parseInt(b.kilometers.replace(/[km\\s,]/g, '')) || 0;
                    return kmB - kmA;
                });
            }

            // Update display
            updateTableDisplay();
            document.getElementById('filtered-count').textContent = filteredListings.length;
        }

        function clearAllFilters() {
            // Reset checkboxes
            document.querySelectorAll('.source-checkbox').forEach(cb => cb.checked = true);
            
            // Reset price range
            document.getElementById('price-min').value = 0;
            document.getElementById('price-max').value = 500000;
            document.getElementById('price-slider-min').value = 0;
            document.getElementById('price-slider-max').value = 500000;
            document.getElementById('price-display-min').textContent = '0';
            document.getElementById('price-display-max').textContent = '500000';
            
            // Reset km range
            document.getElementById('km-min').value = 0;
            document.getElementById('km-max').value = 500000;
            document.getElementById('km-slider-min').value = 0;
            document.getElementById('km-slider-max').value = 500000;
            document.getElementById('km-display-min').textContent = '0';
            document.getElementById('km-display-max').textContent = '500000';
            
            // Reset sort
            document.getElementById('sort-select').value = 'none';
            
            // Close all filter panels
            document.querySelectorAll('.filter-panel-item').forEach(p => p.classList.remove('open'));
            
            applyFilters();
        }

        function updateTableDisplay() {
            // Get active view
            const activeView = document.querySelector('.view-container:not(.hidden)');
            const viewType = activeView?.id.replace('-view', '') || 'bike';

            if (viewType === 'bike') {
                updateBikeView();
            } else if (viewType === 'source') {
                updateSourceView();
            } else if (viewType === 'drops') {
                updateDropsView();
            }
        }

        function updateBikeView() {
            const container = document.getElementById('bike-view');
            
            // Group filtered listings by bike
            const byBike = {};
            filteredListings.forEach(listing => {
                const bike = listing.search_term;
                if (!byBike[bike]) byBike[bike] = [];
                byBike[bike].push(listing);
            });

            container.innerHTML = '';
            if (Object.keys(byBike).length === 0) {
                container.innerHTML = '<div class="no-listings"><p>No listings match your filters.</p></div>';
                return;
            }

            for (const [bike, listings] of Object.entries(byBike)) {
                container.innerHTML += generateTableSection(bike, listings, 'bike');
            }
        }

        function updateSourceView() {
            const container = document.getElementById('source-view');
            
            // Group filtered listings by source
            const bySource = {};
            filteredListings.forEach(listing => {
                const source = listing.source;
                if (!bySource[source]) bySource[source] = [];
                bySource[source].push(listing);
            });

            container.innerHTML = '';
            if (Object.keys(bySource).length === 0) {
                container.innerHTML = '<div class="no-listings"><p>No listings match your filters.</p></div>';
                return;
            }

            for (const [source, listings] of Object.entries(bySource)) {
                container.innerHTML += generateTableSection(source, listings, 'source');
            }
        }

        function updateDropsView() {
            const container = document.getElementById('drops-view');
            const drops = filteredListings.filter(l => l.price_dropped);

            container.innerHTML = '';
            if (drops.length === 0) {
                container.innerHTML = '<div class="no-listings"><p>No price drops match your filters.</p></div>';
                return;
            }

            container.innerHTML += generateDropsTable(drops);
        }

        function generateTableSection(title, listings, type) {
            let html = `
                <div class="table-section">
                    <div class="table-header">
                        <h2>${title}</h2>
                        <span class="listing-count">${listings.length} listing(s)</span>
                    </div>
                    <table>
                        <thead>
                            <tr>
                                <th>${type === 'bike' ? 'Source' : 'Bike Model'}</th>
                                <th>Title</th>
                                <th>Price</th>
                                <th>Kilometers</th>
                                <th>Location</th>
                                <th>Link</th>
                            </tr>
                        </thead>
                        <tbody>
            `;

            listings.forEach(listing => {
                const priceDisplay = listing.price_dropped && listing.old_price
                    ? `<span class='old-price'>${listing.old_price}</span> ${listing.price}`
                    : listing.price;

                html += `
                    <tr class="${listing.price_dropped ? 'price-drop-row' : ''}">
                        <td class="bike-name">${type === 'bike' ? listing.source : listing.search_term}</td>
                        <td class="bike-name">${listing.title}</td>
                        <td class="price">${priceDisplay}</td>
                        <td class="kilometers">${listing.kilometers}</td>
                        <td class="location">${listing.location}</td>
                        <td><a href="${listing.url}" target="_blank" class="view-link">View →</a></td>
                    </tr>
                `;
            });

            html += `
                        </tbody>
                    </table>
                </div>
            `;
            return html;
        }

        function generateDropsTable(listings) {
            let html = `
                <div class="table-section">
                    <div class="table-header">
                        <h2>Price Drops Detected</h2>
                        <span class="listing-count">${listings.length} listing(s) with price drops</span>
                    </div>
                    <table>
                        <thead>
                            <tr>
                                <th>Bike Model</th>
                                <th>Title</th>
                                <th>Price</th>
                                <th>Kilometers</th>
                                <th>Location</th>
                                <th>Source</th>
                                <th>Link</th>
                            </tr>
                        </thead>
                        <tbody>
            `;

            listings.forEach(listing => {
                const priceDisplay = listing.old_price
                    ? `<span class='old-price'>${listing.old_price}</span> ${listing.price}`
                    : listing.price;

                html += `
                    <tr class="price-drop-row">
                        <td class="bike-name">${listing.search_term}</td>
                        <td class="bike-name">${listing.title}</td>
                        <td class="price">${priceDisplay}</td>
                        <td class="kilometers">${listing.kilometers}</td>
                        <td class="location">${listing.location}</td>
                        <td class="source">${listing.source}</td>
                        <td><a href="${listing.url}" target="_blank" class="view-link">View →</a></td>
                    </tr>
                `;
            });

            html += `
                        </tbody>
                    </table>
                </div>
            `;
            return html;
        }
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