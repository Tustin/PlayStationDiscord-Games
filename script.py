import sys, os, requests, re, json, urllib.request, hashlib, hmac
from pytablewriter import MarkdownTableWriter

# key for tdmb link generation (from ps3, ps4)
tmdb_key = bytearray.fromhex('F5DE66D2680E255B2DF79E74F890EBF349262F618BCAE2A9ACCDEE5156CE8DF2CDF2D48C71173CDC2594465B87405D197CF1AED3B7E9671EEB56CA6753C2E6B0')

title_ids = [
    'CUSA07022_00', # Fortnite
    'CUSA05042_00', # Destiny 2
    'CUSA11100_00', # Black Ops 4
    'CUSA05969_00', # WWII
    'CUSA04762_00', # Infinite Warfare
    'CUSA03522_00', # Modern Warfare Remastered
    'CUSA02290_00', # Black Ops 3
    'CUSA00803_00', # Advanced Warfare
    'CUSA00018_00', # Ghosts
]

urls = [
    # Top 50 Games
    "https://store.playstation.com/valkyrie-api/en/US/19/container/STORE-MSF77008-TOPGAMES?size=200&bucket=games&start=0&gameContentType=games&platform=ps4",
    # PS+ Games
    "https://store.playstation.com/valkyrie-api/en/US/19/container/STORE-MSF77008-PSPLUSFREEGAMES?size=30&bucket=games&start=0&platform=ps4",
    # Top 50 digital only games
    "https://store.playstation.com/valkyrie-api/en/US/19/container/STORE-MSF77008-TOPPSNGAMES?size=50&bucket=games&start=0&platform=ps4",
    # 10 newest free games
    "https://store.playstation.com/valkyrie-api/en/US/19/container/STORE-MSF77008-GAMESFREETOPLAY?sort=release_date&direction=desc&size=10&bucket=games&start=0&platform=ps4",
    # Newest games this month
    "https://store.playstation.com/valkyrie-api/en/US/19/container/STORE-MSF77008-NEWTHISMONTH?game_content_type=games&size=100&bucket=games&start=0&platform=ps4",
    # Coming soon
    "https://store.playstation.com/valkyrie-api/en/US/19/container/STORE-MSF77008-PS3PSNPREORDERS?gameContentType=games&gameType=ps4_full_games%2Cpsn_games&releaseDate=coming_soon%2Clast_30_days&platform=ps4"
]


def create_url(title_id):
    hash = hmac.new(tmdb_key, bytes(title_id, 'utf-8'), hashlib.sha1)
    return f'https://tmdb.np.dl.playstation.net/tmdb2/{title_id}_{hash.hexdigest().upper()}/{title_id}.json'


if __name__ == '__main__':

    done = {"ps4": []}
    table_writer = None

    if os.path.isfile('README.template'):
        table_writer = MarkdownTableWriter()
        table_writer.headers = ["Icon", "Title"]
        table_writer.value_matrix = []
    else:
         print('missing README.template. wont update README.md file.')

    for url in urls:
        print(f'--- {url} ---')
        content = requests.get(url).json()

        for item in content['included']:
            info = item['attributes']
            
            if 'thumbnail-url-base' not in info:
                continue

            if 'game' not in str(info['game-content-type']).lower():
                continue

            print(info['name'])

            rating = info['star-rating']
            if not rating['total']:
                print('\tno ratings')
                continue

            if rating['total'] < 10 or rating['score'] < 4:
                print('\tfailed rating check')
                continue

            match = re.search(r'([A-Z]{4}[0-9]{5}_00)', info['default-sku-id'])

            if not match:
                print('\tfailed regex check')
                continue
            
            title_id = match.group(1)

            if title_id not in title_ids:
                title_ids.append(title_id)
                print('\tadded to list')
            else:
                print('\talready added')

    # added all the titleIds... now get their images
    for title_id in title_ids:
        url = create_url(title_id)
        content = requests.get(url)

        if content.status_code != 200:
            print('skipping', title_id)
            continue

        content = content.json()
        
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

        done["ps4"].append({
            "name": game_name,
            "titleId": title_id
        })

        image_dir = 'ps4'

        if not os.path.exists(image_dir):
            os.mkdir(image_dir)

        icon_file = f'{image_dir}/{title_id}.png'

        if table_writer != None:
            table_writer.value_matrix.append([
                f'<img src="{icon_file}?raw=true" width="100" height="100">',
                game_name
            ])

        if os.path.exists(icon_file):
            print('\ticon file exists')
            continue

        urllib.request.urlretrieve(game_icon, icon_file)
        
        print('\tgood')
    
    if table_writer != None:
        with open("README.template", "rt") as template:
            with open('README.md', 'wt', encoding='utf-8') as readme:
                for line in template:
                    readme.write(line.replace('!!games!!', table_writer.dumps()))
    
    with open('games.json', 'w') as games_file:
       json.dump(done, games_file)
