from utils import setup_logging, create_directories
from crawler import KansasBusinessCrawler

def main():
    """Main function to run the crawler"""
    # Setup
    setup_logging()
    create_directories()
    
    # Initialize and run crawler
    crawler = KansasBusinessCrawler()
    
    try:
        success = crawler.run_crawler()
        if success:
            print("Crawling completed successfully!")
        else:
            print("Crawling completed with errors. Check logs for details.")
    except KeyboardInterrupt:
        print("\nCrawling interrupted by user")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        crawler.close()

if __name__ == "__main__":
    main()