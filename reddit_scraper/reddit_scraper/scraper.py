import praw
import json
import csv
import time
import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from mdutils import MdUtils
from prawcore.exceptions import OAuthException, ResponseException

from .config import config

logger = logging.getLogger('reddit_scraper')

class RedditScraper:
    """Reddit scraper with multiple output format support"""
    
    def __init__(self):
        """Initialize Reddit API connection"""
        self.reddit = self._create_reddit_instance()
        
    def _create_reddit_instance(self) -> praw.Reddit:
        """Create and return authenticated Reddit instance"""
        try:
            reddit = praw.Reddit(
                client_id=config.get('reddit.client_id'),
                client_secret=config.get('reddit.client_secret'),
                username=config.get('reddit.username'),
                password=config.get('reddit.password'),
                user_agent=config.get('reddit.user_agent')
            )
            # Verify authentication
            reddit.user.me()
            logger.info("Successfully authenticated with Reddit API")
            return reddit
        except Exception as e:
            logger.error(f"Failed to create Reddit instance: {str(e)}")
            raise

    def _sanitize_filename(self, title: str, post_id: str, max_length: int = 100) -> str:
        """Convert title to a Linux-friendly filename"""
        # Convert to lowercase and replace spaces with underscores
        filename = title.lower().replace(' ', '_')
        
        # Remove special characters except underscores and hyphens
        filename = re.sub(r'[^a-z0-9_-]', '', filename)
        
        # Replace multiple underscores with a single one
        filename = re.sub(r'_+', '_', filename)
        
        # Truncate if too long, leaving room for post_id and extension
        max_base_length = max_length - len(post_id) - 2  # -2 for the hyphen and potential truncation
        if len(filename) > max_base_length:
            filename = filename[:max_base_length].rstrip('_')
        
        # Add post_id for uniqueness
        filename = f"{filename}-{post_id}"
        
        return filename

    def scrape_post(self, post_id: str) -> Optional[Dict[str, Any]]:
        """Scrape a Reddit post and its comments"""
        try:
            submission = self.reddit.submission(id=post_id)
            submission.comments.replace_more(limit=None)
            
            data = {
                "title": submission.title,
                "author": str(submission.author),
                "content": submission.selftext,
                "url": submission.url,
                "score": submission.score,
                "upvote_ratio": submission.upvote_ratio,
                "created_utc": submission.created_utc,
                "num_comments": submission.num_comments,
                "permalink": submission.permalink,
                "comments": []
            }
            
            logger.info(f"Scraping post: {submission.title}")
            for comment in submission.comments:
                comment_data = self._extract_comment(comment)
                if comment_data:
                    data["comments"].append(comment_data)
            
            return data
        except Exception as e:
            logger.error(f"Error scraping post {post_id}: {str(e)}")
            return None

    def _extract_comment(self, comment) -> Optional[Dict[str, Any]]:
        """Extract comment data including replies"""
        try:
            return {
                "author": str(comment.author),
                "body": comment.body,
                "score": comment.score,
                "created_utc": comment.created_utc,
                "edited": comment.edited,
                "is_submitter": comment.is_submitter,
                "replies": [
                    self._extract_comment(reply)
                    for reply in comment.replies
                    if hasattr(reply, 'author')  # Skip MoreComments objects
                ]
            }
        except Exception as e:
            logger.error(f"Error extracting comment: {str(e)}")
            return None

    def save_to_markdown(self, data: Dict[str, Any], output_path: Path) -> Path:
        """Save post data to Markdown format"""
        try:
            # Create filename from post title
            filename = self._sanitize_filename(data["title"], output_path.name.split('_')[-1])
            output_path = output_path.parent / f"{filename}.md"
            
            # Create markdown content
            md = MdUtils(file_name=str(output_path.with_suffix('')))  # Remove .md as MdUtils adds it
            
            # Post Header
            md.new_header(level=1, title=data["title"])
            
            # Post Metadata
            md.new_line(f"**Author**: u/{data['author']}")
            md.new_line(f"**Score**: {data['score']} (Upvote Ratio: {data['upvote_ratio']*100:.0f}%)")
            md.new_line(f"**URL**: {data['url']}")
            created_time = datetime.fromtimestamp(data['created_utc']).strftime('%Y-%m-%d %H:%M:%S UTC')
            md.new_line(f"**Created**: {created_time}")
            md.new_line(f"**Permalink**: https://reddit.com{data['permalink']}")
            md.new_line()
            
            # Post Content
            if data["content"]:
                md.new_header(level=2, title="Content")
                md.new_line(data["content"])
                md.new_line()
            
            # Comments Section
            md.new_header(level=2, title=f"Comments ({data['num_comments']})")
            for comment in data["comments"]:
                if comment:  # Skip any None comments
                    self._add_comment_to_markdown(md, comment)
            
            md.create_md_file()
            logger.info(f"Saved Markdown file to: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error saving to markdown: {str(e)}")
            raise

    def _add_comment_to_markdown(self, md: MdUtils, comment: Dict[str, Any], depth: int = 0) -> None:
        """Add a comment and its replies to the markdown file"""
        try:
            indent = "  " * depth
            created_time = datetime.fromtimestamp(comment['created_utc']).strftime('%Y-%m-%d %H:%M:%S UTC')
            author_prefix = "**[OP]** " if comment.get('is_submitter') else ""
            
            md.new_line(f"{indent}- {author_prefix}**u/{comment['author']}** ({comment['score']} points) - {created_time}")
            md.new_line(f"{indent}  {comment['body'].replace(chr(10), chr(10) + indent + '  ')}")
            
            if comment.get('edited'):
                edit_time = datetime.fromtimestamp(comment['edited']).strftime('%Y-%m-%d %H:%M:%S UTC')
                md.new_line(f"{indent}  *(edited: {edit_time})*")
            
            for reply in comment["replies"]:
                if reply:  # Skip any None replies
                    self._add_comment_to_markdown(md, reply, depth + 1)
                    
        except Exception as e:
            logger.error(f"Error adding comment to markdown: {str(e)}")

    def save_to_json(self, data: Dict[str, Any], output_path: Path) -> Path:
        """Save post data to JSON format"""
        try:
            # Create filename from post title
            filename = self._sanitize_filename(data["title"], output_path.name.split('_')[-1])
            output_path = output_path.parent / f"{filename}.json"
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved JSON file to: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Error saving to JSON: {str(e)}")
            raise

    def save_to_csv(self, data: Dict[str, Any], output_path: Path) -> Path:
        """Save post data to CSV format (flattened structure)"""
        try:
            # Create filename from post title
            filename = self._sanitize_filename(data["title"], output_path.name.split('_')[-1])
            output_path = output_path.parent / f"{filename}.csv"
            
            comments = self._flatten_comments(data["comments"])
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=[
                    "comment_id", "parent_id", "author", "body", "score",
                    "created_utc", "edited", "is_submitter", "depth"
                ])
                writer.writeheader()
                writer.writerows(comments)
                
            logger.info(f"Saved CSV file to: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Error saving to CSV: {str(e)}")
            raise

    def _flatten_comments(self, comments: List[Dict[str, Any]], parent_id: str = None, depth: int = 0) -> List[Dict[str, Any]]:
        """Flatten nested comments structure for CSV output"""
        flattened = []
        for i, comment in enumerate(comments):
            if comment:
                comment_id = f"c{len(flattened)}"
                flat_comment = {
                    "comment_id": comment_id,
                    "parent_id": parent_id,
                    "author": comment["author"],
                    "body": comment["body"],
                    "score": comment["score"],
                    "created_utc": comment["created_utc"],
                    "edited": comment["edited"],
                    "is_submitter": comment["is_submitter"],
                    "depth": depth
                }
                flattened.append(flat_comment)
                
                # Process replies
                flattened.extend(self._flatten_comments(
                    comment["replies"], parent_id=comment_id, depth=depth + 1
                ))
        
        return flattened

    def scrape_subreddit(self, subreddit_name: str, limit: int = 10, time_filter: str = 'day') -> None:
        """Scrape top posts from a subreddit"""
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            logger.info(f"Scraping top {limit} posts from r/{subreddit_name} for time period: {time_filter}")
            
            for submission in subreddit.top(time_filter=time_filter, limit=limit):
                data = self.scrape_post(submission.id)
                if data:
                    output_path = config.get_output_dir() / f"reddit_post_{submission.id}"
                    self.save_to_markdown(data, output_path)
                    time.sleep(2)  # Rate limiting
                    
        except Exception as e:
            logger.error(f"Error scraping subreddit {subreddit_name}: {str(e)}")
            raise