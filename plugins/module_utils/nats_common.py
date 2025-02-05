from typing import Any, TypedDict

import cattrs
import nats
from nats.js.api import ConsumerConfig, StreamConfig
from nats.js.errors import NotFoundError
from nats.js.manager import JetStreamManager

converter = cattrs.Converter(forbid_extra_keys=True)


class Diff(TypedDict):
    before: dict[str, Any] | None
    after: dict[str, Any] | None


class Result(TypedDict):
    changed: bool
    diff: Diff | None


class NatsJetStream:
    def __init__(self, **connect_args: dict[str, Any]):
        # Having reconnections enabled causes a background connection pool to be
        # used which obscures connection errors. For ansible, it's better not to
        # have it (but a user could still force it by explicitly setting
        # allow_reconnect to True themselves).
        connect_args["allow_reconnect"] = connect_args.get("allow_reconnect", False)
        self.connect_args = connect_args

    async def _connect(self) -> JetStreamManager:
        nc = await nats.connect(**self.connect_args)
        return nc.jetstream()

    async def update_stream(
        self, stream: str, config: dict[str, Any], dry_run: bool = False
    ):
        config["name"] = stream
        js = await self._connect()

        try:
            stream_info = await js.stream_info(stream)
            state_before = converter.unstructure(stream_info.config)
        except NotFoundError:
            state_before = None

        state_after = config if state_before is None else state_before | config
        serialized_config = converter.structure(state_after, StreamConfig)
        if not dry_run:
            try:
                stream_info = await js.update_stream(serialized_config)
            except NotFoundError:
                stream_info = await js.add_stream(serialized_config)
            state_after = converter.unstructure(stream_info.config)

        return Result(
            changed=state_before != state_after,
            diff=Diff(before=state_before, after=state_after),
        )

    async def delete_stream(self, stream: str, dry_run: bool = False):
        js = await self._connect()

        try:
            stream_info = await js.stream_info(stream)
            state_before = converter.unstructure(stream_info.config)
        except NotFoundError:
            state_before = None

        state_after = None
        if not dry_run:
            try:
                await js.delete_stream(stream)
            except NotFoundError:
                pass

        return Result(
            changed=state_before != state_after,
            diff=Diff(before=state_before, after=state_after),
        )

    async def update_consumer(
        self, stream: str, consumer: str, config: dict[str, Any], dry_run: bool = False
    ):
        config["name"] = consumer
        js = await self._connect()

        try:
            consumer_info = await js.consumer_info(stream, consumer)
            state_before = converter.unstructure(consumer_info.config)
        except NotFoundError:
            state_before = None

        state_after = config if state_before is None else state_before | config
        serialized_config = converter.structure(state_after, ConsumerConfig)
        if not dry_run:
            await js.add_consumer(stream, serialized_config)

            # Even though add_consumer returns ConsumerInfo, the data comes back
            # stale which causes ansible to not report a correct diff.
            # Re-requesting consumer info works around this.
            consumer_info = await js.consumer_info(stream, consumer)
            state_after = converter.unstructure(consumer_info.config)

        return Result(
            changed=state_before != state_after,
            diff=Diff(before=state_before, after=state_after),
        )

    async def delete_consumer(self, stream: str, consumer: str, dry_run: bool = False):
        js = await self._connect()

        try:
            consumer_info = await js.consumer_info(stream, consumer)
            state_before = converter.unstructure(consumer_info.config)
        except NotFoundError:
            state_before = None

        state_after = None
        if not dry_run:
            try:
                await js.delete_consumer(stream, consumer)
            except NotFoundError:
                pass

        return Result(
            changed=state_before != state_after,
            diff=Diff(before=state_before, after=state_after),
        )
