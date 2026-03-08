from datetime import timedelta

DOMAIN = "mantova_ambiente"
PLATFORMS = ["sensor"]

CONF_ZONE_ID = "zone_id"
CONF_ZONE_TITLE = "zone_title"
CONF_INSTANCE_NAME = "instance_name"

DEFAULT_NAME = "Mantova Ambiente"
API_BASE_URL = "https://www.mantovaambiente.it"
ZONE_LOOKUP_PATH = "/api/zones"
RECYCLINGS_PATH = "/api/recyclings"

UPDATE_INTERVAL = timedelta(hours=6)
