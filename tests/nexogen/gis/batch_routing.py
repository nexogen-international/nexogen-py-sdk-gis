#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
NEXOGEN Batch Routing Integration Test
"""

from __future__ import annotations

import itertools
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
file_handler = logging.FileHandler('output.log')
logger.addHandler(console)
logger.addHandler(file_handler)


class _GisBatchRoutingHttpResponseAdapter(AbstractGisBatchRoutingHttpResponseAdapter):

    def __init__(self, num_locations):
        self.num_locations = num_locations

    def on_success(self, idx: int, from_to: (GeoPoint, GeoPoint), distance: float, duration: float) -> None:
        logger.info(
            f'{idx};{idx // self.num_locations};{idx % self.num_locations};{distance};{duration}')

    def on_fail(self, idx: int, from_to: (GeoPoint, GeoPoint)) -> None:
        logger.info(f'idx:{idx} failed')


async def main(loop) -> None:
    gis_api_url: str = os.environ.get('NEXOGEN_GIS_API_URL')
    gis_api_key: str = os.environ.get('NEXOGEN_GIS_API_KEY')
    gis_provider: str = os.environ.get('NEXOGEN_GIS_PROVIDER', default='ptv')
    gis_profile: str = os.environ.get(
        'NEXOGEN_GIS_PROFILE', default='Truck_40t')
    locations = []
    with open('data/batch_routing_locations.csv', encoding='utf-8') as f:
        locations = list(map(lambda location: GeoPoint(lat=float(location[1]), lon=float(location[2])), [line.strip().split(";") for line in f.readlines()]))
    num_locations = len(locations)
    logger.info(f'n: {num_locations}')
    logger.info(f'idx;from;to;distance_in_meters;duration_in_seconds')
    from_to_pairs = list(itertools.product(locations, locations))
    http_request_parameters_factory = GisBatchRoutingHttpRequestParametersFactory(
        api_url=gis_api_url, api_key=gis_api_key, provider=gis_provider, profile=gis_profile)
    http_response_adapter = _GisBatchRoutingHttpResponseAdapter(num_locations)
    async_batch_http_request_executor = AsyncBatchHttpRequestExecutor(
        logger=logger, http_request_parameters_factory=http_request_parameters_factory, http_response_adapter=http_response_adapter)
    async_batch_http_request_executor.settings = AsyncBatchHttpRequestExecutorSettings(
        max_connection=16, main_queue_size=16, dlq_sleep_seconds=3, dlq_consumer_num=2)
    await async_batch_http_request_executor.run(
        loop=loop, itr_items=from_to_pairs, n=len(from_to_pairs))


if __name__ == '__main__':
    async_main_wrapper(main)
