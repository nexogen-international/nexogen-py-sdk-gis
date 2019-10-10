#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
NEXOGEN AIOHTTP Batch HackerNews API test
"""

from __future__ import annotations
from typing import Any, Dict, List

import logging

import sys
sys.path.append('.')

from src.nexogen.aiohttp.batch import AbstractHttpRequestParametersFactory, AbstractHttpResponseAdapter, AsyncBatchHttpRequestExecutor, HttpRequestParameters
from src.nexogen.asyncio.async_main_wrapper import async_main_wrapper

# setting up logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
console = logging.StreamHandler()
logger.addHandler(console)

# constants

URL_GET_POST: str = 'https://hacker-news.firebaseio.com/v0/item/{}.json'


class HackerNewsHttpRequestParametersFactory(AbstractHttpRequestParametersFactory):
    def create_http_request_parameters(self, request_item: Any) -> HttpRequestParameters:
        url: str = URL_GET_POST.format(request_item)
        headers: Dict[str, str] = {
            'Content-Type': 'application/json', 'Authorization': f'Bearer '}
        return HttpRequestParameters(method='GET', url=url, headers=headers, params=None, json=None, timeout=10)


class HackerNewsHttpResponseAdapter(AbstractHttpResponseAdapter):
    __responses: List[Any] = []

    @property
    def responses(self):
        return self.__responses

    def on_http_response(self, idx: int, request_item: Any, response_json: Dict[str, str]):
        self.__responses.append(response_json)


async def main(loop) -> None:
    n: int = 5
    from_item = 17981552
    http_request_parameters_factory = HackerNewsHttpRequestParametersFactory()
    http_response_adapter = HackerNewsHttpResponseAdapter()
    async_batch_http_request_executor = AsyncBatchHttpRequestExecutor(
        logger=logger, http_request_parameters_factory=http_request_parameters_factory, http_response_adapter=http_response_adapter)
    await async_batch_http_request_executor.run(loop=loop,
                                                itr_items=range(from_item, from_item - n, -1), n=n)
    print(http_response_adapter.responses)


if __name__ == '__main__':
    async_main_wrapper(main)
