#!/usr/bin/env python3
"""Generate a PNG world map of all data centers for the README."""

import csv
import hashlib
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np

REPO_ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = REPO_ROOT / "data" / "datacenters.csv"
PNG_PATH = REPO_ROOT / "assets" / "map.png"

COUNTRY_CENTROIDS = {
    "Afghanistan": (33.9, 67.7), "Albania": (41.2, 20.2), "Algeria": (28.0, 1.7),
    "Andorra": (42.5, 1.5), "Angola": (-11.2, 17.9), "Argentina": (-38.4, -63.6),
    "Armenia": (40.1, 45.0), "Australia": (-25.3, 133.8), "Austria": (47.5, 14.6),
    "Azerbaijan": (40.1, 47.6), "Bahamas": (25.0, -77.4), "Bahrain": (26.0, 50.6),
    "Bangladesh": (23.7, 90.4), "Barbados": (13.2, -59.5), "Belarus": (53.7, 27.9),
    "Belgium": (50.8, 4.5), "Belize": (17.2, -88.5), "Benin": (9.3, 2.3),
    "Bhutan": (27.5, 90.4), "Bolivia": (-16.3, -63.6), "Bosnia and Herzegovina": (43.9, 17.7),
    "Botswana": (-22.3, 24.7), "Brazil": (-14.2, -51.9), "Brunei": (4.5, 114.7),
    "Bulgaria": (42.7, 25.5), "Burkina Faso": (12.2, -1.6), "Burundi": (-3.4, 29.9),
    "Cambodia": (12.6, 105.0), "Cameroon": (7.4, 12.4), "Canada": (56.1, -106.3),
    "Cape Verde": (16.0, -24.0), "Central African Republic": (6.6, 20.9),
    "Chad": (15.5, 18.7), "Chile": (-35.7, -71.5), "China": (35.9, 104.2),
    "Colombia": (4.6, -74.3), "Comoros": (-11.6, 43.3), "Congo": (-0.2, 15.8),
    "Costa Rica": (9.7, -83.8), "Croatia": (45.1, 15.2),
    "Cuba": (21.5, -77.8), "Curacao": (12.2, -68.98), "Cyprus": (35.1, 33.4),
    "Czech Republic": (49.8, 15.5), "Czechia": (49.8, 15.5),
    "Democratic Republic of the Congo": (-4.0, 21.8),
    "Denmark": (56.3, 9.5), "Djibouti": (11.8, 42.6),
    "Dominican Republic": (18.7, -70.2), "Ecuador": (-1.8, -78.2),
    "Egypt": (26.8, 30.8), "El Salvador": (13.8, -88.9),
    "Equatorial Guinea": (1.7, 10.3), "Eritrea": (15.2, 39.8),
    "Estonia": (58.6, 25.0), "Eswatini": (-26.5, 31.5),
    "Ethiopia": (9.1, 40.5), "Fiji": (-17.7, 178.1),
    "Finland": (61.9, 25.7), "France": (46.2, 2.2),
    "Gabon": (-0.8, 11.6), "Gambia": (13.4, -16.6), "Georgia": (42.3, 43.4),
    "Germany": (51.2, 10.5), "Ghana": (7.9, -1.0), "Greece": (39.1, 21.8),
    "Grenada": (12.3, -61.6), "Guatemala": (15.8, -90.2),
    "Guinea": (9.9, -9.7), "Guinea-Bissau": (12.0, -15.2),
    "Guyana": (5.0, -58.9), "Haiti": (19.1, -72.3),
    "Honduras": (15.2, -86.2), "Hong Kong": (22.4, 114.1),
    "Hungary": (47.2, 19.5), "Iceland": (64.9, -19.0),
    "India": (20.6, 78.9), "Indonesia": (-0.8, 113.9),
    "Iran": (32.4, 53.7), "Iraq": (33.2, 43.7),
    "Ireland": (53.1, -8.2), "Isle of Man": (54.2, -4.5),
    "Israel": (31.0, 34.9), "Italy": (41.9, 12.6),
    "Ivory Coast": (7.5, -5.5), "Jamaica": (18.1, -77.3),
    "Japan": (36.2, 138.3), "Jersey": (49.2, -2.1),
    "Jordan": (30.6, 36.2), "Kazakhstan": (48.0, 68.0),
    "Kenya": (-0.0, 37.9), "Kosovo": (42.6, 20.9),
    "Kuwait": (29.3, 47.5), "Kyrgyzstan": (41.2, 74.8),
    "Laos": (19.9, 102.5), "Latvia": (56.9, 24.1),
    "Lebanon": (33.9, 35.9), "Lesotho": (-29.6, 28.2),
    "Liberia": (6.4, -9.4), "Libya": (26.3, 17.2),
    "Liechtenstein": (47.2, 9.6), "Lithuania": (55.2, 23.9),
    "Luxembourg": (49.8, 6.1), "Macao": (22.2, 113.5), "Macau": (22.2, 113.5),
    "Madagascar": (-18.8, 46.9), "Malawi": (-13.3, 34.3),
    "Malaysia": (4.2, 101.9), "Maldives": (3.2, 73.2),
    "Mali": (17.6, -4.0), "Malta": (35.9, 14.4),
    "Mauritania": (21.0, -11.0), "Mauritius": (-20.3, 57.6),
    "Mexico": (23.6, -102.6), "Moldova": (47.4, 28.4),
    "Monaco": (43.7, 7.4), "Mongolia": (46.9, 103.8),
    "Montenegro": (42.7, 19.4), "Morocco": (31.8, -7.1),
    "Mozambique": (-18.7, 35.5), "Myanmar": (21.9, 96.0),
    "Namibia": (-22.6, 17.1), "Nepal": (28.4, 84.1),
    "Netherlands": (52.1, 5.3), "New Caledonia": (-20.9, 165.6),
    "New Zealand": (-40.9, 174.9), "Nicaragua": (12.9, -85.2),
    "Niger": (17.6, 8.1), "Nigeria": (9.1, 8.7),
    "North Korea": (40.3, 127.5), "North Macedonia": (41.5, 21.7),
    "Norway": (60.5, 8.5), "Oman": (21.5, 55.9),
    "Pakistan": (30.4, 69.3), "Palestine": (31.9, 35.2),
    "Panama": (8.5, -80.8), "Papua New Guinea": (-6.3, 143.9),
    "Paraguay": (-23.4, -58.4), "Peru": (-9.2, -75.0),
    "Philippines": (12.9, 121.8), "Poland": (51.9, 19.1),
    "Portugal": (39.4, -8.2), "Puerto Rico": (18.2, -66.6),
    "Qatar": (25.4, 51.2), "Romania": (45.9, 25.0),
    "Russia": (61.5, 105.3), "Russian Federation": (61.5, 105.3),
    "Rwanda": (-1.9, 29.9), "Saudi Arabia": (23.9, 45.1),
    "Senegal": (14.5, -14.5), "Serbia": (44.0, 21.0),
    "Seychelles": (-4.7, 55.5), "Sierra Leone": (8.5, -11.8),
    "Singapore": (1.4, 103.8), "Slovakia": (48.7, 19.7),
    "Slovenia": (46.2, 14.9), "Solomon Islands": (-9.6, 160.2),
    "Somalia": (5.2, 46.2), "South Africa": (-30.6, 22.9),
    "South Korea": (35.9, 127.8), "South Sudan": (6.9, 31.3),
    "Spain": (40.5, -3.7), "Sri Lanka": (7.9, 80.8),
    "Sudan": (12.9, 30.2), "Suriname": (3.9, -56.0),
    "Sweden": (60.1, 18.6), "Switzerland": (46.8, 8.2),
    "Syria": (34.8, 39.0), "Taiwan": (23.7, 121.0),
    "Tajikistan": (38.9, 71.3), "Tanzania": (-6.4, 34.9),
    "Thailand": (15.9, 100.9), "Togo": (8.6, 1.2),
    "Trinidad and Tobago": (10.7, -61.2), "Tunisia": (34.0, 9.5),
    "Turkey": (38.9, 35.2), "Turkmenistan": (39.0, 59.6),
    "Uganda": (1.4, 32.3), "Ukraine": (48.4, 31.2),
    "United Arab Emirates": (23.4, 53.8), "United Kingdom": (55.4, -3.4),
    "United States": (37.1, -95.7), "Uruguay": (-32.5, -55.8),
    "Uzbekistan": (41.4, 64.6), "Venezuela": (6.4, -66.6),
    "Vietnam": (14.1, 108.3), "Yemen": (15.6, 48.5),
    "Zambia": (-13.1, 28.0), "Zimbabwe": (-19.0, 29.2),
    "Reunion": (-21.1, 55.5), "Guadeloupe": (16.3, -61.6),
    "Martinique": (14.6, -61.0), "French Guiana": (3.9, -53.1),
    "Mayotte": (-12.8, 45.2), "French Polynesia": (-17.7, -149.4),
    "Guam": (13.4, 144.8), "U.S. Virgin Islands": (18.3, -64.9),
    "American Samoa": (-14.3, -170.1), "Bermuda": (32.3, -64.8),
    "Cayman Islands": (19.5, -80.6), "Gibraltar": (36.1, -5.4),
    "Greenland": (71.7, -42.6), "Faroe Islands": (62.0, -7.0),
    "Aruba": (12.5, -70.0), "Sint Maarten": (18.0, -63.1),
    "Saint Martin": (18.1, -63.1), "British Virgin Islands": (18.4, -64.6),
    "Turks and Caicos Islands": (21.7, -71.8),
    "Saint Kitts and Nevis": (17.4, -62.7),
    "Saint Lucia": (13.9, -61.0), "Saint Vincent and the Grenadines": (13.3, -61.2),
    "Antigua and Barbuda": (17.1, -61.8), "Dominica": (15.4, -61.4),
    "Samoa": (-13.8, -172.1), "Tonga": (-21.2, -175.2),
    "Cook Islands": (-21.2, -159.8), "Niue": (-19.1, -169.9),
    "Marshall Islands": (7.1, 171.2), "Micronesia": (7.4, 150.6),
    "Palau": (7.5, 134.6), "Nauru": (-0.5, 166.9),
    "Kiribati": (1.9, -157.4), "Tuvalu": (-7.1, 177.6),
    "Vanuatu": (-15.4, 166.9), "Timor-Leste": (-8.9, 125.7),
}

US_STATE_CENTROIDS = {
    "AL": (32.8, -86.8), "AK": (64.2, -152.5), "AZ": (34.0, -111.1),
    "AR": (34.8, -92.2), "CA": (36.8, -119.4), "CO": (39.1, -105.4),
    "CT": (41.6, -72.7), "DE": (39.0, -75.5), "FL": (27.8, -81.7),
    "GA": (32.2, -83.6), "HI": (19.9, -155.6), "ID": (44.1, -114.7),
    "IL": (40.3, -89.0), "IN": (40.3, -86.1), "IA": (42.0, -93.2),
    "KS": (38.5, -98.8), "KY": (37.8, -84.3), "LA": (30.5, -91.2),
    "ME": (45.3, -69.4), "MD": (39.0, -76.6), "MA": (42.4, -71.4),
    "MI": (44.3, -84.5), "MN": (46.7, -94.7), "MS": (32.3, -89.4),
    "MO": (38.6, -92.6), "MT": (46.8, -110.4), "NE": (41.1, -98.3),
    "NV": (38.8, -116.4), "NH": (43.2, -71.6), "NJ": (40.1, -74.4),
    "NM": (34.5, -105.7), "NY": (43.0, -75.5), "NC": (35.6, -79.0),
    "ND": (47.5, -100.5), "OH": (40.4, -82.9), "OK": (35.0, -97.1),
    "OR": (43.8, -120.6), "PA": (41.2, -77.2), "RI": (41.6, -71.5),
    "SC": (33.8, -81.2), "SD": (43.9, -99.9), "TN": (35.5, -86.6),
    "TX": (31.0, -97.6), "UT": (39.3, -111.1), "VT": (44.6, -72.6),
    "VA": (37.8, -78.2), "WA": (47.8, -120.7), "WV": (38.6, -80.6),
    "WI": (43.8, -88.8), "WY": (43.1, -107.6), "DC": (38.9, -77.0),
    "PR": (18.2, -66.6),
    # Full names
    "Alabama": (32.8, -86.8), "Alaska": (64.2, -152.5), "Arizona": (34.0, -111.1),
    "Arkansas": (34.8, -92.2), "California": (36.8, -119.4), "Colorado": (39.1, -105.4),
    "Connecticut": (41.6, -72.7), "Delaware": (39.0, -75.5), "Florida": (27.8, -81.7),
    "Georgia": (32.2, -83.6), "Hawaii": (19.9, -155.6), "Idaho": (44.1, -114.7),
    "Illinois": (40.3, -89.0), "Indiana": (40.3, -86.1), "Iowa": (42.0, -93.2),
    "Kansas": (38.5, -98.8), "Kentucky": (37.8, -84.3), "Louisiana": (30.5, -91.2),
    "Maine": (45.3, -69.4), "Maryland": (39.0, -76.6), "Massachusetts": (42.4, -71.4),
    "Michigan": (44.3, -84.5), "Minnesota": (46.7, -94.7), "Mississippi": (32.3, -89.4),
    "Missouri": (38.6, -92.6), "Montana": (46.8, -110.4), "Nebraska": (41.1, -98.3),
    "Nevada": (38.8, -116.4), "New Hampshire": (43.2, -71.6), "New Jersey": (40.1, -74.4),
    "New Mexico": (34.5, -105.7), "New York": (43.0, -75.5), "North Carolina": (35.6, -79.0),
    "North Dakota": (47.5, -100.5), "Ohio": (40.4, -82.9), "Oklahoma": (35.0, -97.1),
    "Oregon": (43.8, -120.6), "Pennsylvania": (41.2, -77.2), "Rhode Island": (41.6, -71.5),
    "South Carolina": (33.8, -81.2), "South Dakota": (43.9, -99.9), "Tennessee": (35.5, -86.6),
    "Texas": (31.0, -97.6), "Utah": (39.3, -111.1), "Vermont": (44.6, -72.6),
    "Virginia": (37.8, -78.2), "Washington": (47.8, -120.7), "West Virginia": (38.6, -80.6),
    "Wisconsin": (43.8, -88.8), "Wyoming": (43.1, -107.6),
    "District of Columbia": (38.9, -77.0), "Puerto Rico": (18.2, -66.6),
}

MAJOR_CITIES = {
    "Montreal": (45.5, -73.6), "Montréal": (45.5, -73.6), "Toronto": (43.7, -79.4),
    "Vancouver": (49.3, -123.1), "Calgary": (51.0, -114.1), "Edmonton": (53.5, -113.5),
    "Ottawa": (45.4, -75.7), "Markham": (43.9, -79.3), "Mississauga": (43.6, -79.7),
    "Beauharnois": (45.3, -73.9), "Woodbridge": (43.8, -79.5), "Hamilton": (43.3, -79.9),
    "Quebec City": (46.8, -71.2), "Winnipeg": (49.9, -97.1), "Halifax": (44.6, -63.6),
    "London": (51.5, -0.1), "Manchester": (53.5, -2.2), "Edinburgh": (55.95, -3.2),
    "Birmingham": (52.5, -1.9), "Leeds": (53.8, -1.5), "Bristol": (51.5, -2.6),
    "Glasgow": (55.9, -4.3), "Slough": (51.5, -0.6), "Reading": (51.5, -1.0),
    "Frankfurt": (50.1, 8.7), "Berlin": (52.5, 13.4), "Munich": (48.1, 11.6),
    "Hamburg": (53.6, 10.0), "Düsseldorf": (51.2, 6.8), "Cologne": (50.9, 6.96),
    "Stuttgart": (48.8, 9.2), "Nuremberg": (49.5, 11.1),
    "Paris": (48.9, 2.3), "Marseille": (43.3, 5.4), "Lyon": (45.8, 4.8),
    "Strasbourg": (48.6, 7.8), "Lille": (50.6, 3.1),
    "Amsterdam": (52.4, 4.9), "Rotterdam": (51.9, 4.5), "The Hague": (52.1, 4.3),
    "Tokyo": (35.7, 139.7), "Osaka": (34.7, 135.5), "Nagoya": (35.2, 137.0),
    "Fukuoka": (33.6, 130.4),
    "Sydney": (33.9, 151.2), "Melbourne": (-37.8, 145.0), "Brisbane": (-27.5, 153.0),
    "Perth": (-31.9, 115.9), "Adelaide": (-34.9, 138.6), "Canberra": (-35.3, 149.1),
    "Mumbai": (19.1, 72.9), "Delhi": (28.7, 77.1), "New Delhi": (28.6, 77.2),
    "Bangalore": (13.0, 77.6), "Bengaluru": (13.0, 77.6), "Chennai": (13.1, 80.3),
    "Hyderabad": (17.4, 78.5), "Pune": (18.5, 73.9), "Kolkata": (22.6, 88.4),
    "Noida": (28.6, 77.3),
    "Beijing": (39.9, 116.4), "Shanghai": (31.2, 121.5), "Shenzhen": (22.5, 114.1),
    "Guangzhou": (23.1, 113.3), "Hangzhou": (30.3, 120.2), "Chengdu": (30.6, 104.1),
    "Nanjing": (32.1, 118.8), "Wuhan": (30.6, 114.3), "Xi'an": (34.3, 108.9),
    "São Paulo": (23.6, -46.6), "Sao Paulo": (-23.6, -46.6),
    "Rio de Janeiro": (-22.9, -43.2), "Brasília": (-15.8, -47.9),
    "Curitiba": (-25.4, -49.3), "Porto Alegre": (-30.0, -51.2),
    "Singapore": (1.4, 103.8), "Hong Kong": (22.4, 114.1),
    "Seoul": (37.6, 127.0), "Busan": (35.2, 129.1),
    "Jakarta": (-6.2, 106.8), "Surabaya": (-7.3, 112.7),
    "Kuala Lumpur": (3.1, 101.7), "Cyberjaya": (2.9, 101.7),
    "Bangkok": (13.8, 100.5), "Ho Chi Minh City": (10.8, 106.6), "Hanoi": (21.0, 105.9),
    "Manila": (14.6, 121.0), "Quezon City": (14.6, 121.0),
    "Dubai": (25.2, 55.3), "Abu Dhabi": (24.5, 54.7),
    "Riyadh": (24.7, 46.7), "Jeddah": (21.5, 39.2),
    "Johannesburg": (-26.2, 28.0), "Cape Town": (-33.9, 18.4),
    "Nairobi": (-1.3, 36.8), "Lagos": (6.5, 3.4),
    "Cairo": (30.0, 31.2), "Casablanca": (33.6, -7.6),
    "Moscow": (55.8, 37.6), "Saint Petersburg": (59.9, 30.3),
    "Warsaw": (52.2, 21.0), "Kraków": (50.1, 19.9),
    "Zurich": (47.4, 8.5), "Geneva": (46.2, 6.1),
    "Vienna": (48.2, 16.4), "Prague": (50.1, 14.4),
    "Dublin": (53.3, -6.3), "Stockholm": (59.3, 18.1),
    "Copenhagen": (55.7, 12.6), "Helsinki": (60.2, 24.9),
    "Oslo": (59.9, 10.8), "Lisbon": (38.7, -9.1),
    "Madrid": (40.4, -3.7), "Barcelona": (41.4, 2.2),
    "Milan": (45.5, 9.2), "Rome": (41.9, 12.5),
    "Istanbul": (41.0, 29.0), "Ankara": (39.9, 32.9),
    "Tel Aviv": (32.1, 34.8), "Amman": (31.9, 35.9),
    "Mexico City": (19.4, -99.1), "Guadalajara": (20.7, -103.3),
    "Querétaro": (20.6, -100.4), "Queretaro": (20.6, -100.4),
    "Santiago": (-33.4, -70.6), "Buenos Aires": (-34.6, -58.4),
    "Bogotá": (4.7, -74.1), "Bogota": (4.7, -74.1),
    "Lima": (-12.0, -77.0), "Quito": (-0.2, -78.5),
    "Auckland": (-36.8, 174.8), "Wellington": (-41.3, 174.8),
    "Taipei": (25.0, 121.5),
}

COUNTRY_JITTER_SCALE = {
    "Canada": 8.0, "Russia": 12.0, "Russian Federation": 12.0,
    "China": 6.0, "Brazil": 7.0, "Australia": 7.0, "India": 5.0,
    "Indonesia": 6.0, "Argentina": 6.0, "Kazakhstan": 7.0,
    "Algeria": 5.0, "Mexico": 5.0, "Saudi Arabia": 5.0,
    "Mongolia": 5.0, "Peru": 5.0, "Colombia": 4.0,
    "Chile": 3.0, "South Africa": 4.0, "Iran": 4.0,
    "Turkey": 4.0, "France": 3.5, "Spain": 3.5,
    "Germany": 2.5, "United Kingdom": 3.0, "Japan": 3.0,
    "Sweden": 4.0, "Norway": 4.0, "Finland": 3.5,
    "Poland": 2.5, "Italy": 3.0, "Ukraine": 3.0,
    "Malaysia": 3.5, "Thailand": 3.0, "Vietnam": 3.5,
    "Philippines": 3.0, "Pakistan": 3.5, "Nigeria": 3.5,
    "Egypt": 3.5, "South Korea": 2.0,
    "Netherlands": 1.5, "Belgium": 1.5, "Switzerland": 1.5,
    "Austria": 2.0, "Ireland": 2.0, "Denmark": 1.5,
    "New Zealand": 3.0, "Singapore": 0.5, "Hong Kong": 0.5,
}


def jitter(lat, lon, name, scale=2.5):
    h = int(hashlib.md5(name.encode()).hexdigest()[:8], 16)
    angle = (h % 10000) / 10000 * 2 * 3.14159
    r = ((h >> 16) % 10000) / 10000
    r = r ** 0.5 * scale
    cos_lat = max(np.cos(np.radians(lat)), 0.5)
    return lat + r * np.sin(angle), lon + r * np.cos(angle) * min(1.0 / cos_lat, 1.5)


def load_data():
    lats_base, lons_base = [], []
    lats_power, lons_power = [], []
    skipped = 0

    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            lat = row.get("latitude", "").strip()
            lon = row.get("longitude", "").strip()
            country = row.get("country", "").strip()
            name = row.get("name", "").strip()
            power = row.get("power_capacity_mw", "").strip()
            has_power = bool(power and power != "0")

            if lat and lon:
                try:
                    lat, lon = float(lat), float(lon)
                except ValueError:
                    lat, lon = None, None
            else:
                lat, lon = None, None

            if lat is None:
                city = row.get("city", "").strip()
                state = row.get("state_province", "").strip()
                if city in MAJOR_CITIES:
                    clat, clon = MAJOR_CITIES[city]
                    lat, lon = jitter(clat, clon, name, scale=0.8)
                elif country == "United States" and state in US_STATE_CENTROIDS:
                    clat, clon = US_STATE_CENTROIDS[state]
                    lat, lon = jitter(clat, clon, name, scale=1.5)
                elif country in COUNTRY_CENTROIDS:
                    clat, clon = COUNTRY_CENTROIDS[country]
                    n_scale = COUNTRY_JITTER_SCALE.get(country, 3.0)
                    lat, lon = jitter(clat, clon, name, scale=n_scale)
            elif lat is None:
                skipped += 1
                continue

            if has_power:
                lats_power.append(lat)
                lons_power.append(lon)
            else:
                lats_base.append(lat)
                lons_base.append(lon)

    print(f"  Base dots: {len(lats_base)}, Power dots: {len(lats_power)}, Skipped: {skipped}")
    return lats_base, lons_base, lats_power, lons_power


def load_coastlines():
    """Load Natural Earth 110m coastlines via geopandas."""
    import geopandas as gpd
    try:
        world = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))
        return world
    except Exception:
        url = "https://naciscdn.org/naturalearth/110m/cultural/ne_110m_admin_0_countries.zip"
        world = gpd.read_file(url)
        return world


def generate():
    print("Generating map...")
    lats_b, lons_b, lats_p, lons_p = load_data()

    bg = "#0a0e14"
    ocean = "#0a0e14"
    land_fill = "#151c25"
    land_edge = "#2a3444"
    grid_color = "#111820"
    dot_base = "#00d4ff"
    dot_power = "#ff4444"
    text_color = "#e6edf3"
    text_muted = "#8b949e"

    fig, ax = plt.subplots(figsize=(16, 8), facecolor=bg)
    ax.set_facecolor(ocean)

    ax.set_xlim(-180, 180)
    ax.set_ylim(-60, 85)

    for x in range(-180, 181, 30):
        ax.axvline(x, color=grid_color, linewidth=0.3, zorder=0)
    for y in range(-60, 91, 30):
        ax.axhline(y, color=grid_color, linewidth=0.3, zorder=0)

    print("  Loading coastlines...")
    world = load_coastlines()
    world.plot(ax=ax, color=land_fill, edgecolor=land_edge, linewidth=0.4, zorder=1)

    ax.scatter(lons_b, lats_b, s=1.5, c=dot_base, alpha=0.35, linewidths=0, zorder=2)
    ax.scatter(lons_p, lats_p, s=8, c=dot_power, alpha=0.75, linewidths=0, zorder=3)

    total = len(lats_b) + len(lats_p)
    ax.text(-175, -54, "human-override", color=text_color, fontsize=13,
            fontweight="bold", fontfamily="sans-serif", zorder=5)
    ax.text(-175, -58, f"{total:,} data centers mapped", color=text_muted,
            fontsize=9, fontfamily="sans-serif", zorder=5)

    ax.scatter([120], [-52], s=30, c=dot_power, alpha=0.75, linewidths=0, zorder=5)
    ax.text(124, -52.5, f"Power capacity known ({len(lats_p):,})", color=text_muted,
            fontsize=8, fontfamily="sans-serif", va="center", zorder=5)
    ax.scatter([120], [-56], s=10, c=dot_base, alpha=0.5, linewidths=0, zorder=5)
    ax.text(124, -56.5, f"Location only ({len(lats_b):,})", color=text_muted,
            fontsize=8, fontfamily="sans-serif", va="center", zorder=5)

    ax.set_xlim(-180, 180)
    ax.set_ylim(-60, 85)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)

    plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)

    PNG_PATH.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(PNG_PATH, dpi=150, bbox_inches="tight", pad_inches=0.1,
                facecolor=bg, edgecolor="none")
    plt.close(fig)

    size_kb = PNG_PATH.stat().st_size / 1024
    print(f"  Wrote {PNG_PATH} ({size_kb:.0f} KB)")


if __name__ == "__main__":
    generate()
