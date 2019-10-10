#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
NEXOGEN Batch Routing Integration Test
"""

from __future__ import annotations

import logging
import os

import sys
sys.path.append('.')

from src.nexogen.aiohttp.batch import AsyncBatchHttpRequestExecutor, AsyncBatchHttpRequestExecutorSettings
from src.nexogen.asyncio.async_main_wrapper import async_main_wrapper
from src.nexogen.gis.geopoint import GeoPoint
from src.nexogen.gis.batch_routing import GisBatchRoutingHttpRequestParametersFactory, AbstractGisBatchRoutingHttpResponseAdapter

# setting up logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
console = logging.StreamHandler()
logger.addHandler(console)


class _GisBatchRoutingHttpResponseAdapter(AbstractGisBatchRoutingHttpResponseAdapter):

    def on_success(self, idx: int, from_to: (GeoPoint, GeoPoint), distance: float, duration: float) -> None:
        logger.info(
            f'idx:{idx}, distance: {distance/1000.0} [km], duration: {duration} [s]')

    def on_fail(self, idx: int, from_to: (GeoPoint, GeoPoint)) -> None:
        logger.info(f'idx:{idx} failed')


async def main(loop) -> None:
    gis_api_url: str = os.environ.get('NEXOGEN_GIS_API_URL')
    gis_api_key: str = os.environ.get('NEXOGEN_GIS_API_KEY')
    gis_provider: str = os.environ.get('NEXOGEN_GIS_PROVIDER', default='ptv')
    gis_profile: str = os.environ.get(
        'NEXOGEN_GIS_PROFILE', default='Car')
    from_to_1 = (GeoPoint(lat=47.476819, lon=19.038840),
                 GeoPoint(lat=47.474688, lon=19.043840))
    from_to_2 = (GeoPoint(lat=45.0534, lon=3.9696),
                 GeoPoint(lat=54.7733, lon=-1.3643))
    from_to_pairs = [from_to_1, from_to_2] * 100
    http_request_parameters_factory = GisBatchRoutingHttpRequestParametersFactory(
        api_url=gis_api_url, api_key=gis_api_key, provider=gis_provider, profile=gis_profile)
    http_response_adapter = _GisBatchRoutingHttpResponseAdapter()
    async_batch_http_request_executor = AsyncBatchHttpRequestExecutor(
        logger=logger, http_request_parameters_factory=http_request_parameters_factory, http_response_adapter=http_response_adapter)
    async_batch_http_request_executor.settings = AsyncBatchHttpRequestExecutorSettings(
        max_connection=16, main_queue_size=16, dlq_sleep_seconds=3, dlq_consumer_num=2)
    await async_batch_http_request_executor.run(
        loop=loop, itr_items=from_to_pairs, n=len(from_to_pairs))


if __name__ == '__main__':
    async_main_wrapper(main)
