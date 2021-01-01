def name_to_query(name, artist):
    modified_name = name.replace(" ", "+")
    modified_artist = artist.replace(" ", "+")
    search_query = "https://www.youtube.com/results?search_query=" + modified_name + "+" + modified_artist
    return search_query