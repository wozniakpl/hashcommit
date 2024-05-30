#!/bin/bash
set -e

if [ $# -eq 0 ]; then
    tox
else
  case "$1" in
    *)
      exec "$@"
      ;;
  esac
fi
