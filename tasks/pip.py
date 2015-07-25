# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import re

import invoke


REQUIREMENTS_HEADER = """
#
# This file is autogenerated by pip-compile
# Make changes in setup.py, then run this to update:
#
#    $ invoke pip.compile
#

-f https://github.com/Pylons/webob/archive/master.zip#egg=webob-1.5.dev0
-f https://github.com/mitsuhiko/jinja2/archive/master.zip#egg=jinja2-2.8.dev0
-f https://bitbucket.org/ecollins/passlib/get/default.zip#egg=passlib-1.7.dev0

""".lstrip()


@invoke.task
def compile():
    with open("requirements.in", "w") as fp:
        fp.write("-e .")

    try:
        invoke.run("pip-compile --no-header requirements.in", hide="out")
    finally:
        os.remove("requirements.in")

    lines = [REQUIREMENTS_HEADER]
    with open("requirements.txt", "r") as fp:
        for line in fp:
            line = re.sub(
                r"^passlib==(\S+)(.*)$",
                r"passlib==1.7.dev0\2",
                line,
            )
            line = re.sub(r"^jinja2==(\S+)(.*)$", r"jinja2==2.8.dev0\2", line)
            line = re.sub(r"^webob==(\S+)(.*)$", r"webob==1.5.dev0\2", line)

            # The boto3 wheel includes a futures==2.2.0 even though that is a
            # Python 2 only dependency. This dependency comes by default on
            # Python 3, so the backport is never needed. See boto/boto3#163.
            if re.search(r"^futures==2\.2\.0", line.strip()) is not None:
                continue

            if re.search(r"^-e file:///.+/warehouse$", line.strip()) is None:
                lines.append(line)

    with open("requirements.txt", "w") as fp:
        for line in lines:
            fp.write(line)