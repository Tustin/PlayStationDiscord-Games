import json, os, base64, shutil, urllib.error
from discord_assets import get_assets, add_asset, delete_asset

with open('games.json') as games_file:  
    game_data = json.load(games_file)
    if len(game_data) == 0:
        print('no games saved')
        exit(1)
    
    # sort all the supported games title ids from the games.json file 
    supported_games_title_ids = set(n['titleId'].lower() for n in game_data['ps4'])

    print('found %d supported games in games.json' % len(supported_games_title_ids))

    discord_assets = get_assets()
    discord_asset_names = set(n['name'] for n in discord_assets if n['name'] != 'ps4_main') # dont remove the main icon
    print('found %d discord assets' % len(discord_assets))
    if len(discord_assets) > 0:
        # games that have a discord asset that are no longer supported by this repo
        removed_games = [ i for i in discord_asset_names if i not in supported_games_title_ids ]
        if len(removed_games) > 0:
            print('removing %d games' % len(removed_games))
            for game in removed_games:
                asset_id = next(i for i in discord_assets if i['name'] == game)['id']
                try:
                    delete_asset(asset_id)
                    print('deleted %s' % asset_id)
                except:
                    print('failed deleting %s' % asset_id)
        else:
            print('no games need to be removed')
    else:
        print('no discord assets found so none were removed')

    # games that are now supported that don't exist in the discord application
    added_games = [ i for i in supported_games_title_ids if i not in discord_asset_names ]
    if len(added_games) > 0:
        print('adding %d games...' % len(added_games))
        for game in added_games:
            try:
                with open(f'ps4/{game}.png', "rb") as image_file:
                    try:
                        encoded_string = base64.b64encode(image_file.read())
                        add_asset(game, 'data:image/png;base64,%s' % encoded_string.decode("utf-8"))
                        print('added %s' % game)
                    except HTTPError:
                        print('request failed while trying to add %s' % game)
            except:
                print('failed to open file %s.png' % game)
                
    else:
        print('no new games added')
