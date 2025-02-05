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
module: consumer

description: Manage configuration of NATS consumers

options:
    connect_args:
        description: Connection arguments to connect to NATS server. Refer to <https://nats-io.github.io/nats.py/modules.html#nats.aio.client.Client.connect> for available options.
        required: true
        type: dict
    stream:
        description: The name of the stream to operate on.
        required: true
        type: str
    consumer:
        description: The name of the consumer to operate on.
        required: true
        type: str
    state:
        description: The intended state of the consumer.
        required: false
        default: present
        choices: [present, absent]
        type: str
    config:
        description: The configuration of the consumer. Refer to <https://docs.nats.io/nats-concepts/jetstream/consumers#configuration> for available options.
        required: false
        type: dict

author:
    - Castor (@castoredc)
"""


def main():
    module_args = dict(
        stream=dict(type="str", required=True),
        consumer=dict(type="str", required=True),
        state=dict(
            type="str", required=False, default="present", choices=["present", "absent"]
        ),
        config=dict(type="dict", required=False, default={}),
        connect_args=dict(type="dict", required=False, default={}),
    )

    result = dict(changed=False, original_message="", message="", config={})
    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)
    jetstream = NatsJetStream(**module.params["connect_args"])

    if module.params["state"] == "absent":
        coro = jetstream.delete_consumer(
            stream=module.params["stream"],
            consumer=module.params["consumer"],
            dry_run=module.check_mode,
        )
    else:
        coro = jetstream.update_consumer(
            stream=module.params["stream"],
            consumer=module.params["consumer"],
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
