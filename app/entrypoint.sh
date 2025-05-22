#!/bin/bash

### WORKAROUND to sync yarn.lock file with sources
### COPY the the file to /tmp/yarn.lock, which is a shared volume in dev environments

cp -f /app/yarn.lock /tmp/yarn.lock
exec "$@"