"""
Vercel Serverless Function cho OPhim API Proxy
"""

from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json
import requests
from datetime import datetime
import os

# OPhim API base URL
OPHIM_BASE_URL = "https://ophim17.cc"

# Simple in-memory cache (Vercel functions are stateless, nên cache này chỉ tồn tại trong 1 request)
# Để cache tốt hơn, nên dùng Vercel KV hoặc Redis
cache = {}

class handler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        """Handle GET requests"""
        
        # Parse URL
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        query_params = parse_qs(parsed_url.query)
        
        # Set CORS headers
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        # Route handling
        try:
            if path == '/':
                response = self.handle_root()
            elif path.startswith('/api/danh-sach/phim-moi-cap-nhat'):
                page = query_params.get('page', ['1'])[0]
                response = self.fetch_ophim(f"/danh-sach/phim-moi-cap-nhat?page={page}")
            elif path.startswith('/api/danh-sach/'):
                slug = path.replace('/api/danh-sach/', '')
                page = query_params.get('page', ['1'])[0]
                response = self.fetch_ophim(f"/danh-sach/{slug}?page={page}")
            elif path.startswith('/api/phim/'):
                slug = path.replace('/api/phim/', '')
                response = self.fetch_ophim(f"/phim/{slug}")
            elif path.startswith('/api/v1/api/tim-kiem'):
                keyword = query_params.get('keyword', [''])[0]
                limit = query_params.get('limit', [''])[0]
                endpoint = f"/v1/api/tim-kiem?keyword={keyword}"
                if limit:
                    endpoint += f"&limit={limit}"
                response = self.fetch_ophim(endpoint)
            elif path == '/api/the-loai':
                response = self.fetch_ophim("/the-loai")
            elif path == '/api/quoc-gia':
                response = self.fetch_ophim("/quoc-gia")
            else:
                response = {"error": "Endpoint not found"}
            
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            error_response = {"error": str(e)}
            self.wfile.write(json.dumps(error_response).encode('utf-8'))
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def handle_root(self):
        """API documentation"""
        return {
            "name": "OPhim Proxy API on Vercel",
            "version": "2.0.0",
            "description": "Serverless proxy for OPhim API",
            "endpoints": {
                "GET /api/danh-sach/phim-moi-cap-nhat": "Phim mới cập nhật",
                "GET /api/danh-sach/<slug>": "Danh sách theo danh mục",
                "GET /api/phim/<slug>": "Chi tiết phim",
                "GET /api/v1/api/tim-kiem": "Tìm kiếm phim",
                "GET /api/the-loai": "Danh sách thể loại",
                "GET /api/quoc-gia": "Danh sách quốc gia"
            },
            "deployed_on": "Vercel Serverless Functions",
            "timestamp": datetime.now().isoformat()
        }
    
    def fetch_ophim(self, endpoint):
        """Fetch data from OPhim API"""
        try:
            url = f"{OPHIM_BASE_URL}{endpoint}"
            
            # Vercel Edge caching sẽ tự động cache response
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            return {"error": f"Failed to fetch from OPhim: {str(e)}"}
