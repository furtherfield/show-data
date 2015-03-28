!#/bin/bash
# Copyright 2015 Furtherfield
# License: GNU GPL v3 or later, at your option.

# Don't ignore ?page=1 etc., we need the main index ones to list all the others
# ideally we could handle it seperately, but for the moment just filter it later

wget --recursive --random-wait -R gif,jpg,png \
     --accept-regex "http://furtherfield.org/(exhibitions/|programmes/event/|programmes/exhibition/)" \
     http://furtherfield.org/programmes/exhibitions
