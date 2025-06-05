#!/usr/bin/env python
"""
Standalone script to run the Odoo MCP server 
Uses the same approach as in the official MCP SDK examples
"""
import sys
import os
import asyncio
import anyio
import logging
import datetime

from mcp.server.stdio import stdio_server
from mcp.server.lowlevel import Server
import mcp.types as types

from odoo_mcp.server import mcp  # FastMCP instance from our code


def setup_logging():
    """Set up logging to both console and file"""
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
    os.makedirs(log_dir, exist_ok=True)
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"mcp_server_{timestamp}.log")
    
    # Configure logging
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    
    # Remove existing handlers if any
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Console handler with clean format
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # File handler with detailed format
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    
    # Clean format for console
    console_formatter = logging.Formatter('[%(levelname)s] %(message)s')
    console_handler.setFormatter(console_formatter)
    
    # Detailed format for file
    file_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
    file_handler.setFormatter(file_formatter)
    
    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger


def main() -> int:
    """
    Run the MCP server based on the official examples
    """
    logger = setup_logging()
    
    try:
        logger.info("=== ODOO MCP SERVER STARTING ===")
        logger.info(f"Python {sys.version.split()[0]}")
        
        # Log Odoo environment variables in a cleaner format
        odoo_vars = {k: v for k, v in os.environ.items() if k.startswith("ODOO_")}
        if odoo_vars:
            logger.info("Odoo Configuration:")
            for key in sorted(odoo_vars.keys()):
                if key == "ODOO_PASSWORD":
                    logger.info(f"  {key}: ***hidden***")
                else:
                    logger.info(f"  {key}: {odoo_vars[key]}")
        
        # Run server in stdio mode like the official examples
        async def arun():
            logger.info("Starting MCP server...")
            async with stdio_server() as streams:
                # Keep the server running until explicitly stopped
                try:
                    await mcp._mcp_server.run(
                        streams[0], streams[1], mcp._mcp_server.create_initialization_options()
                    )
                    logger.info("Server initialized and ready for requests")
                    # Add an infinite wait to keep the server alive
                    while True:
                        await asyncio.sleep(3600)  # Sleep for an hour and continue running
                except asyncio.CancelledError:
                    logger.info("Server task cancelled")
                except Exception as e:
                    logger.error(f"Server error: {e}")
                
        # Run server
        anyio.run(arun)
        logger.info("Server stopped normally")
        return 0
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 