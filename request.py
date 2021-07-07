import sqlalchemy


def get_genres_data():
    # количество исполнителей в каждом жанре;
    request_data = connection.execute('''SELECT g.name, COUNT(art.name) FROM Artists art
                                    LEFT JOIN ArtistsGenres artgen ON artgen.artistid = art.id
                                    LEFT JOIN Genres g ON g.id = artgen.genresid
                                    GROUP BY g.name
                                    ORDER BY COUNT(art.name) DESC                                    
        ''').fetchall()
    result_line = 'Список жанров по количеству исполнителей:\n'
    for request in request_data:
        result_line += f'{request[0].capitalize()}: {request[1]}\n'

    return result_line


def get_tracks_between(year):
    # количество треков, вошедших в альбомы 2019-2020 годов;
    request_data = connection.execute(f'''SELECT COUNT(s.name) FROM SONGS s
                                         LEFT JOIN Albums al ON al.id = s.albumid
                                         WHERE al.publishedyear BETWEEN {year[0]} AND {year[1]}
    ''').fetchall()[0][0]
    result_line = f'Количество треков выпущенных с {year[0]} по {year[1]}: {request_data}\n'

    return result_line


def get_mid_treck_length():
    # средняя продолжительность треков по каждому альбому;
    request_data = connection.execute(f'''SELECT al.Name,AVG(s.length) FROM SONGS s
                                         LEFT JOIN Albums al ON al.id = s.albumid
                                         GROUP BY al.name
    ''').fetchall()
    result_line = 'Средняя продолжительность треков по каждому альбому\n'
    for data in request_data:
        result_line += f'{data[0].capitalize()}: {round(data[1])} секунд \n'

    return result_line


def get_artists_not_in(year):
    # все исполнители, которые не выпустили альбомы в 2020 году;
    request_data = connection.execute(f'''SELECT art.name FROM Artists art
                                             LEFT JOIN ArtistsAlbum aral ON aral.artistid = art.id    
                                             LEFT JOIN Albums al ON al.id = aral.albumid
                                             WHERE al.publishedyear <> {year}
                                             GROUP BY art.name                                             
                                             ''').fetchall()
    result_line = f'Dсе исполнители, которые не выпустили альбомы в {year} году\n'
    for data in request_data:
        result_line += f'{data[0].capitalize()}\n'

    return result_line


def get_album_by_artist(name):
    # названия сборников, в которых присутствует конкретный исполнитель (выберите сами);
    request_data = connection.execute(f'''SELECT al.name FROM Albums al
                                             LEFT JOIN ArtistsAlbum aral ON al.id = aral.albumid    
                                             LEFT JOIN Artists art ON aral.artistid = art.id 
                                             WHERE art.name = '{name.lower()}'                         
                                             ''').fetchall()
    result_line = f'Названия сборников, в которых присутствует исполнитель {name}\n'
    for data in request_data:
        result_line += f'{data[0].capitalize()}\n'

    return result_line


def get_album_of_multigenres():
    # название альбомов, в которых присутствуют исполнители более 1 жанра;
    request_data = connection.execute(f'''SELECT al.name, art.name FROM Albums al
                                             LEFT JOIN ArtistsAlbum aral ON al.id = aral.albumid    
                                             LEFT JOIN Artists art ON aral.artistid = art.id 
                                             LEFT JOIN ArtistsGenres artgen ON artgen.artistid = art.id
                                             LEFT JOIN Genres gen ON gen.id = artgen.genresid
                                             GROUP BY al.name,art.name
                                             HAVING COUNT(gen.name) > 1                                       
                                             ''').fetchall()
    result_line = f'название альбомов, в которых присутствуют исполнители более 1 жанра:\n'

    for data in request_data:
        result_line += f'альбом {data[0].capitalize()} от исполнителя {data[1].capitalize()}\n'

    return result_line


def get_song_not_into_collection():
    # наименование треков, которые не входят в сборники
    request_data = connection.execute(f'''SELECT s.name FROM Songs s
                                                 LEFT JOIN SongCollection scl ON scl.songid = s.id    
                                                 LEFT JOIN Collection cl ON cl.id = scl.collectionid 
                                                 GROUP BY s.name
                                                 HAVING COUNT(cl.name) = 0                                       
                                                 ''').fetchall()
    result_line = f'ннаименование треков, которые не входят в сборники:\n'
    for data in request_data:
        result_line += f'трек: {data[0].capitalize()}\n'

    return result_line


def get_shortest_song():
    # исполнителя(-ей), написавшего самый короткий по продолжительности трек
    # (теоретически таких треков может быть несколько);
    request_data = connection.execute('''SELECT DISTINCT art.name FROM Artists art
                                        LEFT JOIN ArtistsAlbum aral ON art.id = aral.artistid
                                        LEFT JOIN Albums al ON aral.albumid = al.id
                                        GROUP BY art.name,al.id
                                        HAVING al.id IN (
                                            SELECT albumid FROM Songs as s
                                            WHERE s.length = (
                                                SELECT MIN(Songs.length) FROM Songs))
                                            ''').fetchall()

    result_line = f'исполнитель(И), написавший(ие) самый короткий ' \
                  f'по продолжительности трек:\n'
    for data in request_data:
        result_line += f'исполнитель: {data[0].capitalize()}\n'

    return result_line

def get_album_with_mincount():
    # название альбомов, содержащих наименьшее количество треков.
    request_data = connection.execute('''SELECT al.name, COUNT(sg.name) FROM Albums al
                                            LEFT JOIN SONGS sg ON sg.albumid = al.id
                                            GROUP BY al.name
                                            HAVING COUNT(sg.name) = (                                      
                                                SELECT MIN(qty) FROM (
                                                SELECT COUNT(s.name) qty FROM Albums alb
                                                LEFT JOIN SONGS s ON s.albumid = alb.id
                                                GROUP BY alb.name
                                                ) MinValue
                                                )                                                                                                         
                                        ''').fetchall()

    result_line = f'название альбомов, содержащих наименьшее количество треков\n'
    for data in request_data:
        result_line += f'Альбом: {data[0].capitalize()}\n'

    return result_line




if __name__ == '__main__':
    db = 'postgresql://lesson2:lesson2@localhost:5432/Lesson3'
    engine = sqlalchemy.create_engine(db)
    connection = engine.connect()

    print(get_genres_data())
    print(get_tracks_between([2019, 2020]))
    print(get_mid_treck_length())
    print(get_artists_not_in(2020))
    print(get_album_by_artist('Slipknot'))
    print(get_album_of_multigenres())
    print(get_song_not_into_collection())
    print(get_shortest_song())
    print(get_album_with_mincount())
