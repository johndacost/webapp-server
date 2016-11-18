# WebApp Server

[![Join the chat at https://gitter.im/HE-Arc/webapp-server](https://badges.gitter.im/HE-Arc/webapp-server.svg)](https://gitter.im/HE-Arc/webapp-server?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

The setup scripts to create development environments for many groups.

## Requirements

- Docker >1.10
- Python 3 (pip, virtualenv or requests)

## Setup

### Students

The configuration is done via a TSV file (`config/students.tsv`). Here is its format:

Lastname | Firstname | Email                | Group   | Github   | Team1  | Team2 | Comment
-------- | --------- | -------------------- | ------- | -------- | ------ | ----- | -------
Bon      | Jean      | jean.bon@example.org | INF3    | jeanjean | ninjas | funky | -
Blanc    | Yoan      | yoan.blanc@he-arc.ch | Teacher | greut    | admin  | admin | -

This is how this file is used:

- _Lastname_ no particular usage
- _Firstname_ becomes the username
- _Group_ no particular usage
- _GitHub_ identifier to download the SSH public keys
- _TeamX_ will be the name of the virtual host and identify a container
- _Comment_ no particular usage

### Public keys

To download the public keys, run this python script:

```shell
# setup
$ virtualenv3 .
$ . bin/activate
$ pip3 install -r requirements.txt

$ scripts/github_keys.py config/students.tsv config/keys/ <github_username> <password_or_key>
```

The key is a [personal access token](https://github.com/settings/tokens) to avoid being rate limited by the API.

## Containers

If you don't want to use the [publicly available containers](https://hub.docker.com/r/greut/webapp-server/), you can build them yourself.

```
# Base container
$ docker-compose -f build.yml build base
# Laravel container
$ docker-compose -f build.yml build laravel
# Rails container
$ docker-compose -f build.yml build rails
```

## Run the base

```
$ docker run -d \
             -v `pwd`/config \
             -p 80 \
             greut/webapp-server
```

## Run via docker-compose

Create a `docker-compose.yml` file base on the sample one.

Run the container(s)

```shell
docker-compose up -d
```

### Databases

The databases are open the external world, hence we must modify the super admin password. Setting up a good one during the startup won't be as effective as it will be visible from within the containers anyway.

#### MySQL

##### Post-setup

Changing MySQL root password because the above value will be passed to each linked containers.

```shell
# 5.6
$ mysqladmin -h 127.0.0.1 -u root -p'root' password 's3cur3@P45sw0rd'

# 5.7
$ mysql -h 127.0.0.1 -u root -proot
> SET PASSWORD FOR 'root'@'%' = PASSWORD('s3cur3@P45sw0rd');
```

#### PostgreSQL

Changing Postgres password because the above value will be passed to each linked containers.

```shell
$ psql -h 127.0.0.1 \
    -U postgres \
    -c "ALTER USER postgres WITH PASSWORD 's3cur3@P45sw0rd';"
```

#### Creating the roles and users

Use the script bdd.py to create the proper databases and roles.

```
$ python3 scripts/bdd.py config/bdd.csv
```

Where the csv file contains key values of this type:

```
groupname;password
```

`pwgen` is a great way to build good passwords.

## Troubleshooting with docker-compose

COMPOSE_API_VERSION=1.18
