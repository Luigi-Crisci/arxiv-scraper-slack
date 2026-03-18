DIR=/mnt/home.local/desislava.atanasova/git-repos/arxiv-scraper-slack
source $DIR/.venv/bin/activate
source $DIR/secrets.sh
python3 $DIR/archive_scraper.py
