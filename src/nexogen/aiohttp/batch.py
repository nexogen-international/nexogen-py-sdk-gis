#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
NEXOGEN AIOHTTP Batch
"""

from __future__ import annotations
__version__ = '0.1.0'

from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import Any, Coroutine, Dict, Iterable, NoReturn, Optional, Sequence

import aiohttp
import asyncio
import logging

MAX_CONNECTION: int = 100
MAIN_QUEUE_SIZE: int = 200
DLQ_SLEEP_SECONDS: int = 5
DLQ_CONSUMER_NUM: int = 20
HTTP_STATUS_CODES_TO_RETRY = [500, 502, 503, 504]


@dataclass
class HttpRequestParameters:
    method: str
    url: str
    headers: Optional[Dict[str, str]]
    params: Optional[Dict[str, str]]
    json: Optional[Dict[str, str]]
    timeout: int


class AbstractHttpRequestParametersFactory(ABC):
    '''An abstract HTTP request factory class.'''
    @abstractmethod
    def create_http_request_parameters(self, request_item: Any) -> HttpRequestParameters:
        pass


class AbstractHttpResponseAdapter(ABC):
    '''An abstract HTTP response adapter class.'''
    @abstractmethod
    def on_http_response(self, idx: int, request_item: Any, response_json: Dict[str, str]):
        pass


@dataclass
class AsyncBatchHttpRequestExecutorSettings:
    max_connection: int = MAX_CONNECTION
    main_queue_size: int = MAIN_QUEUE_SIZE
    dlq_sleep_seconds: int = DLQ_SLEEP_SECONDS
    dlq_consumer_num: int = DLQ_CONSUMER_NUM


class AsyncBatchHttpRequestExecutor:
    '''Async batch HTTP request executor'''
    __logger: logging.Logger
    __http_request_parameters_factory: AbstractHttpRequestParametersFactory
    __http_response_adapter: AbstractHttpResponseAdapter
    settings: AsyncBatchHttpRequestExecutorSettings = AsyncBatchHttpRequestExecutorSettings()

    def __init__(self, logger: logging.Logger, http_request_parameters_factory: AbstractHttpRequestParametersFactory, http_response_adapter: AbstractHttpResponseAdapter):
        self.__logger = logger
        self.__http_request_parameters_factory = http_request_parameters_factory
        self.__http_response_adapter = http_response_adapter

    async def __http_request_consumer(self, main_queue: asyncio.Queue, dlq: asyncio.Queue, session: aiohttp.ClientSession) -> NoReturn:
        '''HTTP request consumer'''
        while True:
            try:
                (idx, item) = await main_queue.get()

                request_params: HttpRequestParameters = None
                try:
                    request_params = self.__http_request_parameters_factory.create_http_request_parameters(
                        item)
                except Exception as e:
                    self.__logger.error(e)
                    # TODO: on error callback

                if request_params is not None:
                    async with session.request(method=request_params.method, url=request_params.url, headers=request_params.headers, params=request_params.params, json=request_params.json, timeout=request_params.timeout) as response:
                        response.raise_for_status()
                        response_json = await response.json()

                        try:
                            self.__http_response_adapter.on_http_response(
                                idx, item, response_json)
                        except Exception as e:
                            self.__logger.error(e)
                            # TODO: on error callback

                main_queue.task_done()

            except (aiohttp.ClientError,
                    asyncio.TimeoutError,
                    aiohttp.http_exceptions.HttpProcessingError) as e:
                self.__logger.debug(
                    f'Warning. Problem with request {str(idx)}. Error: ({e})')
                retry_request = True
                if isinstance(e, aiohttp.ClientResponseError):
                    response_status = e.status
                    if response_status not in HTTP_STATUS_CODES_TO_RETRY:
                        retry_request = False
                if retry_request:
                    self.__logger.debug(
                        f'Moving request {str(idx)} to DLQ. Q: ({str(main_queue.qsize())}), DLQ: ({str(dlq.qsize())}).')
                    await dlq.put((idx, item))
                    await asyncio.sleep(self.settings.dlq_sleep_seconds)

                main_queue.task_done()

            except asyncio.CancelledError as e:
                raise e

    async def __produce_http_requests(self, queue: asyncio.Queue, itr_items: Iterable[Any]) -> None:
        '''produce HTTP requests'''
        for idx, item in enumerate(itr_items):
            await queue.put((idx, item))

    async def __perform_batch_http_requests(self, session: aiohttp.ClientSession, consumer_num: int, itr_items: Iterable[Any]) -> None:
        '''perform batch HTTP requests'''
        main_queue: asyncio.Queue = asyncio.Queue(
            maxsize=self.settings.main_queue_size)
        dlq: asyncio.Queue = asyncio.Queue()
        consumers: Sequence[Coroutine] = [asyncio.ensure_future(
            self.__http_request_consumer(main_queue=main_queue, dlq=dlq, session=session))
            for _ in range(consumer_num)]
        dlq_consumers: Sequence[Coroutine] = [asyncio.ensure_future(
            self.__http_request_consumer(main_queue=dlq, dlq=dlq, session=session))
            for _ in range(self.settings.dlq_consumer_num)]
        await self.__produce_http_requests(queue=main_queue, itr_items=itr_items)
        await main_queue.join()
        await dlq.join()
        for consumer_future in consumers + dlq_consumers:
            consumer_future.cancel()

    async def run(self, loop: asyncio.AbstractEventLoop, itr_items: Iterable[Any], n: int = MAX_CONNECTION) -> None:
        '''run HTTP requests and await for the responses'''
        conn_num: int = min(self.settings.max_connection, n)
        async with aiohttp.ClientSession(loop=loop, connector=aiohttp.TCPConnector(limit=conn_num)) as session:
            await self.__perform_batch_http_requests(session, conn_num, itr_items=itr_items)
