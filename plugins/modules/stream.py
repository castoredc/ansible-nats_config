#!/usr/bin/python

import asyncio
import traceback

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.castoredc.nats_config.plugins.module_utils.nats_common import (
    NatsJetStream,
)

__metaclass__ = type


DOCUMENTATION = r"""
---
module: stream

description: Manage configuration of NATS streams

options:
    servers:
        description: List of NATS servers to connect to.
        required: false
        type: list
        default: ['nats://localhost:4222']
    user:
        description: Username to authenticate with.
        required: false
        type: str
    password:
        description: Password to authenticate with.
        required: false
        type: str
    token:
        description: Token to authenticate with.
        required: false
        type: str
    nkey:
        description: Nkey seed to authenticate with.
        required: false
        type: str
    connect_args:
        description: Additional connection arguments to connect to NATS server. Refer to <https://nats-io.github.io/nats.py/modules.html#nats.aio.client.Client.connect> for available options.
        required: true
        type: dict
    stream:
        description: The name of the stream to operate on.
        required: true
        type: str
    state:
        description: The intended state of the stream.
        required: false
        default: present
        choices: [present, absent]
        type: str
    config:
        description: The configuration of the stream. Refer to <https://docs.nats.io/nats-concepts/jetstream/streams#configuration> for available options.
        required: false
        type: dict

author:
    - Castor (@castoredc)
"""


def main():
    module_args = dict(
        servers=dict(type="list", required=False, default=["nats://localhost:4222"]),
        user=dict(type="str", required=False),
        password=dict(type="str", required=False, no_log=True),
        token=dict(type="str", required=False, no_log=True),
        nkey=dict(type="str", required=False, no_log=True),
        stream=dict(type="str", required=True),
        state=dict(
            type="str", required=False, default="present", choices=["present", "absent"]
        ),
        config=dict(type="dict", required=False, default={}),
        connect_args=dict(type="dict", required=False, default={}),
    )
    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    connect_args = module.params["connect_args"]
    connect_args.update(
        {
            "servers": module.params["servers"],
            "user": module.params["user"],
            "password": module.params["password"],
            "token": module.params["token"],
            "nkeys_seed_str": module.params["nkey"],
        }
    )

    result = dict(changed=False, original_message="", message="", config={})
    jetstream = NatsJetStream(**module.params["connect_args"])

    if module.params["state"] == "absent":
        coro = jetstream.delete_stream(
            stream=module.params["stream"],
            dry_run=module.check_mode,
        )
    else:
        coro = jetstream.update_stream(
            stream=module.params["stream"],
            config=module.params["config"],
            dry_run=module.check_mode,
        )

    try:
        result = asyncio.run(coro)
    except Exception as e:
        module.fail_json(msg=str(e), traceback=traceback.format_exc())
    else:
        module.exit_json(**result)


if __name__ == "__main__":
    main()
