ALLOWED_HOSTS = ["*"]

# Modules in use, commented modules that you won't use
MODULES = [
    'authentication',
    'base',
    'booth',
    'census',
    'graphic',
    'mixnet',
    'postproc',
    'store',
    'visualizer',
    'voting',
    'users',
]
BASEURL = 'http://localhost:8000'
APIS = {
    'authentication': BASEURL,
    'base': BASEURL,
    'booth': BASEURL,
    'census': BASEURL,
    'graphic': BASEURL,
    'mixnet': BASEURL,
    'postproc': BASEURL,
    'store': BASEURL,
    'visualizer': BASEURL,
    'voting': BASEURL,
    'users': BASEURL,
}



DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'decide',
        'USER': 'decide',
        'PASSWORD': 'complexpassword',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}


# SOCIAL AUTH

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id' : secrets['SOCIAL_AUTH_GOOGLE_CLIENT_ID'],
            'secret': secrets['SOCIAL_AUTH_GOOGLE_SECRET'],
            'key': '',
        },
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        },
    },
    'facebook': {
        'APP': {
            'client_id' : secrets['SOCIAL_AUTH_FACEBOOK_KEY'],
            'secret': secrets['SOCIAL_AUTH_FACEBOOK_SECRET'],
            'key': '',
        },
        'METHOD': 'oauth2',
        'SCOPE': ['email', 'public_profile'],
        'AUTH_PARAMS': {'auth_type': 'reauthenticate'},
        'INIT_PARAMS': {'cookie': True},
        'FIELDS': [
            'id',
            'first_name',
            'last_name',
            'middle_name',
            'name',
            'name_format',
            'picture',
            'short_name'
        ],
        'EXCHANGE_TOKEN': True,
        'VERIFIED_EMAIL': False,
        'VERSION': 'v13.0',
    },
    'discord': {
        'APP': {
            'client_id' : secrets['SOCIAL_AUTH_DISCORD_CLIENT_ID'],
            'secret': secrets['SOCIAL_AUTH_DISCORD_SECRET'],
            'key': '',
        },
    },
}

# number of bits for the key, all auths should use the same number of bits
KEYBITS = 256