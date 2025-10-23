# Copyright (c) 2024, Sourav Singh and contributors
# For license information, please see license.txt

"""
Command Line Interface for Frappe Postman Sync
"""

import argparse


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Frappe Postman Sync - Automatically generate and sync CRUD APIs to Postman"
    )

    parser.add_argument(
        "--version", action="version", version="frappe_postman_sync 1.0.0"
    )

    parser.add_argument(
        "--help-more", action="help", help="Show detailed help information"
    )

    # Parse arguments
    parser.parse_args()

    print("Frappe Postman Sync CLI")
    print("This is a Frappe app. Use 'bench' commands to interact with it.")
    print("Available commands:")
    print("  bench --site <site> migrate")
    print("  bench --site <site> console")
    print(
        "  bench --site <site> execute frappe_postman_sync.api.postman_sync.sync_to_postman"
    )


if __name__ == "__main__":
    main()
