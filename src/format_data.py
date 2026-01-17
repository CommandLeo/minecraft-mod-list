import json
import requests
import sys
import os

base_urls = {
    'modrinth': 'https://modrinth.com/mod/',
    'github': 'https://github.com/'
}

if len(sys.argv) > 1:
    output_path = sys.argv[1]
else:
    output_path = '../README.md'

with open('mod_list.json') as f:
    mod_list_data = json.load(f)

mod_data = {}
output = f'# {mod_list_data['author']} {mod_list_data['version']} Mod List\n\n'
notes_text = ''
notes_index = 1

github_slugs = [x['slug'] for section in mod_list_data['sections'] for x in section['mod_data'] if x['provider'].lower() == 'github']
if github_slugs:
    print('Fetching GitHub data...')
    for slug in github_slugs:
        repo_response = requests.get(f'https://api.github.com/repos/{slug}')
        repo_response.raise_for_status()
        repo_data = repo_response.json()
        branch = repo_data['default_branch']
        fabric_mod_response = requests.get(f'https://raw.githubusercontent.com/{slug}/{branch}/src/main/resources/fabric.mod.json')
        fabric_mod_response.raise_for_status()
        fabric_mod_data = fabric_mod_response.json()
        icon_relative_path = fabric_mod_data.get('icon')

        name = fabric_mod_data.get('name')
        description = fabric_mod_data.get('description') or repo_data.get('description')
        icon_url = f'https://raw.githubusercontent.com/{slug}/{branch}/src/main/resources/{icon_relative_path}' if icon_relative_path else None
        mod_data[slug] = {
            'name': name,
            'description': description,
            'icon_url': icon_url,
        }
    print('Fetched github data')

modrinth_slugs = [x['slug'] for section in mod_list_data['sections'] for x in section['mod_data'] if x['provider'].lower() == 'modrinth']
if modrinth_slugs:
    print('Fetching Modrinth data...')
    projects_response = requests.get('https://api.modrinth.com/v2/projects', params={'ids': json.dumps(modrinth_slugs)})
    projects_response.raise_for_status()
    for mod in projects_response.json():
        slug = mod['slug']
        mod_data[slug] = {
            'id': mod['id'],
            'name': mod['title'],
            'description': mod['description'],
            'icon_url': mod['icon_url'],
        }
    print('Fetched modrinth data')


print('Formatting data...')

with open('HEADER.md') as f:
    output += f.read().strip() + '\n\n'
for section in mod_list_data['sections']:
    output += f'## {section['name']}\n|Icon|Mod|Mod Page|Description\n|---|---|---|---\n'
    for mod in section['mod_data']:
        provider = mod['provider']
        slug = mod['slug']
        data = mod_data.get(slug)
        if data:
            name = mod.get('name') or data.get('name') or slug
            description = mod.get('description') or data.get('description') or ''
            icon_url = mod.get('icon_url') or data.get('icon_url')
            id = data.get('id') or slug

            notes = mod.get('notes')
            if notes and isinstance(notes, list):
                for note in notes:
                    name += f'[^{notes_index}]'
                    notes_text += f'\n[^{notes_index}]: {note}'
                    notes_index += 1
        mod_link = base_urls[provider.lower()] + id
        img = f'<img src="{icon_url}" height=32 width=32>' if icon_url else ''

        output += f'|{img}|{name}|[{provider}]({mod_link})|{description}\n'
    output += '\n'
output += notes_text
output = output.rstrip('\n')

output_dir = os.path.dirname(output_path)
if output_dir:
    os.makedirs(output_dir, exist_ok=True)

with open(output_path, 'w') as f:
    f.write(output)

print(f'Done! Output written to {output_path}')
