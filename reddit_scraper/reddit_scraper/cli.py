import click
import logging
from pathlib import Path
from rich.console import Console
from rich.logging import RichHandler
from rich.progress import Progress, SpinnerColumn, TextColumn
from typing import Optional

from .config import config
from .scraper import RedditScraper

# Set up rich console for beautiful output
console = Console()

def setup_logging():
    """Configure logging with rich handler"""
    logging.basicConfig(
        level=config.get('logging.level', 'INFO'),
        format="%(message)s",
        datefmt="[%X]",
        handlers=[
            RichHandler(console=console, rich_tracebacks=True),
            logging.FileHandler(config.get_log_dir() / 'reddit_scraper.log')
        ]
    )
    return logging.getLogger('reddit_scraper')

logger = setup_logging()

def validate_url(ctx, param, value):
    """Validate and extract post ID from Reddit URL"""
    if value is None:
        return None
    
    try:
        if 'reddit.com' in value:
            post_id = value.split('/comments/')[1].split('/')[0]
        else:
            post_id = value  # Assume direct ID was provided
        return post_id
    except Exception as e:
        raise click.BadParameter(f'Invalid Reddit URL or post ID: {str(e)}')

@click.group()
@click.version_option(version='0.1.0')
def cli():
    """Reddit Scraper - Download Reddit posts and comments in Markdown format"""
    pass

@cli.command()
@click.option('-u', '--url', callback=validate_url, help='Reddit post URL or ID to scrape')
@click.option('-o', '--output', type=click.Path(), help='Output directory (overrides config)')
@click.option('--format', type=click.Choice(['markdown', 'json', 'csv']), default='markdown',
              help='Output format')
def scrape(url: str, output: Optional[str], format: str):
    """Scrape a Reddit post and save it to file"""
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            # Initialize scraper
            progress.add_task("Initializing Reddit API...", total=None)
            scraper = RedditScraper()
            
            # Set output directory
            if output:
                output_dir = Path(output)
            else:
                output_dir = config.get_output_dir()
            
            # Scrape post
            progress.add_task(f"Scraping post {url}...", total=None)
            result = scraper.scrape_post(url)
            
            if result:
                # Save to file
                base_path = output_dir / f"reddit_post_{url}"
                progress.add_task(f"Saving to {format} format...", total=None)
                
                # Save file and get actual output path
                if format == 'markdown':
                    actual_path = scraper.save_to_markdown(result, base_path)
                elif format == 'json':
                    actual_path = scraper.save_to_json(result, base_path)
                else:  # csv
                    actual_path = scraper.save_to_csv(result, base_path)
                
                console.print(f"\n[green]Successfully saved to: {actual_path}[/green]")
            else:
                console.print("\n[red]Failed to scrape post[/red]")
                
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        console.print(f"\n[red]Error: {str(e)}[/red]")
        raise click.Abort()

@cli.command()
@click.option('-s', '--subreddit', required=True, help='Subreddit name to scrape')
@click.option('-n', '--number', default=10, help='Number of posts to scrape')
@click.option('-t', '--time', type=click.Choice(['hour', 'day', 'week', 'month', 'year', 'all']),
              default='day', help='Time period for top posts')
def subreddit(subreddit: str, number: int, time: str):
    """Scrape top posts from a subreddit"""
    try:
        scraper = RedditScraper()
        scraper.scrape_subreddit(subreddit, limit=number, time_filter=time)
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        console.print(f"\n[red]Error: {str(e)}[/red]")
        raise click.Abort()

@cli.command()
def configure():
    """Configure Reddit Scraper settings"""
    try:
        # Show current configuration
        console.print("\n[bold]Current Configuration:[/bold]")
        console.print(config.config)
        
        # TODO: Add interactive configuration editing
        console.print("\n[yellow]Interactive configuration editing coming soon![/yellow]")
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        console.print(f"\n[red]Error: {str(e)}[/red]")
        raise click.Abort()

def main():
    """Main entry point for the CLI"""
    try:
        cli()
    except Exception as e:
        logger.error(f"Unhandled error: {str(e)}", exc_info=True)
        console.print(f"\n[red]Unhandled error: {str(e)}[/red]")
        raise click.Abort()

if __name__ == '__main__':
    main()