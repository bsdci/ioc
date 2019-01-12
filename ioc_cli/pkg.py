# Copyright (c) 2017-2019, Stefan Grönke
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
"""Jail package management subcommand for the CLI."""
import typing
import click

import libioc.Jail
import libioc.Pkg
import libioc.Logger
import libioc.errors

from .shared.click import IocClickContext


@click.command(name="pkg", help="Manage packages in a jail.")
@click.pass_context
@click.option(
    "--remove", "-r",
    "remove",
    is_flag=True,
    default=False,
    help="Remove the packages instead of installing/updating them."
)
@click.argument("jail")
@click.argument("packages", nargs=-1)
def cli(
    ctx: IocClickContext,
    remove: bool,
    jail: str,
    packages: typing.Tuple[str, ...]
) -> None:
    """Manage packages within jails using an offline mirror."""
    logger = ctx.parent.logger

    try:
        ioc_jail = libioc.Jail.JailGenerator(
            jail,
            logger=logger,
            zfs=ctx.parent.zfs,
            host=ctx.parent.host
        )
    except libioc.errors.JailNotFound:
        exit(1)

    try:
        pkg = libioc.Pkg.Pkg(
            logger=logger,
            zfs=ctx.parent.zfs,
            host=ctx.parent.host
        )
        if remove is False:
            events = pkg.fetch_and_install(
                jail=ioc_jail,
                packages=list(packages)
            )
        else:
            events = pkg.remove(
                jail=ioc_jail,
                packages=list(packages)
            )
        ctx.parent.print_events(events)
    except libioc.errors.IocException:
        exit(1)

