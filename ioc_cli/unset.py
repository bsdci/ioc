# Copyright (c) 2017-2019, Stefan Grönke, Igor Galić
# Copyright (c) 2014-2018, iocage
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted providing that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
# STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING
# IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
"""Unset a configuration value from the CLI."""
import typing
import click

import libioc.errors
import libioc.Host
import libioc.Jail
import libioc.Logger

from .shared.click import IocClickContext


@click.command(
    context_settings=dict(max_content_width=400,),
    name="get",
    help="""Deletes the specified property.

    Specify an individual jail by its name or use `defaults` to get the host's
    defaults from the main source dataset.
    """
)
@click.pass_context
@click.argument("prop", nargs=-1, required=False, default=None)
@click.argument("jail", nargs=1, required=True)
def cli(
    ctx: IocClickContext,
    prop: typing.Tuple[str],
    jail: typing.Optional[str]
) -> None:
    """Get a list of jails and delete the property."""
    logger = ctx.parent.logger
    host = libioc.Host.Host(logger=logger)

    _prop = None if len(prop) == 0 else prop[0]

    if jail == "defaults":
        source_resource = host.defaults
        delete_method = _delete_config_value
    else:
        delete_method = _delete_jail_value
        try:
            source_resource = libioc.Jail.Jail(
                jail,
                host=host,
                logger=logger
            )
        except libioc.errors.JailNotFound:
            exit(1)

    if (_prop is None) and (jail == ""):
        logger.error("Missing arguments property and jail")
        exit(1)
    elif (_prop is not None) and (jail == ""):
        logger.error("Missing argument property name")
        exit(1)

    if _prop:
        try:
            delete_method(source_resource, _prop)
        except KeyError:
            logger.error(f"Unknown property '{_prop}'")
            exit(1)

        print(_prop)


def _delete_config_value(
    resource: 'libioc.Resource.Resource',
    key: str
) -> None:
    del resource.config[key]


def _delete_jail_value(
    resource: 'libioc.LaunchableResource.LaunchableResource',
    key: str
) -> None:
    del resource.config[key]
