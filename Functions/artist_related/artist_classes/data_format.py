"""Module that contains the data format."""

data_format = {
    "userInfo": {
        "id": "UserId",
    },
    "artistInfo": {
        "name": "ArtistName",
        "proof": "png",

        "vadb_info": {
            "artist_id": None,
            "page": "https://fadb.live/"
        },


        "states": {
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
            "usage_rights": [
                {
                    "name": "NameOfAllowedSong",
                    "value": True
                },
                {
                    "name": "NameOfDisallowedSong",
                    "value": False
                }
            ],
        },
        
        "details": {
            "description": "Description",
            "notes": "Notes, Optional",

            "aliases": [{"name": "Alias"}],

            "images": {
                "avatar_url": "AvatarLink",
                "banner_url": "BannerLink, Optional"
            },

            "music_info": {
                "tracks": 1, #AmountOfTracks, int
                "genre": "Genre",
            },
            
            "socials": [
                {
                    "link": "funnyurl",
                    "type": "type"
                },
                {
                    "link": "anotherfunnyurl",
                    "type": "type"
                }
            ],
        }
    }
}

# pylint: disable=line-too-long

# beans = {
#     "data": {
#         "id":18,
#         "name":"TheFatRat",
#         "aliases":[{"name":"ThisIsTheFatRat"}],
#         "description":"rat fat",
#         "tracks":72,
#         "genre":"EDM",
#         "status":0,
#         "availability":3,
#         "notes":"",
#         "usageRights":[
#             {"name":"All songs","value":true},
#             {"name":"Remixes","value":false}
#         ],
#         "details":{
#             "avatarUrl":"https://yt3.ggpht.com/ytc/AKedOLT6GLh1dxDmW0xOlox2a_wbxA7YPA0AGuXk6F3YHQ=s88-c-k-c0x00ffffff-no-rj",
#             "bannerUrl":"",
#             "socials":[
#                 {"link":"https://www.youtube.com/channel/UCa_UMppcMsHIzb5LDx1u9zQ","type":"youtube"},
#                 {"link":"https://www.facebook.com/thisisthefatrat","type":"facebook"},
#                 {"link":"https://open.spotify.com/artist/3OKg7YbOIatODzkRIbLJR4","type":"spotify"},
#                 {"link":"https://music.apple.com/artist/thefatrat/395664545","type":"itunes"},
#                 {"link":"https://twitter.com/ThisIsTheFatRat","type":"twitter"}
#             ]}}}
