#!/usr/bin/env python3
"""
Serply Search API MCP Server - FastMCP with D402 Transport Wrapper

Uses FastMCP from official MCP SDK with D402MCPTransport wrapper for HTTP 402.

Architecture:
- FastMCP for tool decorators and Context objects
- D402MCPTransport wraps the /mcp route for HTTP 402 interception
- Proper HTTP 402 status codes (not JSON-RPC wrapped)

Generated from OpenAPI: https://serply.io/docs

Environment Variables:
- SERPLY_API_KEY: Server's internal API key (for paid requests)
- SERVER_ADDRESS: Payment address (IATP wallet contract)
- MCP_OPERATOR_PRIVATE_KEY: Operator signing key
- D402_TESTING_MODE: Skip facilitator (default: true)
"""

import os
import logging
import sys
from typing import Any, Callable, Dict, List, Optional, Sequence, Set, Tuple, Union
from datetime import datetime

import requests
from retry import retry
from dotenv import load_dotenv
import uvicorn

load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('serply-search-api_mcp')

# FastMCP from official SDK
from mcp.server.fastmcp import FastMCP, Context
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware
from starlette.routing import Route

# D402 payment protocol - using Starlette middleware
from traia_iatp.d402.starlette_middleware import D402PaymentMiddleware
from traia_iatp.d402.mcp_middleware import require_payment_for_tool, get_active_api_key
from traia_iatp.d402.payment_introspection import extract_payment_configs_from_mcp
from traia_iatp.d402.types import TokenAmount, TokenAsset, EIP712Domain

# Configuration
STAGE = os.getenv("STAGE", "MAINNET").upper()
PORT = int(os.getenv("PORT", "8000"))
SERVER_ADDRESS = os.getenv("SERVER_ADDRESS")
if not SERVER_ADDRESS:
    raise ValueError("SERVER_ADDRESS required for payment protocol")

API_KEY = os.getenv("SERPLY_API_KEY")
if not API_KEY:
    logger.warning(f"⚠️  SERPLY_API_KEY not set - payment required for all requests")

logger.info("="*80)
logger.info(f"Serply Search API MCP Server (FastMCP + D402 Wrapper)")
logger.info(f"API: https://api.serply.io")
logger.info(f"Payment: {SERVER_ADDRESS}")
logger.info(f"API Key: {'✅' if API_KEY else '❌ Payment required'}")
logger.info("="*80)

# Create FastMCP server
mcp = FastMCP("Serply Search API MCP Server", host="0.0.0.0")

logger.info(f"✅ FastMCP server created")

# ============================================================================
# TOOL IMPLEMENTATIONS
# ============================================================================
# Tool implementations will be added here by endpoint_implementer_crew
# Each tool will use the @mcp.tool() and @require_payment_for_tool() decorators


# D402 Payment Middleware
# The HTTP 402 payment protocol middleware is already configured in the server initialization.
# It's imported from traia_iatp.d402.mcp_middleware and auto-detects configuration from:
# - PAYMENT_ADDRESS or EVM_ADDRESS: Where to receive payments
# - EVM_NETWORK: Blockchain network (default: base-sepolia)
# - DEFAULT_PRICE_USD: Price per request (default: $0.001)
# - SERPLY_SEARCH_API_API_KEY: Server's internal API key for payment mode
#
# All payment verification logic is handled by the traia_iatp.d402 module.
# No custom implementation needed!


# API Endpoint Tool Implementations

@mcp.tool()
@require_payment_for_tool(
    price=TokenAmount(
        amount="10",  # 1e-05 tokens
        asset=TokenAsset(
            address="0xaf88d065e77c8cC2239327C5EDb3A432268e5831",
            decimals=6,
            network="arbitrum_one",
            eip712=EIP712Domain(
                name="IATPWallet",
                version="1"
            )
        )
    ),
    description="Perform a Google web search using Serply. Returns "

)
async def serply_google_search(
    context: Context,
    query: str,
    proxy_location: Optional[str] = None,
    user_agent: str = "desktop"
) -> Any:
    """
    Perform a Google web search using Serply. Returns structured organic search results with title, link, and description, plus total result count and optional answer box content.

    Generated from OpenAPI endpoint: GET /v1/search/{query}

    Args:
        context: MCP context (auto-injected by framework, not user-provided)
        query: URL-encoded query string following Google's search parameter format. Pass the full parameter string (e.g. 'q=search+api' or 'q=search+api&num=100'). (optional) Examples: "q=openai+company", "q=artificial+intelligence&num=100"
        proxy_location: Geographic proxy location for the search (sent as X-Proxy-Location header). (optional) Examples: "US"
        user_agent: Device type for the request (sent as X-User-Agent header). (optional, default: "desktop") Examples: "desktop"

    Returns:
        API response (dict, list, or other JSON type)

    Example Usage:
        await serply_google_search(query="q=openai+company")

        Note: 'context' parameter is auto-injected by MCP framework
    """
    # Payment already verified by @require_payment_for_tool decorator
    # Get API key using helper (handles request.state fallback)
    api_key = get_active_api_key(context)

    try:
        url = f"https://api.serply.io/v1/search/{query}"
        params = {
            "proxy_location": proxy_location,
            "user_agent": user_agent
        }
        params = {k: v for k, v in params.items() if v is not None}
        headers = {}
        if api_key:
            # Custom header (primary)
            headers["X-Api-Key"] = api_key
            # Also send standard formats for robustness
            headers["Authorization"] = f"Bearer {api_key}"
            headers["X-API-Key"] = api_key

        response = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=30
        )
        response.raise_for_status()

        return response.json()

    except Exception as e:
        logger.error(f"Error in serply_google_search: {e}")
        return {"error": str(e), "endpoint": "/v1/search/{query}"}


@mcp.tool()
@require_payment_for_tool(
    price=TokenAmount(
        amount="10",  # 1e-05 tokens
        asset=TokenAsset(
            address="0xaf88d065e77c8cC2239327C5EDb3A432268e5831",
            decimals=6,
            network="arbitrum_one",
            eip712=EIP712Domain(
                name="IATPWallet",
                version="1"
            )
        )
    ),
    description="Perform a Bing web search using Serply. Returns or"

)
async def serply_bing_search(
    context: Context,
    query: str,
    proxy_location: Optional[str] = None,
    user_agent: str = "desktop"
) -> Any:
    """
    Perform a Bing web search using Serply. Returns organic search results alongside advertisement and shopping-ad data including positioning, pricing, and advertiser information.

    Generated from OpenAPI endpoint: GET /v1/b/search/{query}

    Args:
        context: MCP context (auto-injected by framework, not user-provided)
        query: URL-encoded query string following Bing's search parameter format. Pass the full parameter string (e.g. 'q=search+api'). (optional) Examples: "q=search+api", "q=bitcoin+price"
        proxy_location: Geographic proxy location for the search (sent as X-Proxy-Location header). (optional) Examples: "US"
        user_agent: Device type for the request (sent as X-User-Agent header). (optional, default: "desktop") Examples: "desktop"

    Returns:
        API response (dict, list, or other JSON type)

    Example Usage:
        await serply_bing_search(query="q=search+api")

        Note: 'context' parameter is auto-injected by MCP framework
    """
    # Payment already verified by @require_payment_for_tool decorator
    # Get API key using helper (handles request.state fallback)
    api_key = get_active_api_key(context)

    try:
        url = f"https://api.serply.io/v1/b/search/{query}"
        params = {
            "proxy_location": proxy_location,
            "user_agent": user_agent
        }
        params = {k: v for k, v in params.items() if v is not None}
        headers = {}
        if api_key:
            # Custom header (primary)
            headers["X-Api-Key"] = api_key
            # Also send standard formats for robustness
            headers["Authorization"] = f"Bearer {api_key}"
            headers["X-API-Key"] = api_key

        response = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=30
        )
        response.raise_for_status()

        return response.json()

    except Exception as e:
        logger.error(f"Error in serply_bing_search: {e}")
        return {"error": str(e), "endpoint": "/v1/b/search/{query}"}


@mcp.tool()
@require_payment_for_tool(
    price=TokenAmount(
        amount="10",  # 1e-05 tokens
        asset=TokenAsset(
            address="0xaf88d065e77c8cC2239327C5EDb3A432268e5831",
            decimals=6,
            network="arbitrum_one",
            eip712=EIP712Domain(
                name="IATPWallet",
                version="1"
            )
        )
    ),
    description="Perform a Google Scholar search using Serply. Retu"

)
async def serply_google_scholar(
    context: Context,
    query: str,
    proxy_location: Optional[str] = None,
    user_agent: str = "desktop"
) -> Any:
    """
    Perform a Google Scholar search using Serply. Returns academic search results with title, link, and description/abstract, plus aggregate result count.

    Generated from OpenAPI endpoint: GET /v1/scholar/{query}

    Args:
        context: MCP context (auto-injected by framework, not user-provided)
        query: URL-encoded query string following Google Scholar's search parameter format. Pass the full parameter string (e.g. 'q=high+frequency+trading'). (optional) Examples: "q=retrieval+augmented+generation", "q=graph+neural+networks"
        proxy_location: Geographic proxy location for the search (sent as X-Proxy-Location header). (optional) Examples: "US"
        user_agent: Device type for the request (sent as X-User-Agent header). (optional, default: "desktop") Examples: "desktop"

    Returns:
        API response (dict, list, or other JSON type)

    Example Usage:
        await serply_google_scholar(query="q=retrieval+augmented+generation")

        Note: 'context' parameter is auto-injected by MCP framework
    """
    # Payment already verified by @require_payment_for_tool decorator
    # Get API key using helper (handles request.state fallback)
    api_key = get_active_api_key(context)

    try:
        url = f"https://api.serply.io/v1/scholar/{query}"
        params = {
            "proxy_location": proxy_location,
            "user_agent": user_agent
        }
        params = {k: v for k, v in params.items() if v is not None}
        headers = {}
        if api_key:
            # Custom header (primary)
            headers["X-Api-Key"] = api_key
            # Also send standard formats for robustness
            headers["Authorization"] = f"Bearer {api_key}"
            headers["X-API-Key"] = api_key

        response = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=30
        )
        response.raise_for_status()

        return response.json()

    except Exception as e:
        logger.error(f"Error in serply_google_scholar: {e}")
        return {"error": str(e), "endpoint": "/v1/scholar/{query}"}


# TODO: Add your API-specific functions here

# ============================================================================
# APPLICATION SETUP WITH STARLETTE MIDDLEWARE
# ============================================================================

def create_app_with_middleware():
    """
    Create Starlette app with d402 payment middleware.
    
    Strategy:
    1. Get FastMCP's Starlette app via streamable_http_app()
    2. Extract payment configs from @require_payment_for_tool decorators
    3. Add Starlette middleware with extracted configs
    4. Single source of truth - no duplication!
    """
    logger.info("🔧 Creating FastMCP app with middleware...")
    
    # Get FastMCP's Starlette app
    app = mcp.streamable_http_app()
    logger.info(f"✅ Got FastMCP Starlette app")
    
    # Extract payment configs from decorators (single source of truth!)
    tool_payment_configs = extract_payment_configs_from_mcp(mcp, SERVER_ADDRESS)
    logger.info(f"📊 Extracted {len(tool_payment_configs)} payment configs from @require_payment_for_tool decorators")
    
    # D402 Configuration
    facilitator_url = os.getenv("FACILITATOR_URL") or os.getenv("D402_FACILITATOR_URL")
    operator_key = os.getenv("MCP_OPERATOR_PRIVATE_KEY")
    network = os.getenv("NETWORK", "sepolia")
    testing_mode = os.getenv("D402_TESTING_MODE", "false").lower() == "true"
    
    # Log D402 configuration with prominent facilitator info
    logger.info("="*60)
    logger.info("D402 Payment Protocol Configuration:")
    logger.info(f"  Server Address: {SERVER_ADDRESS}")
    logger.info(f"  Network: {network}")
    logger.info(f"  Operator Key: {'✅ Set' if operator_key else '❌ Not set'}")
    logger.info(f"  Testing Mode: {'⚠️  ENABLED (bypasses facilitator)' if testing_mode else '✅ DISABLED (uses facilitator)'}")
    logger.info("="*60)
    
    if not facilitator_url and not testing_mode:
        logger.error("❌ FACILITATOR_URL required when testing_mode is disabled!")
        raise ValueError("Set FACILITATOR_URL or enable D402_TESTING_MODE=true")
    
    if facilitator_url:
        logger.info(f"🌐 FACILITATOR: {facilitator_url}")
        if "localhost" in facilitator_url or "127.0.0.1" in facilitator_url or "host.docker.internal" in facilitator_url:
            logger.info(f"   📍 Using LOCAL facilitator for development")
        else:
            logger.info(f"   🌍 Using REMOTE facilitator for production")
    else:
        logger.warning("⚠️  D402 Testing Mode - Facilitator bypassed")
    logger.info("="*60)
    
    # Add CORS middleware first (processes before other middleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all origins
        allow_credentials=True,
        allow_methods=["*"],  # Allow all methods
        allow_headers=["*"],  # Allow all headers
        expose_headers=["mcp-session-id"],  # Expose custom headers to browser
    )
    logger.info("✅ Added CORS middleware (allow all origins, expose mcp-session-id)")
    
    # Add D402 payment middleware with extracted configs
    app.add_middleware(
        D402PaymentMiddleware,
        tool_payment_configs=tool_payment_configs,
        server_address=SERVER_ADDRESS,
        requires_auth=True,  # Extracts API keys + checks payment
        internal_api_key=API_KEY,  # Server's internal key (for Mode 2: paid access)
        testing_mode=testing_mode,
        facilitator_url=facilitator_url,
        facilitator_api_key=os.getenv("D402_FACILITATOR_API_KEY"),
        server_name="serply-search-api-mcp-server"  # MCP server ID for tracking
    )
    logger.info("✅ Added D402PaymentMiddleware")
    logger.info("   - Auth extraction: Enabled")
    logger.info("   - Dual mode: API key OR payment")
    
    # Add health check endpoint (bypasses middleware).
    # Note: app.route() decorator was removed in Starlette >= 0.21.
    # We define the function first and register it via Route + router.routes,
    # which works across all Starlette versions including 0.45+.
    async def health_check(request: Request) -> JSONResponse:
        """Health check endpoint for container orchestration."""
        return JSONResponse(
            content={
                "status": "healthy",
                "service": "serply-search-api-mcp-server",
                "timestamp": datetime.now().isoformat()
            }
        )
    app.router.routes.append(Route("/health", health_check, methods=["GET"]))
    logger.info("✅ Added /health endpoint")
    
    return app

if __name__ == "__main__":
    logger.info("="*80)
    logger.info(f"Starting Serply Search API MCP Server")
    logger.info("="*80)
    logger.info("Architecture:")
    logger.info("  1. D402PaymentMiddleware intercepts requests")
    logger.info("     - Extracts API keys from Authorization header")
    logger.info("     - Checks payment → HTTP 402 if no API key AND no payment")
    logger.info("  2. FastMCP processes valid requests with tool decorators")
    logger.info("="*80)
    
    # Create app with middleware
    app = create_app_with_middleware()
    
    # Run with uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=PORT,
        log_level=os.getenv("LOG_LEVEL", "info").lower()
    )
