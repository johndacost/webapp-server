#!/usr/bin/env python3
"""
Database creation
-----------------

Sets up all the databases
"""

import os
import sys
import yaml
import subprocess
import tempfile
import textwrap

__author__ = "Yoan Blanc <yoan@dosimple.ch>"
__version__ = "0.4.0"

# Database host
hostname = "127.0.0.1"
# Root password
root = "root"

mysql = textwrap.dedent(r"""\
    DROP USER IF EXISTS `{username}`;
    DROP DATABASE IF EXISTS `{database}`;
    DROP DATABASE IF EXISTS `{database}_production`;
    DROP DATABASE IF EXISTS `{database}_test`;
    CREATE USER '{username}'@'%';
    SET PASSWORD FOR '{username}'@'%' = PASSWORD('{password}');
    CREATE DATABASE `{database}` DEFAULT CHARACTER SET utf8mb4 DEFAULT COLLATE utf8mb4_unicode_ci;
    CREATE DATABASE `{database}_production` DEFAULT CHARACTER SET utf8mb4 DEFAULT COLLATE utf8mb4_unicode_ci;
    CREATE DATABASE `{database}_test` DEFAULT CHARACTER SET utf8mb4 DEFAULT COLLATE utf8mb4_unicode_ci;
    GRANT ALL PRIVILEGES ON `{database}`.* TO '{username}'@'%';
    GRANT ALL PRIVILEGES ON `{database}_production`.* TO '{username}'@'%';
    GRANT ALL PRIVILEGES ON `{database}_test`.* TO '{username}'@'%';
    FLUSH PRIVILEGES;
""")

postgresql = textwrap.dedent(r"""\
    DROP DATABASE IF EXISTS {database};
    DROP ROLE IF EXISTS {username};
    CREATE ROLE {username} WITH NOINHERIT LOGIN PASSWORD '{password}' VALID UNTIL 'infinity';
    CREATE DATABASE {database} WITH ENCODING 'UTF8' OWNER {username};
    REVOKE ALL PRIVILEGES ON DATABASE {database} FROM public;
    GRANT ALL PRIVILEGES ON DATABASE {database} TO {username};
    \c {database}
    DROP SCHEMA IF EXISTS public CASCADE;
    CREATE SCHEMA {username} AUTHORIZATION {username};
    CREATE SCHEMA production AUTHORIZATION {username};
    CREATE SCHEMA test AUTHORIZATION {username};
    CREATE EXTENSION IF NOT EXISTS postgis WITH SCHEMA {username};
    CREATE EXTENSION IF NOT EXISTS postgis WITH SCHEMA production;
    CREATE EXTENSION IF NOT EXISTS postgis WITH SCHEMA test;
""")


def main():
    compose = yaml.load(sys.stdin)

    for machine, description in compose['services'].items():
        if not description['image'].startswith('hearcch'):
            continue

        groupname = description['environment']['GROUPNAME'].lower()
        password = description['environment']['PASSWORD']

        print(groupname)
        print("=" * len(groupname))

        p = subprocess.Popen(
            ['mysql', '-h', hostname, '-u', 'root', '-p{}'.format(root)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)

        stdin = mysql.format(
            username=groupname, password=password,
            database=groupname).strip()

        out, err = p.communicate(bytearray(stdin, 'utf-8'))
        if p.returncode != 0:
            sys.stderr.write(err.decode('utf-8'))
        else:
            print("MySQL database {} created.".format(groupname))
            # DEBUG
            # print(out.decode('utf-8'), end='')

        with tempfile.NamedTemporaryFile() as fp:
            fp.write(
                bytearray('{}:*:*:postgres:{}'.format(hostname, root),
                            'utf-8'))
            fp.seek(0)
            os.chmod(fp.name, mode=0o600)

            env = os.environ.copy()
            env['PGPASSFILE'] = fp.name

            p = subprocess.Popen(
                ['psql', '-h', hostname, '-U', 'postgres'],
                env=env,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)

            stdin = postgresql.format(
                username=groupname, password=password,
                database=groupname).strip()

            out, err = p.communicate(bytearray(stdin, 'utf-8'))
            if p.returncode != 0:
                sys.stderr.write(err.decode('utf-8'))
            else:
                print("Postgresql database {} created.".format(groupname))
                # DEBUG
                # print(out.decode('utf-8'), end='')

        print("")


if __name__ == "__main__":
    sys.exit(main())
