#!/usr/bin/env bash
pyinstaller --clean -y --windowed --osx-bundle-identifier app.webpow.webpow -i icons.ics webpow.spec
