import sqlalchemy
import insert_data

db = 'postgresql://lesson2:lesson2@localhost:5432/Lesson3'
engine = sqlalchemy.create_engine(db)
connection = engine.connect()


def get_id(cell_name, table_name, cell_key, key_word):
    return connection.execute(f'''SELECT {cell_name} FROM {table_name} 
                                                WHERE {cell_key}='{key_word}'
                                            ''').fetchall()


def cell_is_exist(name_cell, table_name, cell_key, addition=None):
    if addition is None:
        return connection.execute(f'''SELECT {name_cell} FROM {table_name}
                                                WHERE {name_cell}= '{cell_key}'
                                            ''').fetchall()
    else:
        return connection.execute(f'''SELECT {name_cell} FROM {table_name}
                                                WHERE {name_cell}= '{cell_key}'
                                                AND {addition}
                                            ''').fetchall()


def insert_info(table_name, cell_list, value_insert, type='info'):
    if type == 'info':
        value = f"'{value_insert}'"
    else:
        value = value_insert
    connection.execute(f'''INSERT INTO {table_name}({cell_list})
                           VALUES({value.lower()});
                    ''')


def fill_one_cell_table(list_format, table_name, key_cell):
    for elem_of_list in list_format.split(','):
        if not cell_is_exist(key_cell, table_name, elem_of_list):
            insert_info(table_name, key_cell, elem_of_list)
    return connection.execute(f'''SELECT * FROM {table_name}
                ''').fetchall()


def fill_album_table(dict):
    for key in dict.keys():
        for name in dict[key].keys():
            if not cell_is_exist('Name', 'Albums', name.lower()):
                value_insert = f"'{name}', {dict[key][name]}"
                insert_info('Albums', 'Name, PublishedYear', value_insert, type='text')
    return connection.execute(f'''SELECT * FROM Albums
                ''').fetchall()


def fill_song_table(dict):
    for album in dict.keys():
        album_id = get_id('Id', 'Albums', 'Name', album.lower())[0][0]
        for song_name in dict[album].keys():
            if not cell_is_exist('Name', 'Songs', song_name, f'AlbumId = {album_id}'):
                value_insert = f"'{song_name}', {dict[album][song_name]},{album_id}"
                insert_info('Songs', 'Name, Length, AlbumId', value_insert, type='text')
    return connection.execute(f'''SELECT * FROM Songs
                ''').fetchall()


def fill_style_table(dict):
    for style in dict:
        if not cell_is_exist('Name', 'Collection', style, f'PublishedYear = {dict[style]}'):
            insert_info('Collection', 'Name,PublishedYear', f"'{style}',{dict[style]}", type='text')
    return connection.execute(f'''SELECT * FROM Collection
                ''').fetchall()


def is_list(dict):
    if isinstance(dict, list):
        return dict
    else:
        return dict.keys()


def fill_table_to_table(dict, table_result, table_name1, table_name2, cell_table1, cell_table2):
    for key in dict.keys():
        first_id = get_id('Id', table_name1, 'Name', key.lower())[0][0]
        for value in is_list(dict[key]):
            second_id = get_id('Id', table_name2, 'Name', value.lower())[0][0]
            if not cell_is_exist(cell_table1, table_result, first_id, f'{cell_table2} = {second_id}'):
                connection.execute(f'''INSERT INTO {table_result}({cell_table1},{cell_table2})
                                       VALUES({first_id},{second_id});
                                       ''')
    return connection.execute(f'''SELECT * FROM {table_result}
                ''').fetchall()


def purge_all():
    clean_table('SongCollection')
    clean_table('ArtistsAlbum')
    clean_table('ArtistsGenres')
    clean_table('Collection')
    clean_table('Songs')
    clean_table('Albums')
    clean_table('Genres')
    clean_table('Artists')


def clean_table(table_name):
    connection.execute(f'''DELETE FROM {table_name}''')


if __name__ == '__main__':
    purge_all()
    print(fill_one_cell_table(insert_data.artist_list, 'Artists', 'Name'))
    print(fill_one_cell_table(insert_data.genres_list, 'Genres', 'Name'))
    print(fill_album_table(insert_data.album_dict))
    print(fill_song_table(insert_data.songs_dict))
    print(fill_style_table(insert_data.collection_dict))
    print(fill_table_to_table(
        insert_data.artist_to_genres,
        'ArtistsGenres',
        'Artists',
        'Genres',
        'ArtistId',
        'GenresId'
    ))
    print(fill_table_to_table(
        insert_data.album_dict,
        'ArtistsAlbum',
        'Artists',
        'Albums',
        'ArtistId',
        'AlbumId'
    ))
    print(fill_table_to_table(
        insert_data.collection_to_song_dict,
        'SongCollection',
        'Songs',
        'Collection',
        'SongId',
        'CollectionId'))
