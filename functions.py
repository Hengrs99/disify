import time

def name_to_query(name, artist):
    modified_name = name.replace(" ", "+")
    modified_artist = artist.replace(" ", "+")
    search_query = "https://www.youtube.com/results?search_query=" + modified_name + "+" + modified_artist
    return search_query


def read_tmp():
    if tmp_exists():
        with open("tmp.txt", "r") as f:
            content = f.readline()

    else:
        content = "Not Generated"
        time.sleep(1)
        read_tmp()

    return content
        

def tmp_exists():
    try:
        f = open("tmp.txt")
        f.close()
        return True

    except FileNotFoundError:
        return False
