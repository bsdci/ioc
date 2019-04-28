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
"""Export a jail from the CLI."""
import click
import os.path

import libioc.errors
import libioc.Filter
import libioc.Jail
import libioc.Jails
import libioc.Logger
import libioc.Releases
import libioc.Resource

from .shared.click import IocClickContext

__rootcmd__ = True


@click.command(name="export", help="Export a jail to a backup destination")
@click.pass_context
@click.argument("jail", required=True)
@click.argument("destination", required=True)
@click.option(
    "-s", "--standalone",
    default=False,
    is_flag=True,
    help="Exports the jails root dataset independently"
)
@click.option(
    "--format",
    "_format",
    default="txz",
    type=click.Choice(["txz", "directory"]),
    help="Export the jail to a Tar Archive (compressed) or a new directory."
)
# @click.option(
#     "-r", "--recursive",
#     default=False,
#     is_flag=True,
#     help="Include ZFS snapshots. Implies --standalone"
# )
def cli(
    ctx: IocClickContext,
    jail: str,
    destination: str,
    standalone: bool,
    _format: str
) -> None:
    """
    Backup a jail.

    The selected jail will be exported to a gzip compressed tar archive stored
    as the destination path.
    """
    logger = ctx.parent.logger
    zfs: libioc.ZFS.ZFS = ctx.parent.zfs
    host: libioc.Host.HostGenerator = ctx.parent.host
    print_events = ctx.parent.print_events

    # Recursive exports cannot be imported at the current time
    recursive = False

    ioc_jail = libioc.Jail.JailGenerator(
        jail,
        logger=logger,
        zfs=zfs,
        host=host
    )

    if os.path.isfile(destination) is True:
        logger.error(f"The destination {destination} already exists")
        exit(1)

    try:
        print_events(ioc_jail.backup.export(
            destination,
            standalone=standalone,
            recursive=recursive,
            backup_format=_format
        ))
    except libioc.errors.IocException:
        exit(1)
