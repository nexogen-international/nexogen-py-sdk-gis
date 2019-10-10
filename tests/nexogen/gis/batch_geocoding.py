#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
NEXOGEN Batch Geocoding Integration Test
"""

from __future__ import annotations

import logging
import os

import sys
sys.path.append('.')

from src.nexogen.aiohttp.batch import AsyncBatchHttpRequestExecutor
from src.nexogen.asyncio.async_main_wrapper import async_main_wrapper
from src.nexogen.gis.geopoint import GeoPoint
from src.nexogen.gis.batch_geocoding import GisBatchGeocodingHttpRequestParametersFactory, AbstractGisBatchGeocodingHttpResponseAdapter

# setting up logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
console = logging.StreamHandler()
logger.addHandler(console)

class _GisBatchGeocodingHttpResponseAdapter(AbstractGisBatchGeocodingHttpResponseAdapter):

    def on_success(self, idx: int, address: str, point: GeoPoint) -> None:
        logger.info(f'idx:{idx}, lat: {point.lat}, lon: {point.lon}')

    def on_fail(self, idx: int, address: str) -> None:
        logger.info(f'idx:{idx} failed')


async def main(loop) -> None:
    gis_api_url: str = os.environ.get('NEXOGEN_GIS_API_URL')
    gis_api_key: str = os.environ.get('NEXOGEN_GIS_API_KEY')
    gis_provider: str = os.environ.get('NEXOGEN_GIS_PROVIDER', default='ptv')
    addresses = ['1118 Budapest, Torbágy utca 8',
                 '1112 Budapest, Menyecske utca 27']
    http_request_parameters_factory = GisBatchGeocodingHttpRequestParametersFactory(
        api_url=gis_api_url, api_key=gis_api_key, provider=gis_provider)
    http_response_adapter = _GisBatchGeocodingHttpResponseAdapter()
    async_batch_http_request_executor = AsyncBatchHttpRequestExecutor(
        logger=logger, http_request_parameters_factory=http_request_parameters_factory, http_response_adapter=http_response_adapter)
    await async_batch_http_request_executor.run(loop=loop,
                                                itr_items=addresses, n=len(addresses))


if __name__ == '__main__':
    async_main_wrapper(main)
