# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

"""The script for setting up stmdency."""
from __future__ import annotations

import logging
import os
from distutils.dir_util import remove_tree

from setuptools import Command, setup

logger = logging.getLogger(__name__)


class CleanCommand(Command):
    """Command to clean up python api before setup by running `python setup.py pre_clean`."""

    description = "Clean up project root"
    user_options: list[str] = []
    clean_list = [
        "build",
        "htmlcov",
        "dist",
        ".pytest_cache",
        ".coverage",
    ]

    def initialize_options(self) -> None:
        """Set default values for options."""

    def finalize_options(self) -> None:
        """Set final values for options."""

    def run(self) -> None:
        """Run and remove temporary files."""
        for cl in self.clean_list:
            if not os.path.exists(cl):
                logger.info("Path %s do not exists.", cl)
            elif os.path.isdir(cl):
                remove_tree(cl)
            else:
                os.remove(cl)
        logger.info("Finish pre_clean process.")


setup(
    cmdclass={
        "clean": CleanCommand,
    },
)
