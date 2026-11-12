#!/bin/sh
# Restricted SSH endpoint: no arbitrary command execution.
case "$SSH_ORIGINAL_COMMAND" in
 snapshot) jq -c '[.data.entries[] | select(.domain == "esphome") | {mac:.unique_id,host:.data.host,name:.data.device_name}]' /config/.storage/core.config_entries ;;
 logs) exec ha --api-token "$SUPERVISOR_TOKEN" apps logs core_mosquitto --follow --lines 200 ;;
 *) exit 126 ;;
esac
