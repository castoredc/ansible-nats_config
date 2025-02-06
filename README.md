# Ansible Collection - castoredc.nats_config

Modules to manage NATS streams and consumers.

## Dependencies

This module requires the following Python packages to be present on the target:

- [nats-py]
- [nkeys] (optional, for [nkeys authentication])

## Installation

To install the collection, run:

```shell
ansible-galaxy collection install git+https://github.com/castoredc/ansible-nats_config.git
```

## Examples

View documentation on the modules:

```shell
$ ansible-doc castoredc.nats_config.consumer

$ ansible-doc castoredc.nats_config.stream
```

Example playbook:

```yaml
- hosts: all
  vars:
    nats_servers: ["nats://localhost:4222"]
    nats_nkey: "SUAN2KG5DR3SCNY74U52KCY2SYD3HL6YEAFL5SOIR3OCXGMVYB3LQWFJ7E"

  tasks:
    - name: create stream
      castoredc.nats_config.stream:
        stream: example
        config:
          retention: "workqueue"
          subjects: ["foo", "bar"]
          placement:
            cluster: "test-cluster"
            tags: ["example"]
        servers: "{{ nats_servers }}"
        nkey: "{{ nats_nkey }}"

    - name: update subjects
      castoredc.nats_config.stream:
        stream: example
        config:
          subjects: ["foo.>"]
        servers: "{{ nats_servers }}"
        nkey: "{{ nats_nkey }}"

    - name: create consumer
      castoredc.nats_config.consumer:
        stream: example
        consumer: example
        config:
          durable_name: example
          ack_policy: "explicit"
          description: "An example consumer"
        servers: "{{ nats_servers }}"
        nkey: "{{ nats_nkey }}"

    - name: update consumer
      castoredc.nats_config.consumer:
        stream: example
        consumer: example
        config:
          description: "Updated consumer"
        servers: "{{ nats_servers }}"
        nkey: "{{ nats_nkey }}"

    - name: delete consumer
      castoredc.nats_config.consumer:
        stream: example
        consumer: example
        state: absent
        servers: "{{ nats_servers }}"
        nkey: "{{ nats_nkey }}"

    - name: delete stream
      castoredc.nats_config.stream:
        stream: example
        state: absent
        servers: "{{ nats_servers }}"
        nkey: "{{ nats_nkey }}"
```

[nats-py]: https://pypi.org/project/nats-py/
[nkeys authentication]: https://docs.nats.io/running-a-nats-service/configuration/securing_nats/auth_intro/nkey_auth
[nkeys]: https://pypi.org/project/nkeys/
