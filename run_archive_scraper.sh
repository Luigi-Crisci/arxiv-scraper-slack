DIR=/home/luigi-ph3/arxiv-scraper-slack/
source $DIR/.venv/bin/activate
source $DIR/secrets.sh
python3 $DIR/archive_scraper.py
