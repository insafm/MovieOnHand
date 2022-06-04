import os
from matplotlib.style import available
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from bs4 import BeautifulSoup
from unidecode import unidecode
from pprint import pprint as pp
from prettytable import PrettyTable
import re


base_url = 'https://tamilblasters.lol/'

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

class InsMovie(object):

	# Get the movie name and details
	def get_movie_details(self, text):
		
		# TODO: Column for video type(Movie, series, trailor)
		# TODO: Movie certificate type
		# TODO: Get trailor link
		# TODO: Get IMDB rating
		
		# Set initial values
		details = {}
		details['movie_name'] = "N/A"
		details['year'] = "N/A"
		details['language'] = "N/A"
		details['quality'] = "N/A"
		details['audio'] = "N/A"
		
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
						
						if len(split3) > 1:
							split4_lang_type = split3[1].split(" ", 1)
							if len(split4_lang_type) > 0:
								if len(split4_lang_type[0]) > 3:
									# Get movie language
									details['language'] = split4_lang_type[0].strip()
								
								# Get movie quality
								if len(split4_lang_type) > 1:
									if len(split4_lang_type[1]) > 3 and len(split4_lang_type[1]) < 30:
										details['quality'] = split4_lang_type[1].strip()

				if len(split2) > 2:
					# Get audio type
					split5_audio = split2[2].split(")", 1)
					if len(split5_audio) > 0:
						details['audio'] = split5_audio[0].strip()

		return details

	# Get movie links from node
	def get_movie_links(self, soup):
		links = []
		for link in soup.find_all("a"):
			href = link.get('href', None)
			if href:
				if "/topic/" in href:
					_link = {}
					_link['link'] = href
					_link['text'] = unidecode(link.get_text()).strip("[").strip("]")
					_link['size'] = _link['text'].split(" ")[-1].strip()
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
		with open(file_name, 'wb') as f:
			requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

			r = requests.get(url, stream = True, verify=False) 

			with open(dir + file_name, 'wb') as f: 
				for chunk in r.iter_content(chunk_size = 1024*1024): 
					if chunk: 
						f.write(chunk)               

	# Main executing function
	def run(self):
		page = requests.get(base_url).text
		soup = BeautifulSoup(page, 'html.parser')

		exclude_string_list = [
			'WE ARE NOW AVAILABLE ON',
			'JOIN FOR LATEST UPDATES',
		]

		i = 0
		
		# TODO: Table style formating
		x = PrettyTable()
		x.field_names = ['Sl.No', 'Title', 'Year', 'Language', 'Quality', 'Audio', 'Available Sizes']
		
		all_list = []
		
		for node in soup.find_all('p'):
			text = unidecode(node.get_text()).strip()
			if text:
				# skip if it is in exclude string list or length is less than 40
				if any(x in text for x in exclude_string_list) or len(text) < 40:
					continue
				
				i += 1
				
				movie_details_list = [i]
				# print(bcolors.OKGREEN + text + bcolors.ENDC)
				movie_detail = self.get_movie_details(text)
				movie_details_list += list(movie_detail.values())
				
				movie_links = self.get_movie_links(node)
				movie_links_size_list = [item['size'] for item in movie_links]
				movie_links_size_list = " - ".join(movie_links_size_list)
				movie_details_list.append(movie_links_size_list)

				# Saving data for later use
				movie_detail['links'] = movie_links
				all_list.append(movie_detail)

				# pp(movie_details_list)

				if len(movie_details_list) == len(x.field_names):
					x.add_row(movie_details_list)
					
			if i >= 20:
				break
		
		print(x)

		# Select movie to download
		option = int(input("Enter Movie Number: ")) - 1
		if len(all_list) >= option:

			# List available options
			x2= PrettyTable()
			x2.field_names = ['Sl.No', 'File Size', 'Format', 'Page Link']

			for index, item in enumerate(all_list[option]['links']):
				x2_rows = [index + 1, item['size'], item['text'], item['link']]
				x2.add_row(x2_rows)
			print(x2)
		
		# Create directory for storing files
		dir_name = res = re.sub(r'[^a-zA-Z0-9]', '', all_list[option]['movie_name']) + "/"
		if not os.path.exists(dir_name):
			os.makedirs(dir_name)

		# Fetch movie link
		option2 = int(input("Enter Sl.No To Fetch Link: ")) - 1
		if len(all_list[option]['links']) >= option2:
			page_url = all_list[option]['links'][option2]['link']
			print("Fetching: ", page_url)
			movie_page = self.extract_movie_page(page_url)
			pp(movie_page)
			if "images" in movie_page:
				for file in movie_page['images']:
					self.download_file(file, dir_name)
			
			# Fetch movie link
			option3 = input("Start Torrent Download (Y | n)?")
			option3 = option3 if option3 else "Y"

			if option3 == "Y":
				# Download usnig torrent file - Not required
				# if "torrent_links" in movie_page:
				# 	for file in movie_page['torrent_links']:
				# 		self.download_file(file, dir_name)
				# Download using magnet link now.
				if "magnet_links" in movie_page:
					for link in movie_page['magnet_links']:
						# TODO: Download from torrent directly
						os.system("xdg-open '" + link + "'")

ins_movie = InsMovie()
ins_movie.run()