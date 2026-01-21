#!/usr/bin/env bash

docker run --rm -v "$PWD":/project -w /project -u "$UID" -e HOME=/tmp espressif/idf:v5.4.1 idf.py build || {
	echo "Docker build failed" >&2
	exit 1
}

TARGET_HOST="192.168.2.252"
FW_PATH="build/wican-fw_obd_$(git rev-parse --short HEAD).bin"

# Basic reachability check
if ! ping -c 1 -W 1 "$TARGET_HOST" >/dev/null 2>&1; then
	echo "Host unreachable: $TARGET_HOST" >&2
	exit 1
fi

# Check HTTP responsiveness
if ! curl -s -o /dev/null -w "%{http_code}\n" "http://${TARGET_HOST}/" | grep -q "^[23]"; then
	echo "HTTP check failed on http://${TARGET_HOST}/" >&2
	exit 1
fi

if [ -f "$FW_PATH" ]; then
	curl -v -X POST -F "file=@${FW_PATH}" "http://${TARGET_HOST}/upload/ota.bin"
else
	echo "Firmware not found: $FW_PATH" >&2
	exit 1
fi
