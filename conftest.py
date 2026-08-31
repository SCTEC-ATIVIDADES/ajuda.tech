import os

import pytest

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ajuda_tech.settings")


@pytest.fixture(autouse=True)
def isolate_catalog(settings):
    settings.CATALOG_API_URL = ""
