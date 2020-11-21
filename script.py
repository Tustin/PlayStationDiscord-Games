import sys, os, requests, re, json, urllib.request, urllib.error, hashlib, hmac, traceback, logging, shutil, yaml
from pytablewriter import MarkdownTableWriter

# key for tdmb link generation (from ps3, ps4)
tmdb_key = bytearray.fromhex('F5DE66D2680E255B2DF79E74F890EBF349262F618BCAE2A9ACCDEE5156CE8DF2CDF2D48C71173CDC2594465B87405D197CF1AED3B7E9671EEB56CA6753C2E6B0')

titles = []

ps5_titles_url = 'https://m.np.playstation.com/api/graphql/v1/op?operationName=categoryGridRetrieve&variables={"id":"d71e8e6d-0940-4e03-bd02-404fc7d31a31","pageArgs":{"size":100,"offset":0}}&extensions={"persistedQuery":{"version":1,"sha256Hash":"45ca7c832b785ad8455869e92f9f40a8bdbf04cb7a87a215455649ebf0c884b0"}}'

print('checking games.yml for custom titles...')
with open('games.yml', 'r') as game_reader:
	try:
		titles = yaml.safe_load(game_reader)
	except yaml.YAMLError as exc:
		print(exc)
		exit()

def create_url(title_id):
	hash = hmac.new(tmdb_key, bytes(title_id, 'utf-8'), hashlib.sha1)
	return f'https://tmdb.np.dl.playstation.net/tmdb2/{title_id}_{hash.hexdigest().upper()}/{title_id}.json'

def grep_title_id(sku):
	match = re.search(r'([A-Z]{4}[0-9]{5}_00)', sku)

	return match.group(1) if match else None

if __name__ == '__main__':
	log = logging.getLogger(__name__)
	handler = logging.StreamHandler(sys.stdout)
	handler.setFormatter(logging.Formatter('[%(asctime)s] %(message)s'))
	handler.setLevel(logging.INFO)
	log.addHandler(handler)
	log.setLevel(logging.INFO)
	discord_title_ids = []

	done = {k: [] for k in titles}

	table_writer = None

	if os.path.isfile('README.template'):
		table_writer = MarkdownTableWriter()
		table_writer.headers = ["Icon", "Title"]
		table_writer.value_matrix = []
	else:
		 print('missing README.template. wont update README.md file.')

	
	for platform in titles:
		# Remove the platform image folder if it exists.
		if os.path.exists(platform):
			shutil.rmtree(platform)
		
		os.mkdir(platform)

		# If we are dealing with PS5, for now let's just grab every PS5 title
		# Mostly because there's very few of them atm, but also I don't have a way to pull title data from title id yet.
		if platform == 'ps5':
			content = requests.get(ps5_titles_url).json()

			for title in content['data']['categoryGridRetrieve']['products']:
				if title['storeDisplayClassification'] != 'FULL_GAME':
					continue

				name = title['name']
				image = None
				for media in title['media']:
					if media['role'] != 'MASTER':
						continue
					image = media['url']
					break
				
				if image == None:
					print('no image found for title', name)

				title_id = grep_title_id(title['id'])
				
				if title_id == None:
					print('unable to grep title_id from sku', name)
					continue
				
				done[platform].append({
					"name": name,
					"titleId": title_id
				})

				icon_file = f'{platform}/{title_id}.png'

				if table_writer != None:
					table_writer.value_matrix.append([
						f'<img src="{icon_file}?raw=true" width="100" height="100">',
						name
					])

				if os.path.exists(icon_file):
					print('\ticon file exists')
					continue

				urllib.request.urlretrieve(image, icon_file)

		elif platform == 'ps4':
			for title_id in titles[platform]:
				url = create_url(title_id)
				print(url)
				content = requests.get(url)

				if content.status_code != 200:
					print('skipping', title_id)
					continue
				try:
					content = content.json()
				except ValueError:
					continue
				
				game_name = content['names'][0]['name']
				
				print(game_name)

				if not content['icons'] or len(content['icons']) == 0:
					print('\tno icons')
					continue

				game_icon = None

				for icon in content['icons']:
					if icon['type'] == '512x512':
						game_icon = icon['icon']
						break
				
				if game_icon == None:
					print('\tno 512x512 icon')
					continue

				done[platform].append({
					"name": game_name,
					"titleId": title_id
				})

				if not os.path.exists(platform):
					os.mkdir(platform)

				icon_file = f'{platform}/{title_id}.png'

				if table_writer != None:
					table_writer.value_matrix.append([
						f'<img src="{icon_file}?raw=true" width="100" height="100">',
						game_name
					])

				if os.path.exists(icon_file):
					print('\ticon file exists')
					continue

				urllib.request.urlretrieve(game_icon, icon_file)
				
				print('\tsaved')
	
	if table_writer != None:
		with open("README.template", "rt") as template:
			with open('README.md', 'wt', encoding='utf-8') as readme:
				for line in template:
					readme.write(line.replace('!!games!!', table_writer.dumps()))
	
	with open('games.json', 'w') as games_file:
		json.dump(done, games_file)