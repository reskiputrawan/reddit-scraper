import praw
import os
from dotenv import load_dotenv
from mdutils import MdUtils
import time
from prawcore.exceptions import OAuthException, ResponseException

# Load environment variables
load_dotenv()

def create_reddit_instance():
    """Create and return a Reddit instance with proper authentication"""
    try:
        reddit = praw.Reddit(
            client_id=os.getenv('REDDIT_CLIENT_ID'),
            client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
            username=os.getenv('REDDIT_USERNAME'),
            password=os.getenv('REDDIT_PASSWORD'),
            user_agent=os.getenv('REDDIT_USER_AGENT')
        )
        return reddit
    except Exception as e:
        print(f"Error creating Reddit instance: {str(e)}")
        return None

def scrape_post(reddit, post_id):
    """Scrape a Reddit post and its comments"""
    try:
        submission = reddit.submission(id=post_id)
        submission.comments.replace_more(limit=None)  # Load all comments
        
        data = {
            "title": submission.title,
            "author": str(submission.author),
            "content": submission.selftext,
            "url": submission.url,
            "score": submission.score,
            "upvote_ratio": submission.upvote_ratio,
            "created_utc": submission.created_utc,
            "comments": []
        }
        
        for comment in submission.comments:
            data["comments"].append(extract_comment(comment))
        
        return data
    except Exception as e:
        print(f"Error scraping post: {str(e)}")
        return None

def extract_comment(comment):
    """Extract comment data including replies"""
    try:
        return {
            "author": str(comment.author),
            "body": comment.body,
            "score": comment.score,
            "created_utc": comment.created_utc,
            "replies": [extract_comment(reply) for reply in comment.replies]
        }
    except Exception as e:
        print(f"Error extracting comment: {str(e)}")
        return None

def save_to_markdown(data, filename):
    """Convert post data to Markdown format and save to file"""
    try:
        md = MdUtils(file_name=filename)
        
        # Post Header
        md.new_header(level=1, title=data["title"])
        
        # Post Metadata
        md.new_line(f"**Author**: u/{data['author']}")
        md.new_line(f"**Score**: {data['score']} (Upvote Ratio: {data['upvote_ratio']*100:.0f}%)")
        md.new_line(f"**URL**: {data['url']}")
        md.new_line(f"**Created**: {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(data['created_utc']))}")
        md.new_line()
        
        # Post Content
        if data["content"]:
            md.new_header(level=2, title="Content")
            md.new_line(data["content"])
            md.new_line()
        
        # Comments Section
        md.new_header(level=2, title="Comments")
        for comment in data["comments"]:
            if comment:  # Skip any None comments
                add_comment(md, comment)
        
        md.create_md_file()
        print(f"Successfully saved to {filename}.md")
        return True
    except Exception as e:
        print(f"Error saving to markdown: {str(e)}")
        return False

def add_comment(md, comment, depth=0):
    """Add a comment and its replies to the markdown file"""
    try:
        indent = "  " * depth
        created_time = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(comment['created_utc']))
        md.new_line(f"{indent}- **u/{comment['author']}** ({comment['score']} points) - {created_time}")
        md.new_line(f"{indent}  {comment['body'].replace(chr(10), chr(10) + indent + '  ')}")
        
        for reply in comment["replies"]:
            if reply:  # Skip any None replies
                add_comment(md, reply, depth + 1)
    except Exception as e:
        print(f"Error adding comment: {str(e)}")

def main():
    # Initialize Reddit instance
    reddit = create_reddit_instance()
    if not reddit:
        return
    
    # Example usage with a post ID
    try:
        # Get post ID from user
        post_url = input("Enter Reddit post URL: ")
        
        # Extract post ID from URL
        if "reddit.com" in post_url:
            post_id = post_url.split("/comments/")[1].split("/")[0]
        else:
            post_id = post_url  # Assume direct ID was provided
        
        print(f"Scraping post {post_id}...")
        
        # Scrape post data
        post_data = scrape_post(reddit, post_id)
        if not post_data:
            return
        
        # Save to markdown
        output_file = f"reddit_post_{post_id}"
        save_to_markdown(post_data, output_file)
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()