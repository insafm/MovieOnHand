import os
import requests
import re
import libtorrent as lt
import time
import sys
from bs4 import BeautifulSoup
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from urllib.parse import urlparse
from pprint import pprint as pp
from prettytable import PrettyTable
from config import *

class bcolors:
	HEADER = '\033[95m'
	OKBLUE = '\033[94m'
	OKCYAN = '\033[96m'
	OKGREEN = '\033[92m'
	WARNING = '\033[93m'
	FAIL = '\033[91m'
	ENDC = '\033[0m'
	BOLD = '\033[1m'
	UNDERLINE = '\033[4m'

# --------------------------------------------------
# Main class for downloading movie and get info
# --------------------------------------------------
class InsMovie(object):

	movie_page = None
	movie_table = None
	movie_all_list = []

	# Initialize
	def __init__(self):
		
		# Banner
		print(bcolors.OKGREEN + """
		
 ███▄ ▄███▓ ▒█████   ██▒   █▓ ██▓▓█████  ▒█████   ███▄    █  ██░ ██  ▄▄▄       ███▄    █ ▓█████▄ 
▓██▒▀█▀ ██▒▒██▒  ██▒▓██░   █▒▓██▒▓█   ▀ ▒██▒  ██▒ ██ ▀█   █ ▓██░ ██▒▒████▄     ██ ▀█   █ ▒██▀ ██▌
▓██    ▓██░▒██░  ██▒ ▓██  █▒░▒██▒▒███   ▒██░  ██▒▓██  ▀█ ██▒▒██▀▀██░▒██  ▀█▄  ▓██  ▀█ ██▒░██   █▌
▒██    ▒██ ▒██   ██░  ▒██ █░░░██░▒▓█  ▄ ▒██   ██░▓██▒  ▐▌██▒░▓█ ░██ ░██▄▄▄▄██ ▓██▒  ▐▌██▒░▓█▄   ▌
▒██▒   ░██▒░ ████▓▒░   ▒▀█░  ░██░░▒████▒░ ████▓▒░▒██░   ▓██░░▓█▒░██▓ ▓█   ▓██▒▒██░   ▓██░░▒████▓ 
░ ▒░   ░  ░░ ▒░▒░▒░    ░ ▐░  ░▓  ░░ ▒░ ░░ ▒░▒░▒░ ░ ▒░   ▒ ▒  ▒ ░░▒░▒ ▒▒   ▓▒█░░ ▒░   ▒ ▒  ▒▒▓  ▒ 
░  ░      ░  ░ ▒ ▒░    ░ ░░   ▒ ░ ░ ░  ░  ░ ▒ ▒░ ░ ░░   ░ ▒░ ▒ ░▒░ ░  ▒   ▒▒ ░░ ░░   ░ ▒░ ░ ▒  ▒ 
░      ░   ░ ░ ░ ▒       ░░   ▒ ░   ░   ░ ░ ░ ▒     ░   ░ ░  ░  ░░ ░  ░   ▒      ░   ░ ░  ░ ░  ░ 
       ░       ░ ░        ░   ░     ░  ░    ░ ░           ░  ░  ░  ░      ░  ░         ░    ░    
                         ░                                                                ░      """+ bcolors.ENDC)
		
		# Warning message
		print(bcolors.FAIL + bcolors.BOLD + f"\nATTENTION: This experiment is done in Python for educational purpose. I am not responsible for your download of illegal content, pirated files or download without permissions by using this script and it does not offer its own torrent files. There are several risks involved in using the script, including downloading files with viruses and malware and violating copyright laws. Although it's not illegal to share and download torrents, you can be prosecuted if the files are copyrighted. So, avoid this kind of content. Also, use a VPN to use the script because it'll protect you against malware and viruses and hide your identity. Please respect the laws license permits of your country. \n" + bcolors.ENDC)

		option_agree = input("Do you agree? (y|N)? ")
		option_agree = option_agree if option_agree else "N"

		if option_agree.lower() != "y":
			print("Aborting.")
			exit()

		# Shortcuts		# 
		print(bcolors.OKCYAN + bcolors.UNDERLINE + f"\nShortcuts: "+ bcolors.ENDC)
		print(f"Back: b\n")


	"""
	Main class for downloading movie and get info
	"""
	# Get the movie name and details
	def get_movie_details(self, text):
		text = text.encode('utf-8').decode('utf-8').replace(u'\xa0', u' ')

		# Set initial values
		details = {}
		details['movie_name'] = ""
		details['year'] = ""
		details['language'] = self.get_language(text)
		details['type'] = self.get_content_type(text)
		details['quality'] = self.get_quality_type(text)
		details['audio'] = self.get_audio_type(text)
		
		split1 = text.split("- [")
		if len(split1) > 0:
			split2 = split1[0].split("(")
			if len(split2) > 0:

				# Get movie name from split
				details['movie_name'] = split2[0].strip()

				if len(split2) > 1:
					split3 = split2[1].split(") ")
					if len(split3) > 0:
						# Get movie year
						if split3[0].strip().isdigit():
							details['year'] = int(split3[0].strip())
			
		return details
	
	# Get language
	def get_language(self, text):
		text_lower = text.lower()
		lang = ""
		if "tamil" in text_lower:
			lang += "Tamil, "
		if "malayalam" in text_lower:
			lang += "Malayalam, "
		if "english" in text_lower:
			lang += "English, "
		if "hindi" in text_lower:
			lang += "Hindi, "
		if "telug" in text_lower:
			lang += "Telugu, "
		
		if not lang:
			if "tam" in text_lower:
				lang += "Tamil, "
			if "mal" in text_lower:
				lang += "Malayalam, "
			if "eng" in text_lower:
				lang += "English, "
			if "hin" in text_lower:
				lang += "Hindi, "
			if "tel" in text_lower:
				lang += "Telugu, "
		
		return lang.rstrip(', ')

	
	# Get audio type from string
	def get_audio_type(self, text):
		text_lower = text.lower()
		audio_type = ""
		if "aac" in text_lower:
			audio_type += "AAC - "
		if "ddp5.1" in text_lower:
			audio_type += bcolors.OKGREEN + "DDP5.1" + bcolors.ENDC + " - "
		elif "dd5.1" in text_lower:
			audio_type += bcolors.OKGREEN + "DD5.1" + bcolors.ENDC + " - "
		if "hqline" in text_lower.replace(" ", ""):
			audio_type += bcolors.FAIL + "Line Audio" + bcolors.ENDC + " - "
		return audio_type.rstrip(' - ')
	
	# Get quality type from string
	def get_quality_type(self, text):
		text_lower = text.lower()
		quality_type = ""
		if "hq hdrip" in text_lower:
			quality_type += "HQ HDRip - "
		if "hd avc" in text_lower:
			quality_type += bcolors.OKGREEN + "HD AVC"+ bcolors.ENDC + " - "
		if "web-hd" in text_lower:
			quality_type += bcolors.OKGREEN + "WEB-HD"+ bcolors.ENDC + " - "
		if "x264" in text_lower:
			quality_type += "x264 - "
		if "hq hevcrip" in text_lower:
			quality_type += "HQ HEVCRip - "
		if "x265" in text_lower:
			quality_type += "x265 - "
		if "original score" in text_lower:
			quality_type += "Original Score - "
		if "hq predvdrip" in text_lower:
			quality_type += bcolors.FAIL + "HQ PreDVDRip" + bcolors.ENDC + " - "

		return quality_type.rstrip(' - ')
	
	# Get content type like movie or series
	def get_content_type(self, text):
		content_type = "M"
		
		text_1 = text.lower().replace(" ", "")
		if "e(" in text_1 or "ep(" in text_1 or "ep" in text_1:
			content_type = bcolors.WARNING + "S"+ bcolors.ENDC
		
		return content_type
		
	# Get movie links from node
	def get_movie_links(self, soup):
		links = []
		for link in soup.find_all("a"):
			href = link.get('href', None)
			if href:
				if "/topic/" in href:
					_link = {}
					_link['link'] = href
					_link['text'] = link.get_text().strip("[").strip("]")
					size = _link['text'].split(" ")[-1].strip()
					
					# If size not contains valid GB or MB.
					if "GB" not in size and "MB" not in size:
						try:
							size = _link['text'].split(" ")[-3].strip()
						except Exception as e:
							pass
					
					_link['size'] = size
					links.append(_link)
		return links

	# Function for extracting movie page - screenshots and torrent link
	def extract_movie_page(self, page_url):
		page = requests.get(page_url).text
		soup = BeautifulSoup(page, 'html.parser')

		page_info = {}
		page_info['images'] = []
		page_info['torrent_links'] = []
		page_info['magnet_links'] = []
		
		div = soup.find("div", {"class": "cPost_contentWrap"})
		for img in div.find_all("img"):
			img_src = img.get('data-src', None)
			if img_src and not any(x in img_src for x in [".gif", "TB_Torrenticon"]):
				page_info['images'].append(img_src)

		torrent_links = soup.find_all("a", {"class": "ipsAttachLink"})
		for link in torrent_links:
			torrent_link = link.get('href', None)
			if torrent_link:
				page_info['torrent_links'].append(torrent_link)

		magnet_links = soup.find_all("a", {"class": "magnet-plugin"})
		for link in magnet_links:
			magnet_link = link.get('href', None)
			if magnet_link:
				page_info['magnet_links'].append(magnet_link)

		return page_info

	# Download file funcion
	def download_file(self, url, dir):
		print("Downloading: ", url)
		file_name = url.split('/')[-1]
		
		requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
		try:
			r = requests.get(url, stream = True, verify=False, timeout=5) 

			with open(dir + file_name, 'wb') as f: 
				for chunk in r.iter_content(chunk_size = 1024*1024): 
					if chunk: 
						f.write(chunk)
			return dir + file_name
		except Exception as e:
			print(f"ERROR: {str(e)} while downloading: {url}.")

	# Get movie list
	def show_movie_table(self):
		if not self.movie_page:
			self.movie_page = requests.get(BASE_URL).text

		soup = BeautifulSoup(self.movie_page, 'html.parser')

		exclude_string_list = [
			'WE ARE NOW AVAILABLE ON',
			'JOIN FOR LATEST UPDATES',
			'Motion Poster',
			'Look Poster',
			'Teaser',
			'Trailer',
			'Song Promo',
			'BIGG BOSS',
		]

		i = 0
		
		if not self.movie_table:
			self.movie_table = PrettyTable()
			self.movie_table.field_names = ['Sl.No', 'Title', 'Year', 'Languages', 'Type', 'Quality', 'Audio']

			# Align left
			for field in self.movie_table.field_names:
				self.movie_table.align[field] = "l"
			
			find_all = soup.find_all('p')

			for node in find_all:
				text = node.get_text().strip()
				if text:
					# skip if it is in exclude string list or length is less than 40
					if any(x in text for x in exclude_string_list) or len(text) < 40:
						continue
					
					i += 1
					
					movie_details_list = [i]
					movie_detail = self.get_movie_details(text)
					movie_details_list += list(movie_detail.values())
					
					movie_links = self.get_movie_links(node)

					# Saving data for later use
					movie_detail['links'] = movie_links
					movie_detail['extra'] = {
						'title': text,
					}
					self.movie_all_list.append(movie_detail)

					if len(movie_details_list) == len(self.movie_table.field_names):
						self.movie_table.add_row(movie_details_list)
						
				if i >= LIST_LIMIT:
					break

		print(self.movie_table)
		

	# Main executing function
	def run(self):

		# Back selected
		back_selected = True

		while back_selected:
			back_selected = False
			
			# Print table
			self.show_movie_table()

			# Select movie to download
			option_input = input("Enter Number: ")
			
			# Check back selected
			if option_input == "b":
				back_selected = True
				continue

			option = int(option_input) - 1
			if len(self.movie_all_list) >= option:

				print(bcolors.HEADER + f"\n{self.movie_all_list[option]['extra']['title']}" + bcolors.ENDC)

				# IMDB details
				imdb = self.get_imdb(self.movie_all_list[option]["movie_name"], self.movie_all_list[option]["year"])
				if imdb and "imdbID" in imdb and imdb['imdbID']:
					# Print IMDB details
					for key, item in imdb.items():
						print(f"{key}: {item}")
					
					# Open IMDB page
					option_open_imdb = input("Do you wanna open IMDB page? (Y|n)? ")
					option_open_imdb = option_open_imdb if option_open_imdb else "Y"

					# Check back selected
					if option_open_imdb == "b":
						back_selected = True
						continue

					imdb_link = f"https://www.imdb.com/title/{imdb['imdbID']}/"
					if option_open_imdb == "Y":
						os.system('xdg-open "%s"' % imdb_link)
				
				# List available options
				x2= PrettyTable()
				x2.field_names = ['Sl.No', 'File Size', 'Format', 'Page Link']

				for index, item in enumerate(self.movie_all_list[option]['links']):
					x2_rows = [index + 1, item['size'], item['text'], item['link']]
					x2.add_row(x2_rows)
				print(x2)
			
			# Create directory for storing files
			parent_dir = DOWNLOAD_DIR
			dir_name = re.sub(r'[^a-zA-Z0-9]', '', self.movie_all_list[option]['movie_name'])
			path = parent_dir + dir_name + "/"
			if not os.path.exists(path):
				os.makedirs(path)

			# Fetch movie link
			option_input = input("Enter Sl.No: ")
			# Check back selected
			if option_input == "b":
				back_selected = True
				continue

			option2 = int(option_input) - 1
			
			if len(self.movie_all_list[option]['links']) >= option2:
				page_url = self.movie_all_list[option]['links'][option2]['link']
				print("Fetching: ", page_url)
				movie_page = self.extract_movie_page(page_url)
				# pp(movie_page)
				if "images" in movie_page:
					option_ss = input("Do you wanna fetch the screenshots? (Y|n)? ")

					# Check back selected
					if option_ss == "b":
						back_selected = True
						continue

					option_ss = option_ss if option_ss else "Y"

					if option_ss == "Y":
						for file in movie_page['images']:
							image_name = os.path.basename(urlparse(file).path)
							if not os.path.exists(path + image_name):
								self.download_file(file, path)
				
				if option_ss == "Y":
					# Do you wan't open the screenshots?
					option3 = input("Do you wanna show the screenshots? (Y|n)? ")
					option3 = option3 if option3 else "Y"

					if option3 == "Y":
						os.system('xdg-open "%s"' % path)
				

				# Fetch movie link
				option3 = input("Start Torrent Download (Y|n)? ")
				option3 = option3 if option3 else "Y"

				# Check back selected
				if option3 == "b":
					back_selected = True
					continue


				if option3 == "Y":
					torrent_downloaded = False
					# Download usnig torrent file - Not required
					if "torrent_links" in movie_page and movie_page['torrent_links']:
						for file in movie_page['torrent_links']:
							torrent = self.download_file(file, path)
							torrent_downloaded = self.download_torrent(torrent, path)
					else:
						# Download using magnet link now.
						if "magnet_links" in movie_page and movie_page['magnet_links']:
							for torrent in movie_page['magnet_links']:
								torrent_downloaded = self.download_torrent(path, torrent)
					
					if torrent_downloaded:
						# Do you wan't open the downloaded?
						option_open_downloads = input("Do you wanna open the downloads? (Y|n)? ")
						option_open_downloads = option_open_downloads if option_open_downloads else "Y"


						# Check back selected
						if option_open_downloads == "b":
							back_selected = True
							continue

						if option_open_downloads == "Y":
							os.system('xdg-open "%s"' % path)

	# Download from torrent
	def download_torrent(self, torrent, path):
		ses = lt.session({'listen_interfaces': '0.0.0.0:6881'})
		params = {
			'save_path': path,
		}

		h = None
		if "magnet:?" in torrent:
			h = lt.add_magnet_uri(ses, torrent, params)
		else:
			print("torrent: ", torrent)
			params['ti'] = lt.torrent_info(torrent)
			h = ses.add_torrent(params)

		s = h.status()
		print(bcolors.OKGREEN + "Starting Download: "+ bcolors.ENDC + s.name)

		while (not s.is_seeding):
			s = h.status()

			print('\r%.2f%% completed (down: %.1f kB/s up: %.1f kB/s peers: %d) %s' % (
				s.progress * 100, s.download_rate / 1000, s.upload_rate / 1000,
				s.num_peers, s.state), end=' ')

			sys.stdout.flush()
			time.sleep(1)

		print(h.status().name, 'completed.')
		return True
	
	# Get IMDB details
	def get_imdb(self, name, year):
		url = f"http://www.omdbapi.com/?t={name}&y={year}&plot=full&apikey={OMDBAPI_KEY}"
		r = requests.get(url, timeout=5)

		response = r.json()
		return response



ins_movie = InsMovie()
ins_movie.run()