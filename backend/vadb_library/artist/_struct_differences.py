""""These are struct differences. This is just meant for taking notes, don't import this!"""


vadb_create_send = {
	"name": str,
	"status": int,
	"availability": int
}

vadb_create_receive = {
	"code": 200,
	"data": {
		"id": int
	}
}


vadb_edit_send = {
	"name": str,
	"aliases": [
		{
			"name": str
		}, ...
	],
	"status": int,
	"availability": int,
	"description": str,
	"notes": str,
	"avatar": None,
	"banner": None,
	"tracks": int,
	"genre": str,
	"usageRights": [
		{
			"name": str,
			"value": bool
		}, ...
	],
	"socials": [
		{
			"link": str,
			"type": str
		}, ...
	],
}


vadb_get_receive = {
    'code': 200,
    'data': {
        'id': int,
        'name': str,
        'aliases': [
            {
                'name': str
            }, ...
        ],
        'description': str,
        'tracks': int,
        'genre': str,
		'status': int,
		'availability': int,
		'notes': str,
		'usageRights': [
			{
				'name': str,
				'value': bool
			},
			{
				'name': str,
				'value': bool
			}
		],
		'details': {
			'socials': [
				{
					'link': str,
					'type': str
				}, ...
			]
		}
	}
}
