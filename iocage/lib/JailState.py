# Copyright (c) 2014-2017, iocage
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
"""Jail State collection."""
import typing
import shlex
import subprocess

import iocage.lib.errors

JailStatesDict = typing.Dict[str, 'JailState']


def _parse(text: str) -> JailStatesDict:
    output: JailStatesDict = {}
    for line in text.split("\n"):
        data: typing.Dict[str, str] = {}
        for item in shlex.split(line):
            if "=" not in item:
                data[item] = ""
            else:
                pair = item.split("=", maxsplit=1)
                if len(pair) == 2:
                    data[pair[0]] = pair[1]
                else:
                    data[pair[0]] = ""
        output[data["name"]] = JailState(data["name"], data)
    return output


class JailState(dict):
    """State of a running Resource/Jail."""

    name: str
    _data: typing.Optional[typing.Dict[str, str]] = None
    updated = False

    def __init__(
        self,
        name: str,
        data: typing.Optional[typing.Dict[str, str]]=None,
    ) -> None:

        self.name = name

        if data is not None:
            self._data = data

    def query(self) -> typing.Dict[str, str]:
        """Execute jls to update a jails state."""
        data: typing.Dict[str, str] = {}
        try:
            stdout = subprocess.check_output([
                "/usr/sbin/jls",
                "-j",
                self.name,
                "-v",
                "-n",
                "-q"
            ], shell=False, stderr=subprocess.DEVNULL)  # nosec TODO use helper
            data = _parse(stdout.decode().strip())[self.name]
        except (subprocess.CalledProcessError, KeyError):
            pass
        self._data = data
        return data

    @property
    def data(self) -> typing.Dict[str, str]:
        """Return the jail state data that was previously queried."""
        if self._data is None:
            self._data = self.query()
        return self._data

    def __getitem__(self, name: str) -> str:
        """Get a value from the jail state."""
        return self.data[name]

    def __iter__(
        self
    ) -> typing.Iterator[str]:
        """Iterate over the jail state entries."""
        return self.data.__iter__()

    def keys(self) -> typing.List[str]:  # noqa: T484
        """Return all available jail state keys."""
        return list(self.data.keys())


class JailStates(dict):
    """A dictionary of JailStates."""

    def __init__(
        self,
        states: typing.Optional[JailStatesDict]=None
    ) -> None:

        if states is None:
            dict.__init__(self, {})
        else:
            dict.__init__(self, states)

    def query(self) -> None:
        """Invoke update of the jail state from jls output."""
        try:
            stdout = subprocess.check_output([
                "/usr/sbin/jls",
                "-v",
                "-n",
                "-q"
            ], shell=False, stderr=subprocess.DEVNULL)  # nosec TODO use helper
            output = stdout.decode().strip()
            output_data = _parse(output)
            for name in output_data:
                dict.__setitem__(self, name, output_data[name])

        except BaseException:
            raise iocage.lib.errors.JailStateUpdateFailed()
