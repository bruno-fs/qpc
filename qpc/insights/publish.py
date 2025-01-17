# Copyright (c) 2022 Red Hat, Inc.
#
# This software is licensed to you under the GNU General Public License,
# version 3 (GPLv3). There is NO WARRANTY for this software, express or
# implied, including the implied warranties of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. You should have received a copy of GPLv3
# along with this software; if not, see
# https://www.gnu.org/licenses/gpl-3.0.txt.
#
"""InsightsPublishCommand is used to publish insights report to C.RH.C."""

import os
import sys
import tarfile
from logging import getLogger
from pathlib import Path

from qpc import insights, messages
from qpc.clicommand import CliCommand
from qpc.exceptions import QPCError
from qpc.insights.http import InsightsClient
from qpc.translation import _
from qpc.utils import read_insights_config, read_insights_login_config

log = getLogger("qpc")


class InsightsPublishCommand(CliCommand):
    """Defines the Insights command.

    This command is for publishing server reports to insights client
    """

    SUBCOMMAND = insights.SUBCOMMAND
    ACTION = insights.PUBLISH

    def __init__(self, subparsers):
        """Create command."""
        super().__init__(
            self.SUBCOMMAND,
            self.ACTION,
            subparsers.add_parser(self.ACTION),
            None,
            None,
            [],
        )
        self.parser.add_argument(
            "--input-file",
            dest="input_file",
            metavar="INPUT_FILE",
            help=_(messages.INSIGHTS_INPUT_GZIP_HELP),
            required=True,
        )

    def _validate_insights_report_name(self):
        """Validate if report file exists and its file extension (tar.gz)."""
        input_file = self.args.input_file
        if not os.path.isfile(input_file):
            log.info(_(messages.INSIGHTS_LOCAL_REPORT_NOT), input_file)
            sys.exit(1)
        if "tar.gz" not in self.args.input_file:
            log.info(_(messages.INSIGHTS_LOCAL_REPORT_NOT_TAR_GZ), input_file)
            sys.exit(1)

    def _validate_insights_report_content(self):
        """Check if report tarball contains the expected json files."""
        filenames = self._get_filenames()

        if len(filenames) < 2:
            log.error(_(messages.INSIGHTS_REPORT_CONTENT_MIN_NUMBER))
            raise SystemExit(1)

        top_folder, filenames = self._separate_top_folder(filenames)

        if f"{top_folder}/metadata.json" not in filenames:
            log.error(_(messages.INSIGHTS_REPORT_CONTENT_MISSING_METADATA))
            raise SystemExit(1)

        for filename in filenames:
            self._validate_filename(top_folder, filename)

    def _get_filenames(self):
        try:
            with tarfile.open(self.args.input_file) as tarball:
                filenames = sorted(tarball.getnames())
        except tarfile.ReadError as err:
            log.exception(_(messages.INSIGHTS_REPORT_CONTENT_UNEXPECTED))
            raise SystemExit(1) from err
        return filenames

    def _is_top_folder(self, top_folder):
        expected_top_folder_parent = Path(".")
        return top_folder.parent == expected_top_folder_parent

    def _separate_top_folder(self, filenames):
        top_folder = Path(filenames[0])
        if self._is_top_folder(top_folder) and len(filenames) >= 3:
            filenames = filenames[1:]
        elif self._is_top_folder(top_folder.parent):
            top_folder = top_folder.parent
        else:
            log.error(_(messages.INSIGHTS_REPORT_CONTENT_UNEXPECTED))
            raise SystemExit(1)
        return top_folder, filenames

    def _validate_filename(self, top_folder, filename):
        filepath = Path(filename)
        if filepath.parent != top_folder:
            log.error(_(messages.INSIGHTS_REPORT_CONTENT_UNEXPECTED))
            raise SystemExit(1)
        if filepath.suffix != ".json":
            log.error(_(messages.INSIGHTS_REPORT_CONTENT_NOT_JSON))
            raise SystemExit(1)

    def _remove_file_extension(self):
        file_name = Path(self.args.input_file).stem
        return file_name.replace(".tar", "")

    def _publish_to_ingress(self):
        self._validate_insights_report_name()
        self._validate_insights_report_content()

        base_url = self._get_base_url()

        insights_login = read_insights_login_config()
        auth = (insights_login["username"], insights_login["password"])

        insights_client = InsightsClient(base_url=base_url, auth=auth)
        file_to_be_uploaded = open(  # pylint: disable=consider-using-with
            f"{self.args.input_file}", "rb"
        )
        filename_without_extensions = self._remove_file_extension()
        files = {
            "file": (
                f"{filename_without_extensions}",
                file_to_be_uploaded,
                f"{insights.CONTENT_TYPE}",
            )
        }
        successfully_submitted = self._make_publish_request(
            insights_client, insights.INGRESS_REPORT_URI, files
        )
        file_to_be_uploaded.close()
        if not successfully_submitted:
            raise SystemExit(1)

    def _get_base_url(self):
        insights_config = read_insights_config()

        if insights_config["use_http"]:
            protocol = "http://"
        else:
            protocol = "https://"
        host = insights_config["host"]
        port = insights_config["port"]

        base_url = f"{protocol}{host}:{port}"
        return base_url

    def _make_publish_request(self, session_client, url, files):
        """Make insights client request and log status code."""
        response = session_client.post(url=url, files=files)
        log.info(_(messages.INSIGHTS_PUBLISH_RESPONSE), response.text)
        if response.ok:
            log.info(_(messages.INSIGHTS_PUBLISH_SUCCESSFUL))
            print(response.text)
        elif response.status_code == 401:
            log.error(_(messages.INSIGHTS_PUBLISH_AUTH_ERROR))
        elif response.status_code == 404:
            log.error(_(messages.INSIGHTS_PUBLISH_NOT_FOUND_ERROR))
        elif response.status_code == 500:
            log.error(_(messages.INSIGHTS_PUBLISH_INTERNAL_SERVER_ERROR))

        return response.ok

    def _do_command(self):
        """Execute command flow.

        Sub-commands define this method to perform the required action once
        all options have been verified.
        """
        try:
            self._publish_to_ingress()
        except QPCError as err:
            log.error(_(err.message))
            SystemExit(1)
