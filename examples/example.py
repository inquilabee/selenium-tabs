#!/usr/bin/env python3
"""
Simple example to test seleniumtabs functionality.
Run this file after making changes to verify everything works.
"""

from seleniumtabs import Browser


def main():
    """Run a simple test of the browser functionality."""

    with Browser(
        name="Chrome",
        implicit_wait=10,
        headless=True,
        full_screen=False,  # Set to False to see the browser
    ) as browser:
        # Open a website

        tab = browser.open("https://yahoo.com")

        # Perform some actions
        tab.scroll_down(times=2)


if __name__ == "__main__":
    main()
