# Surok

[![Build Status](https://travis-ci.org/Difrex/surok.svg?branch=master)](https://travis-ci.org/Difrex/surok)

Service discovery for Apache Mesos.

* Jinja2 Templates
* Discovery over mesos-dns
* Applications config reload

**Table of Contents**

- [Surok](https://difrex.github.io/surok/)
    - [Build](https://github.com/Difrex/surok/blob/master/docs/Build.md)
    - [Wiki](https://github.com/Difrex/surok/wiki)
    - **Configuration**
      - [Main config file](https://github.com/Difrex/surok/blob/master/docs/Main-config-file.md)
      - [App config file](https://github.com/Difrex/surok/blob/master/docs/App-config-file.md)
      - [Templates](https://github.com/Difrex/surok/blob/master/docs/Templates.md)
    - **Usage**
      - [Use Surok with Supervisord](https://github.com/Difrex/surok/blob/master/docs/Use-Surok-with-supervisord.md) 
- [Known issues](#known-issues)
- [Athors](#authors)
- [LICENSE](#license)

## Known issues

* python3-memcache is broken in Debian Jessie. Backport fresh version from testing (>= 1.57).

## Authors

* Denis Zheleztsov <difrex.punk@gmail.com>
* Denis Ryabyy <vv1r0x@gmail.com>

## LICENSE

Released under BSD 3-clause license. See [LICENSE](https://raw.githubusercontent.com/Difrex/surok/master/LICENSE)
