dataFormat = {
    "userInfo": {
        "id": "UserId",
    },
    "artistInfo": {
        "proof": "png",
        "vadbpage": "https://fadb.live/",
        "data": {
            "id": None,
            "name": "ArtistName",
            "aliases": [
                {
                    "name": "Alias"
                }
            ],
            "avatar": "AvatarLink",
            "banner": "BannerLink, Optional",
            "description": "Description",
            "tracks": 1, #AmountOfTracks, int
            "genre": "Genre",
            "status": 0,
                # 0: Completed
                # 1: No contact
                # 2: Pending
                # 3: Requested
                # 99: nil
            "availability": 0,
                # 0: Verified
                # 1: Disallowed
                # 2: Contact required
                # 3: Varies
                # 99: nil
            "notes": "Notes, Optional",
            "usageRights": [
                {
                    "name": "NameOfAllowedSong",
                    "value": True
                },
                {
                    "name": "NameOfDisallowedSong",
                    "value": False
                }
            ],
            "socials": [
                { 
                    "url": "funnyurl",
                    "type": "type"
                },
                {
                    "url": "anotherfunnyurl",
                    "type": "type"
                }
            ],
            "notes": "text"
        }
    }
}