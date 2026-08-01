#!/usr/bin/env python3
"""Çankaya Konut Haritası — Server (Python stdlib, no Flask required)"""

import json
import os
import sqlite3
import urllib.parse
from http.server import HTTPServer, SimpleHTTPRequestHandler
from math import radians, cos, sin, asin, sqrt

DB = os.path.expanduser("~/.hermes/hepsiemlak.db")
WORK_LAT, WORK_LON = 39.8897782, 32.8594033

def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    return R * 2 * asin(sqrt(a))

class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path.rstrip('/')

        if path == '/api/neighborhoods':
            self.send_json(self.get_neighborhoods())
        elif path == '/api/listings':
            params = urllib.parse.parse_qs(parsed.query)
            limit = int(params.get('limit', [50])[0])
            offset = int(params.get('offset', [0])[0])
            sort = params.get('sort', ['score'])[0]
            order = params.get('order', ['desc'])[0]
            self.send_json(self.get_listings(limit, offset, sort, order))
        elif path == '/api/stats':
            self.send_json(self.get_stats())
        elif path == '/' or path == '':
            self.send_html()
        else:
            super().do_GET()

    def send_json(self, data):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-cache')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())

    def send_html(self):
        html_path = os.path.join(os.path.dirname(__file__), 'cankaya_harita.html')
        if os.path.exists(html_path):
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            with open(html_path, 'rb') as f:
                self.wfile.write(f.read())
        else:
            self.send_error(404, "HTML dosyası bulunamadı")

    def get_conn(self):
        conn = sqlite3.connect(DB)
        conn.row_factory = sqlite3.Row
        return conn

    def get_stats(self):
        conn = self.get_conn()
        cur = conn.cursor()
        cur.execute("""
            SELECT
                COUNT(*) as total,
                ROUND(AVG(price),0) as avg_price,
                ROUND(MIN(price),0) as min_price,
                ROUND(MAX(price),0) as max_price,
                ROUND(AVG(score),1) as avg_score,
                COUNT(DISTINCT neighborhood) as neighborhoods,
                ROUND(AVG(gross_sqm),1) as avg_sqm
            FROM listings
        """)
        stats = dict(cur.fetchone())
        conn.close()
        stats['work_lat'] = WORK_LAT
        stats['work_lon'] = WORK_LON
        return stats

    def get_neighborhoods(self):
        conn = self.get_conn()
        cur = conn.cursor()
        cur.execute("""
            SELECT
                neighborhood,
                COUNT(*) as count,
                ROUND(AVG(price),0) as avg_price,
                ROUND(MIN(price),0) as min_price,
                ROUND(MAX(price),0) as max_price,
                ROUND(AVG(gross_sqm),1) as avg_sqm,
                ROUND(AVG(score),1) as avg_score,
                ROUND(AVG(map_lat),6) as lat,
                ROUND(AVG(map_lon),6) as lon,
                ROUND(AVG(CAST(price AS REAL) / NULLIF(gross_sqm, 0)), 0) as avg_ppm
            FROM listings
            WHERE map_lat IS NOT NULL AND map_lon IS NOT NULL
            GROUP BY neighborhood
            ORDER BY count DESC
        """)
        rows = [dict(r) for r in cur.fetchall()]
        conn.close()

        for n in rows:
            if n['lat'] and n['lon']:
                n['distance_km'] = round(haversine_km(WORK_LAT, WORK_LON, n['lat'], n['lon']), 1)
            else:
                n['distance_km'] = None

        return rows

    def get_listings(self, limit=50, offset=0, sort='score', order='desc'):
        conn = self.get_conn()
        cur = conn.cursor()

        valid_sorts = {'price', 'score', 'gross_sqm', 'age'}
        if sort not in valid_sorts:
            sort = 'score'
        if order not in ('asc', 'desc'):
            order = 'desc'

        cur.execute(f"""
            SELECT id, price, room, neighborhood, gross_sqm, net_sqm, score,
                   map_lat, map_lon, detail_url, floor_name, age,
                   image_url, advertise_owner, seller_type
            FROM listings
            WHERE map_lat IS NOT NULL AND map_lon IS NOT NULL
            ORDER BY {sort} {order}
            LIMIT ? OFFSET ?
        """, (limit, offset))

        rows = [dict(r) for r in cur.fetchall()]
        conn.close()

        for r in rows:
            if r['map_lat'] and r['map_lon']:
                r['distance_km'] = round(haversine_km(WORK_LAT, WORK_LON, r['map_lat'], r['map_lon']), 1)
            else:
                r['distance_km'] = None
            r['url'] = r.pop('detail_url') or ''
            if r['url'] and not r['url'].startswith('http'):
                r['url'] = 'https://www.hepsiemlak.com/' + r['url'].lstrip('/')

        return rows


if __name__ == '__main__':
    port = 8200
    server = HTTPServer(('0.0.0.0', port), Handler)
    print(f"🚀 Çankaya Konut Haritası: http://localhost:{port}")
    print(f"   API: http://localhost:{port}/api/neighborhoods")
    print(f"        http://localhost:{port}/api/listings?limit=10&offset=0&sort=score&order=desc")
    print(f"        http://localhost:{port}/api/stats")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Kapatıldı")
        server.server_close()
