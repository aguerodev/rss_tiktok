# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TikTok RSS is a tool that generates usable RSS feeds from TikTok user accounts using GitHub Actions and GitHub Pages. The project fetches videos from specified TikTok usernames and creates XML RSS feeds that can be consumed by feed readers like Feedly.

## Key Components

- **postprocessing.py**: Main Python script that fetches TikTok videos and generates RSS feeds
- **config.py**: Contains configuration for GitHub Pages URLs
- **subscriptions.csv**: List of TikTok usernames to generate feeds for
- **tiktok.py.patch**: Patch applied to the TikTokApi library to ensure it works properly
- **GitHub Actions Workflow**: Runs the RSS generation process periodically

## Commands

### Running Locally

1. Set up the virtual environment:
```bash
pip install virtualenv
python -m venv venv
source venv/bin/activate  # On Unix/macOS
# Or on Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. Set the MS_TOKEN environment variable (required for TikTok access):
```bash
export MS_TOKEN="your_token_here"  # On Unix/macOS
# Or on Windows: set MS_TOKEN=your_token_here
```

3. Run the feed generation script:
```bash
python postprocessing.py
```

4. To apply the patch to TikTokApi library if needed:
```bash
# First locate the TikTok.py file in your virtualenv
# Then apply the patch
patch /path/to/TikTok.py tiktok.py.patch
```

### Testing

To test if the TikTok API connections work properly, you can use the example script:
```bash
python user_example.py
```

## Architecture

1. **TikTok API Integration**: Uses the unofficial TikTokApi Python library to fetch user videos
2. **Feed Generation**: Converts TikTok video data to RSS XML files using the feedgen library
3. **Image Handling**: Downloads video thumbnails using Playwright
4. **Automated Deployment**: GitHub Actions workflow runs every 4 hours to update feeds
5. **GitHub Pages**: Hosts the generated RSS feeds for public access

## Important Notes

- The MS_TOKEN is critical for accessing TikTok data and must be updated periodically
- The project requires Playwright for capturing screenshots of video thumbnails
- The TikTok API is unofficial and might break with TikTok updates
- Due to TikTok's anti-scraping measures, running with headless=False is required
- GitHub Actions secrets must include MS_TOKEN for automated runs