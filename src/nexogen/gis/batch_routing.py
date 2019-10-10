#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
NEXOGEN GIS Batch Routing
"""

from __future__ import annotations
__version__ = '0.1.0'

from abc import abstractmethod
from typing import Any, Dict

from src.nexogen.aiohttp.batch import AbstractHttpRequestParametersFactory, AbstractHttpResponseAdapter, AsyncBatchHttpRequestExecutor, HttpRequestParameters
from src.nexogen.gis.geopoint import GeoPoint

# constants

URL_ROUTING: str = 'https://{}/gis/v1/routing/direct'


class GisBatchRoutingHttpRequestParametersFactory(AbstractHttpRequestParametersFactory):
    __api_url: str
    __api_key: str
    __provider: str
    __profile: str

    def __init__(self, api_url: str, api_key: str, provider: str, profile: str):
        self.__api_url = URL_ROUTING.format(api_url)
        self.__api_key = api_key
        self.__provider = provider
        self.__profile = profile

    def create_http_request_parameters(self, item: (GeoPoint, GeoPoint)) -> HttpRequestParameters:
        headers: Dict[str, str] = {
            'Content-Type': 'application/json', 'Authorization': f'Bearer {self.__api_key}'}
        body: Dict[str, str] = {'from': {'latitude': item[0].lat, 'longitude': item[0].lon},
                                'to': {'latitude': item[1].lat, 'longitude': item[1].lon},
                                'vehicleProfile': self.__profile,
                                'provider': self.__provider, 'requiredResults': ['Distance', 'Duration']}
        return HttpRequestParameters(method='POST', url=self.__api_url, headers=headers, params=None, json=body, timeout=60)


class AbstractGisBatchRoutingHttpResponseAdapter(AbstractHttpResponseAdapter):

    @abstractmethod
    def on_success(self, idx: int, from_to: (GeoPoint, GeoPoint), distance: float, duration: float) -> None:
        pass

    @abstractmethod
    def on_fail(self, idx: int, from_to: (GeoPoint, GeoPoint)) -> None:
        pass

    def on_http_response(self, idx: int, request_item: Any, response_json: Dict[str, str]) -> None:
        try:
            distance = response_json['distance']['distance']
            duration = response_json['duration']['duration']
            self.on_success(
                idx=idx, from_to=request_item, distance=distance, duration=duration)
        except Exception:
            self.on_fail(idx=idx, from_to=request_item)
