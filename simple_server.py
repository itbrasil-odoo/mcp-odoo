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
from odoo_mcp.odoo_client import get_odoo_client

# Configure logging
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

class MCPHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_OPTIONS(self):
        self._set_headers()
        
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
                odoo_client = get_odoo_client()
                
                # Handle resource request
                try:
                    if resource == "odoo://models":
                        # Get all models
                        models = odoo_client.get_models()
                        self._set_headers()
                        self.wfile.write(json.dumps(models).encode())
                        
                    elif resource.startswith("odoo://model/"):
                        # Get model info
                        model_name = resource.replace("odoo://model/", "")
                        
                        # Verificar se o modelo existe
                        try:
                            # Primeiro, verifique se o modelo existe usando search
                            model_ids = odoo_client._execute(
                                "ir.model",
                                "search",
                                [("model", "=", model_name)]
                            )
                            
                            if not model_ids:
                                self._set_headers(404)
                                self.wfile.write(json.dumps({
                                    "error": f"Model {model_name} not found",
                                    "resource": resource
                                }).encode())
                                return
                            
                            # Depois, leia os dados do modelo
                            model_info = odoo_client._execute(
                                "ir.model",
                                "read",
                                model_ids,
                                ["name", "model"]
                            )[0]
                            
                            # Tente obter os campos do modelo
                            try:
                                fields = odoo_client.get_model_fields(model_name)
                                if isinstance(fields, dict) and "error" not in fields:
                                    model_info["fields"] = fields
                            except Exception as field_error:
                                model_info["fields_error"] = str(field_error)
                            
                            self._set_headers()
                            self.wfile.write(json.dumps(model_info).encode())
                            
                        except Exception as e:
                            logger.error(f"Error getting model info: {str(e)}")
                            self._set_headers(500)
                            self.wfile.write(json.dumps({
                                "error": str(e),
                                "resource": resource
                            }).encode())
                            
                    elif resource.startswith("odoo://record/"):
                        # Get record by ID
                        parts = resource.replace("odoo://record/", "").split("/")
                        if len(parts) != 2:
                            self._set_headers(400)
                            self.wfile.write(json.dumps({
                                "error": "Invalid record resource format",
                                "resource": resource
                            }).encode())
                            return
                            
                        model_name, record_id = parts
                        try:
                            record_id_int = int(record_id)
                            record = odoo_client.read_records(model_name, [record_id_int])
                            
                            if not record:
                                self._set_headers(404)
                                self.wfile.write(json.dumps({
                                    "error": f"Record not found: {model_name} ID {record_id}",
                                    "resource": resource
                                }).encode())
                                return
                                
                            self._set_headers()
                            self.wfile.write(json.dumps(record[0]).encode())
                            
                        except Exception as e:
                            logger.error(f"Error getting record: {str(e)}")
                            self._set_headers(500)
                            self.wfile.write(json.dumps({
                                "error": str(e),
                                "resource": resource
                            }).encode())
                            
                    elif resource.startswith("odoo://search/"):
                        # Search records
                        parts = resource.replace("odoo://search/", "").split("/")
                        if len(parts) != 2:
                            self._set_headers(400)
                            self.wfile.write(json.dumps({
                                "error": "Invalid search resource format",
                                "resource": resource
                            }).encode())
                            return
                            
                        model_name, domain = parts
                        try:
                            domain_list = json.loads(domain)
                            limit = 10  # Default limit
                            
                            results = odoo_client.search_read(model_name, domain_list, limit=limit)
                            
                            self._set_headers()
                            self.wfile.write(json.dumps(results).encode())
                            
                        except Exception as e:
                            logger.error(f"Error searching records: {str(e)}")
                            self._set_headers(500)
                            self.wfile.write(json.dumps({
                                "error": str(e),
                                "resource": resource
                            }).encode())
                            
                    else:
                        self._set_headers(400)
                        self.wfile.write(json.dumps({
                            "error": f"Unknown resource: {resource}",
                            "resource": resource
                        }).encode())
                        
                except Exception as e:
                    logger.error(f"Error processing resource: {str(e)}")
                    self._set_headers(500)
                    self.wfile.write(json.dumps({
                        "error": str(e),
                        "resource": resource
                    }).encode())
                    
            except Exception as e:
                logger.error(f"Error processing request: {str(e)}")
                self._set_headers(500)
                self.wfile.write(json.dumps({
                    "error": f"Server error: {str(e)}"
                }).encode())
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