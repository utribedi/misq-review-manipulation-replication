# airbnb/ — Inside Airbnb detailed listings (listings.csv.gz), latest public snapshot per city (Sept 2026)

Source: https://insideairbnb.com/get-the-data/ (CC BY 4.0). Downloaded 2026-10-28 via Chrome; files gzip-verified.
Cities: Austin, Dallas, Fort Worth (Texas setup) and London, Paris, Amsterdam, Barcelona, Milan, Vienna (Booking.com 515K setup).

Key fields: id, host_id, latitude, longitude, room_type, price, first_review, number_of_reviews,
  hosts_time_as_host_years / hosts_time_as_host_months  <- replaces host_since (empty in these snapshots).
  Host start date ~= last_scraped - (years*12 + months) months. Used as the listing entry date, as Nie et al. used host registration date.
Caveats: earliest host start is Jan 2011 in every file (field appears capped); only listings still live in 2026 are observed (survivorship).

Files (gzip, read directly by pandas): austin_listings_2026-09-17, dallas_listings_2026-09-19, fort-worth_listings_2026-09-17 (Texas panel);
london_listings_2026-09-17, paris_listings_2026-09-16, amsterdam_listings_2026-09-16, barcelona_listings_2026-09-17, milan_listings_2026-09-19, vienna_listings_2026-09-17 (Europe panel).
Used by code/03_build_panel_eu.py, 04_build_panel_tx.py, 07-12 to count listings within 1 km of each hotel (and of each hotel's competitors, for the instrument), quarter by quarter from the reconstructed host start date.
Inside Airbnb only keeps the most recent snapshot online, so these September 2026 files are archived here for reproducibility.
