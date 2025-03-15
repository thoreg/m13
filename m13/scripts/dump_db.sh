#!/bin/bash
NOW=`date "+%Y%m%dT%H%M%S"`
DIR=`pwd`
python manage.py dumpdata      \
    --natural-foreign          \
    --natural-primary          \
    -e contenttypes            \
    -e auth.Permission         \
    -e otto.StatsOrderItems    \
    -e zalando.StatsOrderItems \
    -e etsy.StatsOrderItems    \
    -e etsy                    \
    -e admin                   \
    -e core.SalesStatsTop13    \
    -e core.SalesStatsReturnTop13 \
    -e core.SalesVolumeZalando \
    -v 2                       \
    --traceback                \
    --indent 2 > ${NOW}-dump.json
zip ${NOW}-dump.json.zip ${NOW}-dump.json
echo
PWD=`pwd`
echo "scp gaja:${DIR}/${NOW}-dump.json.zip ."
echo
