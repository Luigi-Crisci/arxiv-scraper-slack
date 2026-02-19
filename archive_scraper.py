import os
import time
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET

app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

def get_channel_id_by_name(name):
    """Fetch the channel ID from the name via API"""
    try:
        for result in app.client.conversations_list(types="private_channel"):
            for channel in result["channels"]:
                if channel["name"] == name:
                    return channel["id"]
    except Exception as e:
        print(f"Error fetching channels: {e}")
    return None

def get_arxiv_documents():
    BASE_URL = 'http://export.arxiv.org/api/query?'
    KEYWORDS = [
        'quantum computing',
        "superconducting",
        "quantum annealing",
        "quanrum resevoir",
        "QPU",
        "Analog Computing"] # Add more keywords as needed 

    # Format: YYYYMMDDHHMM
    DAYS_TO_CHECK = 1
    start_date = time.strftime("%Y%m%d%H%M", time.localtime(time.time() - 24*3600*DAYS_TO_CHECK))
    end_date = time.strftime("%Y%m%d%H%M") # Today

    print(start_date)
    
    query_keywords = ' OR '.join([f'all:{kw}' for kw in KEYWORDS])
    query = f'({query_keywords}) AND submittedDate:[{start_date} TO {end_date}]'
    params = {
        'search_query': query,
        'start': 0,
        'max_results': 100,
        'sortBy': 'relevance',
        'sortOrder': 'descending'
    }
    full_url = BASE_URL + urllib.parse.urlencode(params)
    print(full_url)
    try:
        with urllib.request.urlopen(full_url) as response:
            raw_xml = response.read()
            root = ET.fromstring(raw_xml)
            
            # arXiv uses the Atom namespace
            ns = {'atom': 'http://www.w3.org/2005/Atom'}
            
            entries = root.findall('atom:entry', ns)
            
            if not entries:
                print("No new papers found in that timeframe.")
                return []
            else:
                print(f"Found {len(entries)} papers matching the criteria.")

            results = []
            for entry in entries:
                title = entry.find('atom:title', ns).text.strip().replace('\n', ' ')
                link = entry.find('atom:id', ns).text
                author_elements = entry.findall('atom:author', ns)
                authors = []
                for auth in author_elements:
                    name = auth.find('atom:name', ns).text
                    authors.append(name)
                
                author_string = ", ".join(authors)
                results.append(f"*{title}*\nAuthors: {author_string}\nLink: {link}")
 
            return results

    except Exception as e:
        print(f"Error fetching from arXiv: {e}")
        return [] 


def post_arxiv_updates():
    CHANNEL_NAME = "arxiv-papers"  # To be filled with the actual channel name where you want to post updates

    channel_id = get_channel_id_by_name(CHANNEL_NAME)
    if not channel_id:
        print(f"Channel '{CHANNEL_NAME}' not found. Please create it and try again.")
        return
    
    documents = get_arxiv_documents()
    if not documents:
        app.client.chat_postMessage(channel=channel_id, text="No new papers found.")
        return
	
    today = time.strftime("%d/%m/%Y")
    app.client.chat_postMessage(channel=channel_id, text=f"*{today}: Found {len(documents)} new papers.*")
    for doc in documents:
        app.client.chat_postMessage(channel=channel_id, text=doc)

if __name__ == "__main__":  
    post_arxiv_updates()
