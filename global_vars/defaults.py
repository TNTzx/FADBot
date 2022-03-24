"""Where defaults for the Firebase Database reside."""

import global_vars.variables as vrs


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
            "adminRole": 0,
            "logs": {
                "locations": {
                    "dump": firebase.PLACEHOLDER_DATA,
                    "live": firebase.PLACEHOLDER_DATA
                }
            }
        }
    }
}
