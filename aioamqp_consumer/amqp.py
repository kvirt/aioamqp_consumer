from aioamqp import AioamqpException, from_url

from .log import logger


class AMQPMixin:

    _connected = _closed = False
    _transport = _protocol = _channel = None

    def _on_error_callback(self, exc):
        while hasattr(exc, 'code'):
            _exc = getattr(exc, 'code')

            if isinstance(_exc, Exception):
                exc = _exc
            else:
                break

        _code = getattr(exc, 'code', None)
        _message = getattr(exc, 'message', None)

        if _code is not None or _message is not None:
            logger.exception(exc)

    async def _connect(self, url, on_error=None, **kwargs):
        if self._connected:
            return

        assert not self._closed, 'Already closed'
        assert self._transport is None
        assert self._protocol is None
        assert self._channel is None

        if on_error is None:
            on_error = self._on_error_callback

        kwargs['on_error'] = on_error

        try:
            self._transport, self._protocol = await from_url(
                url,
                **kwargs,
            )
        except OSError as exc:
            raise AioamqpException from exc

        self._channel = await self._protocol.channel()

        self._connected = True

        msg = 'Connected amqp'
        logger.debug(msg)

    async def _disconnect(self):
        if self._transport is not None and self._protocol is not None:
            if self._channel is not None:
                try:
                    await self._channel.close()

                    msg = 'Amqp channel is closed'
                    logger.debug(msg)
                except AioamqpException:
                    pass

            try:
                await self._protocol.close()

                self._transport.close()

                msg = 'Amqp protocol and transport are closed'
                logger.debug(msg)
            except (AioamqpException, AttributeError):
                # AttributeError tmp hotfix
                pass

        self._transport = self._protocol = self._channel = None
        self._connected = False

    async def _queue_declare(self, **kwargs):
        return await self._channel.queue_declare(**kwargs)

    async def _queue_bind(self, *args, **kwargs):
        return await self._channel.queue_bind(*args, **kwargs)

    async def _queue_delete(self, *args, **kwargs):
        return await self._channel.queue_delete(*args, **kwargs)

    async def _queue_purge(self, *args, **kwargs):
        return await self._channel.queue_purge(*args, **kwargs)

    async def _exchange_declare(self, *args, **kwargs):
        return await self._channel.exchange_declare(*args, **kwargs)

    async def _exchange_bind(self, *args, **kwargs):
        return await self._channel.exchange_bind(*args, **kwargs)

    async def _basic_reject(self, *args, **kwargs):
        return await self._channel.basic_reject(*args, **kwargs)

    async def _basic_client_ack(self, *args, **kwargs):
        return await self._channel.basic_client_ack(*args, **kwargs)

    async def _basic_qos(self, **kwargs):
        return await self._channel.basic_qos(**kwargs)

    async def _basic_consume(self, *args, **kwargs):
        return await self._channel.basic_consume(*args, **kwargs)

    async def _basic_publish(self, *args, **kwargs):
        return await self._channel.basic_publish(*args, **kwargs)

    async def _basic_cancel(self, *args, **kwargs):
        return await self._channel.basic_cancel(*args, **kwargs)
