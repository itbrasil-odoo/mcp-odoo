#!/usr/bin/env python
"""
Simplified HTTP server for Odoo MCP
"""
import os
import sys
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
import logging

# Adicionar o diretório src ao path para encontrar o módulo odoo_mcp
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
from odoo_mcp.server import get_models, get_model_info, get_record, search_records_resource

# Configure logging
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

class MCPHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
    def do_GET(self):
        if self.path == '/':
            self._set_headers()
            response = {"message": "Odoo MCP Server is running"}
            self.wfile.write(json.dumps(response).encode())
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode())
    
    def do_POST(self):
        if self.path == '/mcp/resource':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode())
                resource = data.get("resource")
                
                if not resource:
                    self._set_headers(400)
                    self.wfile.write(json.dumps({"error": "Missing 'resource' parameter"}).encode())
                    return
                
                logger.info(f"Resource request: {resource}")
                
                # Handle resource request
                if resource == "odoo://models":
                    result = get_models()
                elif resource.startswith("odoo://model/"):
                    model_name = resource.replace("odoo://model/", "")
                    result = get_model_info(model_name)
                elif resource.startswith("odoo://record/"):
                    parts = resource.replace("odoo://record/", "").split("/")
                    if len(parts) != 2:
                        self._set_headers(400)
                        self.wfile.write(json.dumps({"error": "Invalid record resource format"}).encode())
                        return
                    model_name, record_id = parts
                    result = get_record(model_name, record_id)
                elif resource.startswith("odoo://search/"):
                    parts = resource.replace("odoo://search/", "").split("/")
                    if len(parts) != 2:
                        self._set_headers(400)
                        self.wfile.write(json.dumps({"error": "Invalid search resource format"}).encode())
                        return
                    model_name, domain = parts
                    result = search_records_resource(model_name, domain)
                else:
                    self._set_headers(400)
                    self.wfile.write(json.dumps({"error": f"Unknown resource: {resource}"}).encode())
                    return
                
                # Parse result as JSON
                try:
                    result_json = json.loads(result)
                    self._set_headers()
                    self.wfile.write(json.dumps(result_json).encode())
                except:
                    self._set_headers()
                    self.wfile.write(json.dumps({"result": result}).encode())
                    
            except Exception as e:
                logger.error(f"Error processing resource request: {str(e)}")
                self._set_headers(500)
                self.wfile.write(json.dumps({"error": str(e)}).encode())
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode())

def run(server_class=HTTPServer, handler_class=MCPHandler, port=8080):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    logger.info(f'Starting HTTP server on port {port}...')
    httpd.serve_forever()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8080"))
    run(port=port)