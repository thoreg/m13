#!/bin/bash
NOW=`date "+%Y%m%dT%H%M%S"`
python manage.py dumpdata --natural-foreign --natural-primary -e contenttypes -e auth.Permission -e otto.StatsOrderItems -e zalando.StatsOrderItems -e etsy.StatsOrderItems -e zalando.rawdailyshipmentreport -e etsy -e admin --indent 2 > ${NOW}-dump.json
zip ${NOW}-dump.json.zip ${NOW}-dump.json
