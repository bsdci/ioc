# ioc

**The libioc command line tool for FreeBSD / HardenedBSD jail management**

ioc originates from the FreeBSD jail manager iocage.

## Compatibility

- python-iocage < 1.0 (JSON file)
- iocell (UCL file)
- iocage\_legacy @ master (UCL file)
- iocage\_legacy @ v1.7.6 (ZFS properties)

Jails created with either or mixed versions of the above implementations can be modified and used with ioc.
For performance reasons a migration to the latest configuration format is recommended:

```sh
ioc set config_type=json basejail=yes basejail_type=nullfs <MY_JAIL>
```

## Install

```sh
git clone https://github.com/bsdci/ioc
cd ioc
make install
```

At the current time ioc is not packaged or available in FreeBSD ports yet. A request for [sysutilc/ioc](https://bugs.freebsd.org/bugzilla/show_bug.cgi?id=234816) is in review on bugs.freebsd.org.

This Python module does not ship with a CLI tool. The project an installation instructions can be foun on [bsdci/ioc](https://github.com/bsdci/ioc).

## Documentation

- ioc Handbook: https://bsdci.github.io/handbook
- libioc Reference Documentation: https://bsdci.github.io/libioc
- Gitter Chat: https://gitter.im/libioc/community

## Configuration

### Active ZFS pool

libioc iterates over existing ZFS pools and stops at the first one with ZFS property `org.freebsd.ioc:active` set to `yes`.
This behavior is the default used by prior iocage variants and is restricted to one pool managed by iocage.

One or many datasets can be activated from rc.conf entries, replacing ZFS property activated pools.

### Root Datasets configured in /etc/rc.conf

When ioc datasets are specified in the jail hosts `/etc/rc.conf`, libioc prefers them over activated pool lookups.
Every ZFS filesystem that ioc should use as root dataset has a distinct name and is configured as `ioc_dataset_<NAME>="zroot/some-dataset/ioc"`, for example:

```
$ cat /etc/rc.conf | grep ^ioc_dataset
ioc_dataset_mysource="zroot/mysource/ioc"
ioc_dataset_iocage="zroot/iocage"
```

ioc commands default to the first root data source specified in the file.
Operations can be pointed to an alternative root by prefixing the subject with the source name followed by a slash.

```sh
ioc create othersource/myjail
ioc rename othersource/myjail myjail2
```

When `othersource` is the only datasource with a jail named `myjail` the above operation would have worked without explicitly stating the dataset name.

## Command Line Interface

The CLI tool called `ioc` is powered by libioc. 
It is inspired by the command line interface of [iocage](https://github.com/iocage/iocage) but meant to be developed along with [libioc](https://github.com/bsdci/libioc) and aims to improve stability and performance of prior implementations.

```
Usage: ioc [OPTIONS] COMMAND [ARGS]...

  A jail manager.

Options:
  --version             Show the version and exit.
  --source TEXT         Globally override the activated iocage dataset(s)
  -d, --log-level TEXT  Set the CLI log level ('critical', 'error', 'warn',
                        'info', 'notice', 'verbose', 'debug', 'spam',
                        'screen')
  --help                Show this message and exit.

Commands:
  activate    Set a zpool active for iocage usage.
  clone       Clone and promote jails.
  console     Login to a jail.
  create      Create a jail.
  deactivate  Disable a ZFS pool for iocage.
  destroy     Destroy specified resource
  exec        Run a command inside a specified jail.
  export      Export a jail to a backup archive
  fetch       Fetch and update a Release to create Jails...
  fstab       View and manipulate a jails fstab file.
  get         Gets the specified property.
  import      Import a jail from a backup archive
  list        List a specified dataset type, by default...
  migrate     Migrate jails to the latest format.
  pkg         Manage packages in a jail.
  promote     Clone and promote jails.
  provision   Trigger provisioning of jails.
  rename      Rename a stopped jail.
  restart     Restarts the specified jails.
  set         Sets the specified property.
  snapshot    Take and manage resource snapshots.
  start       Starts the specified jails or ALL.
  stop        Stops the specified jails or ALL.
  update      Starts the specified jails or ALL.
```

### Custom Release (e.g. running -CURRENT)

#### Initially create the release dataset

```sh
zfs create zroot/ioc/releases/custom/root
cd /usr/src
# install your source tree
make installworld DESTDIR=/ioc/releases/custom/root
make distribution DESTDIR=/ioc/releases/custom/root
ioc fetch -r custom -b
```

#### Update the installation after recompile
```sh
make installworld DESTDIR=/ioc/releases/custom/root
ioc fetch -r custom -b
```

## Development

### Static Code Analysis

The project enforces PEP-8 code style and MyPy strong typing via flake8, that is required to pass before merging any changes.
Together with Bandit checks for common security issues the static code analysis can be ran on Linux and BSD as both do not require py-libzfs or code execution.

```
make install-dev
make check
```

