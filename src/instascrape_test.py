import instascrape

scraper = instascrape.InstagramScraper()

usernames = ["lonepsi", "ragdoll_brotherz", "kendricklamar"]


for username in usernames:

    media = scraper.scrape_user_medias(username, count=10)

    for photo in media:
        print(f"Média ID: {photo['id']}")
        print(f"Propriétaire du média: {photo['owner']['username']}")
        print(f"Description: {photo['caption']}")
        print(f"Nombre de likes: {photo['like_count']}")
        print(f"Date de création: {photo['taken_at_timestamp']}")


