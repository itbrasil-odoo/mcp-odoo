#!/usr/bin/env python
"""
HTTP server for Odoo MCP
"""
import os
import sys
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import json
import logging

# Adicionar o diretório src ao path para encontrar o módulo odoo_mcp
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
from odoo_mcp.server import mcp  # FastMCP instance from our code

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="Odoo MCP Server")

@app.post("/mcp/resource")
async def resource_endpoint(request: Request):
    """Endpoint for MCP resources"""
    try:
        data = await request.json()
        resource = data.get("resource")
        
        if not resource:
            return JSONResponse({"error": "Missing 'resource' parameter"}, status_code=400)
        
        logger.info(f"Resource request: {resource}")
        
        # Handle resource request
        if resource == "odoo://models":
            result = mcp.resources["odoo://models"]()
        elif resource.startswith("odoo://model/"):
            model_name = resource.replace("odoo://model/", "")
            result = mcp.resources["odoo://model/{model_name}"](model_name)
        elif resource.startswith("odoo://record/"):
            parts = resource.replace("odoo://record/", "").split("/")
            if len(parts) != 2:
                return JSONResponse({"error": "Invalid record resource format"}, status_code=400)
            model_name, record_id = parts
            result = mcp.resources["odoo://record/{model_name}/{record_id}"](model_name, record_id)
        elif resource.startswith("odoo://search/"):
            parts = resource.replace("odoo://search/", "").split("/")
            if len(parts) != 2:
                return JSONResponse({"error": "Invalid search resource format"}, status_code=400)
            model_name, domain = parts
            result = mcp.resources["odoo://search/{model_name}/{domain}"](model_name, domain)
        else:
            return JSONResponse({"error": f"Unknown resource: {resource}"}, status_code=400)
        
        # Parse result as JSON
        try:
            result_json = json.loads(result)
            return JSONResponse(result_json)
        except:
            return JSONResponse({"result": result})
            
    except Exception as e:
        logger.error(f"Error processing resource request: {str(e)}")
        return JSONResponse({"error": str(e)}, status_code=500)

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Odoo MCP Server is running"}

if __name__ == "__main__":
    # Get port from environment or use default
    port = int(os.environ.get("PORT", "8080"))
    
    # Start server
    logger.info(f"Starting HTTP server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)