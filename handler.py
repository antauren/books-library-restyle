import requests


def raise_for_status(response):
    response.raise_for_status()

    if response.status_code != 200:
        raise requests.HTTPError(
            'Status code is {} (200 required).'.format(response.status_code)
        )
