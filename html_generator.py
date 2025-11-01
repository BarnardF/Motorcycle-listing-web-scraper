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
        
        # Group by source for stats
        by_source = {}
        for listing in all_listings:
            source = listing['source']
            by_source.setdefault(source, []).append(listing)
        
        # Generate timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Build HTML
        html = f"""<!DOCTYPE HTML>
<html>
<head>
    <title>Motorcycle Listings Tracker</title>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1, user-scalable=no" />
    <style>
        @import url("https://fonts.googleapis.com/css?family=Roboto:100,300,100italic,300italic");

        * {{
            margin: 0;
            padding: 0;
            border: 0;
            font-size: 100%;
            font: inherit;
            vertical-align: baseline;
            box-sizing: border-box;
        }}

        html, body {{
            background: #1c1d26;
        }}

        body {{
            color: rgba(255, 255, 255, 0.75);
            font-family: "Roboto", Helvetica, sans-serif;
            font-size: 15pt;
            font-weight: 100;
            line-height: 1.75em;
        }}

        a {{
            transition: border-color 0.2s ease-in-out, color 0.2s ease-in-out;
            border-bottom: dotted 1px;
            color: #e44c65;
            text-decoration: none;
        }}

        a:hover {{
            color: #e44c65 !important;
            border-bottom-color: transparent;
        }}

        h1 {{
            color: #ffffff;
            font-weight: 300;
            font-size: 2.5em;
            line-height: 1.5em;
            letter-spacing: -0.025em;
            margin: 0 0 0.5em 0;
        }}

        h2 {{
            color: #ffffff;
            font-weight: 300;
            font-size: 2em;
            line-height: 1.5em;
            letter-spacing: -0.025em;
            margin: 0 0 1em 0;
        }}

        h3 {{
            color: #ffffff;
            font-weight: 300;
            font-size: 1.35em;
            line-height: 1.5em;
            margin: 0 0 1em 0;
        }}

        p {{
            margin: 0 0 2em 0;
        }}

        .container {{
            margin: 0 auto;
            max-width: calc(100% - 4em);
            width: 70em;
        }}

        .wrapper {{
            padding: 6em 0 4em 0;
        }}

        .wrapper.style1 {{
            background: #1c1d26;
        }}

        header.major {{
            margin: 0 0 4em 0;
            position: relative;
            text-align: center;
        }}

        header.major:after {{
            background: #e44c65;
            content: '';
            display: inline-block;
            height: 0.2em;
            max-width: 20em;
            width: 75%;
        }}

        header p {{
            color: rgba(255, 255, 255, 0.75);
            position: relative;
            margin: 0 0 1.5em 0;
        }}

        header h1 + p {{
            font-size: 1.25em;
            margin-top: -1em;
            line-height: 1.75em;
        }}

        .stats {{
            display: flex;
            justify-content: center;
            gap: 3em;
            margin: 2em 0 4em 0;
            flex-wrap: wrap;
        }}

        .stat-box {{
            background: rgba(255, 255, 255, 0.05);
            padding: 1.5em 2em;
            border-radius: 8px;
            text-align: center;
            min-width: 150px;
            border: 1px solid rgba(228, 76, 101, 0.2);
            transition: transform 0.3s ease, border-color 0.3s ease;
        }}

        .stat-box:hover {{
            transform: translateY(-5px);
            border-color: #e44c65;
        }}

        .stat-number {{
            font-size: 2.5em;
            font-weight: 300;
            color: #e44c65;
            display: block;
            margin-bottom: 0.2em;
        }}

        .stat-label {{
            font-size: 0.9em;
            color: rgba(255, 255, 255, 0.6);
            text-transform: uppercase;
            letter-spacing: 0.1em;
        }}

        .bike-section {{
            margin-bottom: 4em;
        }}

        .bike-header {{
            background: linear-gradient(135deg, rgba(228, 76, 101, 0.1), rgba(228, 76, 101, 0.05));
            padding: 1.5em 2em;
            border-left: 4px solid #e44c65;
            margin-bottom: 2em;
            border-radius: 4px;
        }}

        .bike-header h2 {{
            margin: 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .listing-count {{
            font-size: 0.6em;
            color: #e44c65;
            font-weight: 100;
        }}

        .listing-card {{
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            padding: 1.5em;
            margin-bottom: 1.5em;
            transition: transform 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease;
        }}

        .listing-card:hover {{
            transform: translateX(10px);
            border-color: #e44c65;
            box-shadow: 0 4px 20px rgba(228, 76, 101, 0.2);
        }}

        .listing-header {{
            display: flex;
            justify-content: space-between;
            align-items: start;
            margin-bottom: 1em;
            flex-wrap: wrap;
            gap: 1em;
        }}

        .listing-title {{
            color: #ffffff;
            font-size: 1.2em;
            font-weight: 300;
            margin: 0;
        }}

        .listing-price {{
            color: #e44c65;
            font-size: 1.3em;
            font-weight: 300;
            white-space: nowrap;
        }}

        .listing-meta {{
            display: flex;
            gap: 2em;
            flex-wrap: wrap;
            font-size: 0.9em;
            color: rgba(255, 255, 255, 0.5);
            margin-bottom: 1em;
        }}

        .meta-item {{
            display: flex;
            align-items: center;
            gap: 0.5em;
        }}

        .badge {{
            display: inline-block;
            padding: 0.3em 0.8em;
            background: rgba(228, 76, 101, 0.2);
            color: #e44c65;
            border-radius: 4px;
            font-size: 0.85em;
            font-weight: 300;
        }}

        .listing-link {{
            display: inline-block;
            padding: 0.7em 1.5em;
            background: rgba(228, 76, 101, 0.1);
            border: 1px solid #e44c65;
            border-radius: 4px;
            color: #e44c65;
            text-decoration: none;
            border-bottom: none;
            transition: background 0.3s ease, color 0.3s ease;
            font-size: 0.9em;
        }}

        .listing-link:hover {{
            background: #e44c65;
            color: #ffffff !important;
        }}

        .no-listings {{
            text-align: center;
            padding: 3em;
            color: rgba(255, 255, 255, 0.4);
            font-style: italic;
        }}

        .timestamp {{
            text-align: center;
            color: rgba(255, 255, 255, 0.4);
            font-size: 0.9em;
            margin-top: 4em;
            padding-top: 2em;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
        }}

        @media screen and (max-width: 980px) {{
            body {{
                font-size: 12pt;
            }}

            .stats {{
                gap: 1.5em;
            }}

            .listing-header {{
                flex-direction: column;
                align-items: start;
            }}

            .wrapper {{
                padding: 4.5em 2.5em 2.5em 2.5em;
            }}
        }}

        @media screen and (max-width: 736px) {{
            body {{
                font-size: 12pt;
            }}

            h1 {{
                font-size: 1.8em;
            }}

            h2 {{
                font-size: 1.5em;
            }}

            .stat-box {{
                min-width: 120px;
            }}

            .wrapper {{
                padding: 3.25em 1.5em 1.25em 1.5em;
            }}

            header.major {{
                margin: 0 0 2em 0;
            }}

            .listing-card {{
                padding: 1em;
            }}
        }}
    </style>
</head>
<body>
    <section class="wrapper style1">
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
                    <span class="stat-number">{len(by_source)}</span>
                    <span class="stat-label">Sources</span>
                </div>
            </div>
"""

        # Add each bike section
        if not all_listings:
            html += """
            <div class="no-listings">
                <p>No listings found yet. Run the tracker to populate this page!</p>
            </div>
"""
        else:
            for bike in bikes_tracked:
                listings = listings_by_bike.get(bike, [])
                if not listings:
                    continue
                
                html += f"""
            <!-- {bike} Section -->
            <div class="bike-section">
                <div class="bike-header">
                    <h2>
                        {bike}
                        <span class="listing-count">{len(listings)} listing(s)</span>
                    </h2>
                </div>
"""
                
                for listing in listings:
                    html += f"""
                <div class="listing-card">
                    <div class="listing-header">
                        <h3 class="listing-title">{listing['title']}</h3>
                        <div class="listing-price">{listing['price']}</div>
                    </div>
                    <div class="listing-meta">
                        <div class="meta-item">
                            <span class="badge">{listing['source']}</span>
                        </div>
                        <div class="meta-item">
                            📅 {listing['found_date'][:10]}
                        </div>
                    </div>
                    <a href="{listing['url']}" target="_blank" class="listing-link">View Listing →</a>
                </div>
"""
                
                html += """
            </div>
"""

        # Footer with timestamp
        html += f"""
            <div class="timestamp">
                Last updated: {timestamp}
            </div>
        </div>
    </section>
</body>
</html>
"""
        
        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        logger.info(f"✓ Generated HTML report: {output_file}")
        logger.info(f"  Total listings: {len(all_listings)}")
        logger.info(f"  Bikes with listings: {len(listings_by_bike)}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error generating HTML report: {e}")
        return False
