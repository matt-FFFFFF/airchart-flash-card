#!/usr/bin/env bash
set -euo pipefail
rm -rf _site
mkdir -p _site
cp -R public/. _site/
cp -R web/. _site/
touch _site/.nojekyll
