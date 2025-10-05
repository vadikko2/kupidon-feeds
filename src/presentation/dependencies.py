import functools

import cqrs
from cqrs.events import bootstrap as event_bootstrap
from cqrs.requests import bootstrap as request_bootstrap

from infrastructure import dependencies
from service import mapping


@functools.lru_cache
def request_mediator_factory() -> cqrs.RequestMediator:
    return request_bootstrap.bootstrap(
        di_container=dependencies.container,
        commands_mapper=mapping.init_requests,
        domain_events_mapper=mapping.init_events,
    )


@functools.lru_cache
def event_mediator_factor() -> cqrs.EventMediator:
    return event_bootstrap.bootstrap(
        di_container=dependencies.container,
        events_mapper=mapping.init_events,
    )
