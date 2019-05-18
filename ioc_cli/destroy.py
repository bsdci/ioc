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
"""Destroy a jail from the CLI."""
import click
import typing

import libioc.errors
import libioc.Filter
import libioc.Jail
import libioc.Jails
import libioc.Logger
import libioc.Releases
import libioc.Resource

from .shared.click import IocClickContext

__rootcmd__ = True


@click.command(name="destroy", help="Destroy specified resource")
@click.pass_context
@click.option("--force", "-f", default=False, is_flag=True,
              help="Destroy the jail without warnings or more user input.")
@click.option(
    "--template", "-t",
    "dataset_type",
    flag_value="template",
    help="List all templates."
)
@click.option(
    "--release", "-r",
    "dataset_type",
    flag_value="release",
    help="Destroy a specified RELEASE dataset."
)
@click.option("--recursive", "-R", default=False, is_flag=True,
              help="Bypass the children prompt, best used with --force (-f).")
@click.argument("filters", nargs=-1)
def cli(
    ctx: IocClickContext,
    force: bool,
    dataset_type: typing.Optional[str],
    recursive: bool,
    filters: typing.Tuple[str, ...]
) -> None:
    """
    Destroy a jail, release or template.

    Looks for the jail supplied and passes the uuid, path and configuration
    location to stop_jail.
    """
    logger = ctx.parent.logger

    if filters is None or len(filters) == 0:
        logger.error("No filter specified - cannot select a target to delete")
        exit(1)

    if dataset_type is None:
        filters += ("template=no,-",)
        dataset_type = "jail"
    elif dataset_type == "template":
        filters += ("template=yes",)

    release = (dataset_type == "release") is True

    resources_class: typing.Union[
        typing.Type[libioc.Releases.ReleasesGenerator],
        typing.Type[libioc.Jails.JailsGenerator]
    ]
    if release is True:
        resources_class = libioc.Releases.ReleasesGenerator
    else:
        resources_class = libioc.Jails.JailsGenerator

    try:
        resources = list(resources_class(
            filters=filters,
            zfs=ctx.parent.zfs,
            host=ctx.parent.host,
            logger=logger,
            skip_invalid_config=True
        ))
    except libioc.errors.IocException:
        exit(1)

    if len(resources) == 0:
        logger.error("No target matched your input")
        exit(1)

    if not force:
        _msg = f"These {dataset_type}s will be deleted"
        message = "\n- ".join(
            [_msg] + [r.getstring('full_name') for r in resources]
        ) + "\nAre you sure?"
        click.confirm(message, default=False, abort=True)

    failed_items = []

    for item in resources:

        old_mountpoint = item.dataset.mountpoint

        if (not release and force and item.running) is True:
            ctx.parent.print_events(item.stop(force=True))

        try:
            ctx.parent.print_events(item.destroy())
            logger.screen(f"{old_mountpoint} destroyed")
        except libioc.errors.IocException:
            failed_items.append(item)

    if len(failed_items) > 0:
        exit(1)
