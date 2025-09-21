#!/usr/bin/env python3
"""
Simple test script for the sitemap endpoint.
This script demonstrates how to use the sitemap API endpoint.
"""

import json
import logging
import sys

import requests

logger = logging.getLogger(__name__)

# Configuration
API_BASE_URL = "https://cold-backend-beta.livelyisland-3dd94f86.switzerlandnorth.azurecontainerapps.io/api/v1"
JWT_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzb21lLWZpeGVkLXVzZXIiLCJyb2xlIjoiYWRtaW4ifQ.3_fkTu5wVfv5OIAxY2S4xzEFSaPWRAyYdGXOppUQ8eg"  # noqa: E501


def test_sitemap_endpoint():
    """Test the sitemap/urls endpoint."""

    url = f"{API_BASE_URL}/sitemap/urls"
    headers = {
        "Authorization": f"Bearer {JWT_TOKEN}",
        "Content-Type": "application/json",
    }

    logger.debug("Testing endpoint: %s", url)
    logger.debug("Using JWT token: %s...", JWT_TOKEN[:50])

    response: requests.Response | None = None
    try:
        response = requests.get(url, headers=headers, timeout=30)

        logger.debug("\nResponse Status Code: %s", response.status_code)
        logger.debug("Response Headers: %s", dict(response.headers))

        if response.status_code == 200:
            data = response.json()

            logger.debug("\n✅ Success! Retrieved sitemap data:")

            # Show alpha environment data
            alpha_data = data.get("alpha", {})
            logger.debug(f"Alpha URLs ({alpha_data.get('base_url', 'N/A')}): {alpha_data.get('total_count', 0)}")

            # Show beta environment data
            beta_data = data.get("beta", {})
            logger.debug(f"Beta URLs ({beta_data.get('base_url', 'N/A')}): {beta_data.get('total_count', 0)}")

            logger.debug(f"Tables processed: {len(data.get('tables_processed', []))}")

            # Show first 5 URLs from each environment as examples
            alpha_urls = alpha_data.get("urls", [])
            if alpha_urls:
                logger.debug("\nFirst 5 Alpha URLs:")
                for i, url in enumerate(alpha_urls[:5], 1):
                    logger.debug(f"{i}. {url}")

            beta_urls = beta_data.get("urls", [])
            if beta_urls:
                logger.debug("\nFirst 5 Beta URLs:")
                for i, url in enumerate(beta_urls[:5], 1):
                    logger.debug(f"{i}. {url}")

            # Show table breakdown
            tables = data.get("tables_processed", [])
            if tables:
                logger.debug(f"\nTables processed: {', '.join(tables)}")

            return True

        else:
            logger.debug(f"\n❌ Error: {response.status_code}")
            try:
                error_data = response.json()
                logger.debug(f"Error details: {json.dumps(error_data, indent=2)}")
            except Exception:
                logger.debug(f"Response text: {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        logger.debug(f"\n❌ Request failed: {e}")
        return False
    except json.JSONDecodeError as e:
        logger.debug(f"\n❌ JSON decode error: {e}")
        response_text = response.text if response is not None else ""
        logger.debug(f"Response text: {response_text}")
        return False


def main():
    """Main function."""
    logger.debug("CoLD Sitemap API Test")
    logger.debug("=" * 50)

    success = test_sitemap_endpoint()

    if success:
        logger.debug("\n🎉 Test completed successfully!")
        sys.exit(0)
    else:
        logger.debug("\n💥 Test failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
