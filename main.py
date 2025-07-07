import argparse
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from tqdm import tqdm  # For progress bars

from input_handler import process_input
from model_client import ModelClient
from quality_checker import evaluate_listing


def generate_batch_listings(details_list, sold_listings, max_workers=4, min_score=70):
    """Generate multiple listings in parallel with quality control"""
    results = []
    successful = 0
    failed = 0

    print(f"Starting batch generation with {max_workers} workers...")

    def process_single(details):
        try:
            client = ModelClient()
            processed = process_input(details)
            result = client.generate_listing(processed, sold_listings)

            # Apply quality check
            quality = evaluate_listing(result)
            result["quality_score"] = quality["score"]
            result["suggestions"] = quality["suggestions"]

            # Track item details for reporting
            result["item_details"] = details

            # If score is below threshold, regenerate once
            if quality["score"] < min_score:
                print(f"Low quality score ({quality['score']}), regenerating {details.get('model', 'item')}...")
                result = client.generate_listing(processed, sold_listings, temperature=0.8)
                quality = evaluate_listing(result)
                result["quality_score"] = quality["score"]
                result["suggestions"] = quality["suggestions"]
                result["item_details"] = details

            return result
        except Exception as e:
            print(f"Error processing {details.get('model', 'item')}: {e}")
            return None

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(process_single, item) for item in details_list]

        # Track progress with tqdm
        for future in tqdm(futures, desc="Generating listings"):
            try:
                result = future.result()
                if result:
                    results.append(result)
                    successful += 1
                else:
                    failed += 1
            except Exception as e:
                print(f"Future execution failed: {e}")
                failed += 1

    print(f"Batch generation completed: {successful} successful, {failed} failed")

    # Sort by quality score
    results.sort(key=lambda x: x["quality_score"], reverse=True)
    return results


def display_listing(result, index=None):
    """Format and display a single listing with quality metrics"""
    title = "=== GENERATED LISTING " + (f"#{index + 1} " if index is not None else "") + "==="
    print(f"\n{title}")

    if "item_details" in result:
        details = result["item_details"]
        print(f"Item: {details.get('brand', '')} {details.get('model', '')} ({details.get('condition', '')})")

    print(f"Title: {result['title']}")
    print(f"\nDescription:\n{result['description']}")
    print(f"\nPrice Range: {result['price_range']}")

    # Display quality metrics
    if "quality_score" in result:
        print(f"\nQuality Score: {result['quality_score']}/100")

    if "suggestions" in result and result["suggestions"]:
        print("Improvement Suggestions:")
        for suggestion in result["suggestions"]:
            print(f"- {suggestion}")


def export_results(results, format="txt"):
    """Export results to file"""
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filename = f"ebay_listings_{timestamp}.{format}"

    with open(filename, "w") as f:
        for i, result in enumerate(results):
            f.write(f"=== LISTING #{i + 1} ===\n")
            f.write(f"Title: {result['title']}\n")
            f.write(f"Description: {result['description']}\n")
            f.write(f"Price Range: {result['price_range']}\n")
            f.write(f"Quality Score: {result.get('quality_score', 'N/A')}/100\n")
            f.write("\n\n")

    print(f"Results exported to {filename}")
    return filename


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="eBay Listing Generator")
    parser.add_argument("--batch", action="store_true", help="Run in batch mode")
    parser.add_argument("--workers", type=int, default=4, help="Number of workers for batch processing")
    parser.add_argument("--export", action="store_true", help="Export results to file")
    parser.add_argument("--min-score", type=int, default=70, help="Minimum quality score (0-100)")
    parser.add_argument("--temperature", type=float, default=0.7, help="Model temperature (0.1-1.0)")
    args = parser.parse_args()

    # Common sold listings data
    sold_listings = [
        "Similar item sold for $15 (New)",
        "Used version sold for $8-10",
        "Limited edition variant sold for $25"
    ]

    if args.batch:
        # Batch processing example
        details_list = [
            {
                'brand': 'Example Brand',
                'model': 'Model A',
                'condition': 'New',
                'notes': 'Sample notes'
            },
            {
                'brand': 'Another Brand',
                'model': 'Model B',
                'condition': 'Used',
                'notes': 'Light wear'
            },
            {
                'brand': 'Premium Brand',
                'model': 'Pro Model C',
                'condition': 'New',
                'variant': 'Limited Edition',
                'notes': 'Collector\'s item, original packaging'
            }
        ]

        try:
            results = generate_batch_listings(
                details_list,
                sold_listings,
                max_workers=args.workers,
                min_score=args.min_score
            )

            # Display results
            print(f"\nGenerated {len(results)} listings:")
            for i, result in enumerate(results):
                display_listing(result, i)

            # Export if requested
            if args.export and results:
                export_results(results)

        except Exception as e:
            print(f"Batch processing error: {e}")
            sys.exit(1)
    else:
        # Single item processing
        details = {
            'brand': 'Example Brand',
            'model': 'Example Model',
            'condition': 'New',
            'notes': 'Sample notes'
        }

        try:
            print("Starting up AI Agent...")
            processed_input = process_input(details)
            client = ModelClient()
            result = client.generate_listing(
                processed_input,
                sold_listings,
                temperature=args.temperature
            )

            if not result["title"] or not result["description"]:
                print("Warning: Generated listing is incomplete")

            # Apply quality check
            quality = evaluate_listing(result)
            result["quality_score"] = quality["score"]
            result["suggestions"] = quality["suggestions"]

            # Display the result
            display_listing(result)

            # Export if requested
            if args.export:
                export_results([result])

        except ValueError as e:
            print(f"Input error: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"Unexpected error: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()