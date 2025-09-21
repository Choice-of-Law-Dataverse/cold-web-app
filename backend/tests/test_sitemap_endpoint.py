#!/usr/bin/env python3
"""
Simple test script for the sitemap endpoint.
This script demonstrates how to use the sitemap API endpoint.
"""

import json
import sys

import requests

# Configuration
API_BASE_URL = "https://cold-backend-beta.livelyisland-3dd94f86.switzerlandnorth.azurecontainerapps.io/api/v1"
JWT_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzb21lLWZpeGVkLXVzZXIiLCJyb2xlIjoiYWRtaW4ifQ.3_fkTu5wVfv5OIAxY2S4xzEFSaPWRAyYdGXOppUQ8eg"


def test_sitemap_endpoint():
    """Test the sitemap/urls endpoint."""

    url = f"{API_BASE_URL}/sitemap/urls"
    headers = {
        "Authorization": f"Bearer {JWT_TOKEN}",
        "Content-Type": "application/json",
    }

    print(f"Testing endpoint: {url}")
    print(f"Using JWT token: {JWT_TOKEN[:50]}...")

    response: requests.Response | None = None
    try:
        response = requests.get(url, headers=headers, timeout=30)

        print(f"\nResponse Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")

        if response.status_code == 200:
            data = response.json()

            print("\n✅ Success! Retrieved sitemap data:")

            # Show alpha environment data
            alpha_data = data.get("alpha", {})
            print(
                f"Alpha URLs ({alpha_data.get('base_url', 'N/A')}): {alpha_data.get('total_count', 0)}"
            )

            # Show beta environment data
            beta_data = data.get("beta", {})
            print(
                f"Beta URLs ({beta_data.get('base_url', 'N/A')}): {beta_data.get('total_count', 0)}"
            )

            print(f"Tables processed: {len(data.get('tables_processed', []))}")

            # Show first 5 URLs from each environment as examples
            alpha_urls = alpha_data.get("urls", [])
            if alpha_urls:
                print("\nFirst 5 Alpha URLs:")
                for i, url in enumerate(alpha_urls[:5], 1):
                    print(f"  {i}. {url}")

            beta_urls = beta_data.get("urls", [])
            if beta_urls:
                print("\nFirst 5 Beta URLs:")
                for i, url in enumerate(beta_urls[:5], 1):
                    print(f"  {i}. {url}")

            # Show table breakdown
            tables = data.get("tables_processed", [])
            if tables:
                print(f"\nTables processed: {', '.join(tables)}")

            return True

        else:
            print(f"\n❌ Error: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {json.dumps(error_data, indent=2)}")
            except Exception:
                print(f"Response text: {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"\n❌ Request failed: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"\n❌ JSON decode error: {e}")
        response_text = response.text if response is not None else ""
        print(f"Response text: {response_text}")
        return False


def main():
    """Main function."""
    print("CoLD Sitemap API Test")
    print("=" * 50)

    success = test_sitemap_endpoint()

    if success:
        print("\n🎉 Test completed successfully!")
        sys.exit(0)
    else:
        print("\n💥 Test failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
