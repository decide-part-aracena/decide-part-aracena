#Email SMTP SECRETS
EMAIL_HOST_PASSWORD = 'Ask the secrets administator to get secrets keys'

# SOCIAL AUTH SECRETS
SOCIAL_AUTH_DISCORD_CLIENT_ID = 'Ask the secrets administator to get secrets keys'
SOCIAL_AUTH_DISCORD_SECRET = 'Ask the secrets administator to get secrets keys'
SOCIAL_AUTH_FACEBOOK_KEY = 'Ask the secrets administator to get secrets keys'
SOCIAL_AUTH_FACEBOOK_SECRET = 'Ask the secrets administator to get secrets keys'
SOCIAL_AUTH_GOOGLE_CLIENT_ID = 'Ask the secrets administator to get secrets keys'
SOCIAL_AUTH_GOOGLE_SECRET = 'Ask the secrets administator to get secrets keys'

#Email SMTP
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp-mail.outlook.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'decide.part.aracena@outlook.com'


# SOCIAL AUTH
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id' : SOCIAL_AUTH_GOOGLE_CLIENT_ID,
            'secret': SOCIAL_AUTH_GOOGLE_SECRET,
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
            'client_id' : SOCIAL_AUTH_FACEBOOK_KEY,
            'secret': SOCIAL_AUTH_FACEBOOK_SECRET,
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
            'client_id' : SOCIAL_AUTH_DISCORD_CLIENT_ID,
            'secret': SOCIAL_AUTH_DISCORD_SECRET,
            'key': '',
        },
    },
}