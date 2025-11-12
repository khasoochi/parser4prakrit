"""
Aksharamukha REST API client for transliteration
Uses the public Aksharamukha API at https://aksharamukha.appspot.com
"""

import requests
from typing import Optional

class AksharamukhaAPI:
    """Client for Aksharamukha transliteration REST API"""

    BASE_URL = "https://aksharamukha.appspot.com/api/public"

    @staticmethod
    def transliterate(text: str, source: str, target: str, timeout: int = 10) -> Optional[str]:
        """
        Transliterate text using Aksharamukha API

        Args:
            text: Text to transliterate
            source: Source script (e.g., 'Devanagari', 'HK')
            target: Target script (e.g., 'HK', 'Devanagari')
            timeout: Request timeout in seconds

        Returns:
            Transliterated text or None if request fails
        """
        try:
            params = {
                'source': source,
                'target': target,
                'text': text
            }

            response = requests.get(
                f"{AksharamukhaAPI.BASE_URL}/",
                params=params,
                timeout=timeout
            )

            if response.status_code == 200:
                return response.text.strip()
            else:
                print(f"⚠ Aksharamukha API error: HTTP {response.status_code}")
                return None

        except requests.exceptions.Timeout:
            print("⚠ Aksharamukha API timeout")
            return None
        except requests.exceptions.RequestException as e:
            print(f"⚠ Aksharamukha API connection error: {e}")
            return None
        except Exception as e:
            print(f"⚠ Aksharamukha API unexpected error: {e}")
            return None

    @staticmethod
    def devanagari_to_hk(text: str) -> Optional[str]:
        """
        Convert Devanagari to Harvard-Kyoto

        Args:
            text: Devanagari text

        Returns:
            Harvard-Kyoto transliteration or None if fails
        """
        return AksharamukhaAPI.transliterate(text, 'Devanagari', 'HK')

    @staticmethod
    def hk_to_devanagari(text: str) -> Optional[str]:
        """
        Convert Harvard-Kyoto to Devanagari

        Args:
            text: Harvard-Kyoto text

        Returns:
            Devanagari transliteration or None if fails
        """
        return AksharamukhaAPI.transliterate(text, 'HK', 'Devanagari')


def test_transliteration():
    """Test Aksharamukha API transliteration"""
    test_cases = [
        ('पुच्छिस्संति', 'pucchissaMti'),
        ('मुणिन्ति', 'muNinti'),
        ('जाणिन्ति', 'jANinti'),
        ('मुणीहिंतो', 'muNIhiMto'),
        ('नेमो', 'nemo'),
        ('भवति', 'bhavati'),
    ]

    print("Testing Aksharamukha API transliteration:")
    print("=" * 60)

    for dev, expected in test_cases:
        result = AksharamukhaAPI.devanagari_to_hk(dev)
        if result:
            status = "✓" if result == expected else "✗"
            print(f"{status} {dev:15s} → {result:15s} (expected: {expected})")
        else:
            print(f"✗ {dev:15s} → API failed")

    print()
    print("Testing reverse transliteration:")
    print("=" * 60)
    test_hk = "pucchissaMti"
    result_dev = AksharamukhaAPI.hk_to_devanagari(test_hk)
    if result_dev:
        print(f"✓ {test_hk} → {result_dev}")
    else:
        print(f"✗ {test_hk} → API failed")


if __name__ == '__main__':
    test_transliteration()
