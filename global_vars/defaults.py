"""Where defaults for the Firebase Database reside."""

import backend.firebase as firebase


default = {
    "artistData": {
        "pending": {
            "artists": {
                "artist": "test"
            }
        }
    },
    "guildData": {
        "guildId": {
            "admin_role": 0,
            "logs": {
                "locations": {
                    "dump": firebase.PLACEHOLDER_DATA,
                    "live": firebase.PLACEHOLDER_DATA
                }
            }
        }
    }
}
