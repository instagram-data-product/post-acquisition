import instascrape

# Création d'un objet scrapeur
scraper = instascrape.InstagramScraper()

# Liste des noms d'utilisateur des profils que vous souhaitez récupérer
usernames = ["lonepsi", "ragdoll_brotherz", "kendricklamar"]

# Boucle sur chaque nom d'utilisateur
for username in usernames:
    # Récupération des informations sur les dernières photos publiées par l'utilisateur
    media = scraper.scrape_user_medias(username, count=10)

    # Boucle sur chaque photo
    for photo in media:
        # Affichage des informations sur la photo
        print(f"Média ID: {photo['id']}")
        print(f"Propriétaire du média: {photo['owner']['username']}")
        print(f"Description: {photo['caption']}")
        print(f"Nombre de likes: {photo['like_count']}")
        print(f"Date de création: {photo['taken_at_timestamp']}")

