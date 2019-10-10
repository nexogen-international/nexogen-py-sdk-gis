#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
NEXOGEN GIS Batch Geocoding
"""

from __future__ import annotations
__version__ = '0.1.0'

from abc import abstractmethod
from typing import Any, Dict

from src.nexogen.aiohttp.batch import AbstractHttpRequestParametersFactory, AbstractHttpResponseAdapter, AsyncBatchHttpRequestExecutor, HttpRequestParameters
from src.nexogen.gis.geopoint import GeoPoint

# constants

URL_GEOCODING: str = 'https://{}/gis/v1/geocode'


class GisBatchGeocodingHttpRequestParametersFactory(AbstractHttpRequestParametersFactory):
    __api_url: str
    __api_key: str
    __provider: str

    def __init__(self, api_url: str, api_key: str, provider: str):
        self.__api_url = URL_GEOCODING.format(api_url)
        self.__api_key = api_key
        self.__provider = provider

    def create_http_request_parameters(self, item: Any) -> HttpRequestParameters:
        headers: Dict[str, str] = {
            'Content-Type': 'application/json', 'Authorization': f'Bearer {self.__api_key}'}
        params: Dict[str, str] = {'address': item,
                                  'provider': self.__provider, 'structured': 'false'}
        return HttpRequestParameters(method='GET', url=self.__api_url, headers=headers, params=params, json=None, timeout=10)


class AbstractGisBatchGeocodingHttpResponseAdapter(AbstractHttpResponseAdapter):

    @abstractmethod
    def on_success(self, idx: int, address: str, point: GeoPoint) -> None:
        pass

    @abstractmethod
    def on_fail(self, idx: int, address: str) -> None:
        pass

    def on_http_response(self, idx: int, request_item: Any, response_json: Dict[str, str]) -> None:
        results = response_json['results']
        if results == []:
            self.on_fail(idx=idx, address=request_item)
        else:
            location = results[0]['centerPoint']
            lat = location['latitude']
            lon = location['longitude']
            self.on_success(idx=idx, address=request_item,
                            point=GeoPoint(lat=lat, lon=lon))
