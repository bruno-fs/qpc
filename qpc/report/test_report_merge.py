"""Test the CLI module."""

import json
import logging
import sys
from argparse import ArgumentParser, Namespace
from pathlib import Path
from uuid import uuid4

import pytest

from qpc import messages
from qpc.cli import CLI
from qpc.release import QPC_VAR_PROGRAM_NAME
from qpc.report import ASYNC_MERGE_URI
from qpc.report.merge import ReportMergeCommand
from qpc.scan import SCAN_JOB_URI
from qpc.utils import get_server_location


@pytest.fixture
def details1(tmp_path):
    """Fixture for a "good" details report file file."""
    _path = tmp_path / "details_report1.json"
    _path.write_text('{"id": 1,"sources":[{"facts": ["B"],"server_id": "8"}]}')
    return str(_path)


@pytest.fixture
def details2(tmp_path):
    """Fixture for a "bad" details report file file."""
    _path = tmp_path / "details_report2.json"
    _path.write_text('{"id": 2,"sources":[{"source_name": "source2"}]}')
    return str(_path)


@pytest.fixture
def not_json_file(tmp_path):
    """Fixture for a file that's not a report (not even a json)."""
    _path = tmp_path / "notjson.txt"
    _path.write_text("not a json file")
    return str(_path)


@pytest.fixture
def bad_details1(tmp_path):
    """Fixture for a "bad" details report file."""
    _path = tmp_path / "bad_details_report_source.json"
    _path.write_text('{"id": 4,"bsources":[{"facts": ["A"],"server_id": "8"}]}')
    return str(_path)


@pytest.fixture
def bad_details2(tmp_path):
    """Fixture for a "bad" details report file."""
    _path = tmp_path / "bad_details_report_facts.json"
    _path.write_text('{"id": 4,"sources":[{"bfacts": ["A"],"server_id": "8"}]}')
    return str(_path)


@pytest.fixture
def bad_details3(tmp_path):
    """Fixture for a "bad" details report file."""
    _path = tmp_path / "bad_details_report_server_id.json"
    _path.write_text('{"id": 4,"sources":[{"facts": ["A"],"bserver_id": "8"}]}')
    return str(_path)


@pytest.fixture
def bad_details4(tmp_path):
    """Fixture for a "bad" details report file."""
    _path = tmp_path / "bad_details_report_bad_json.json"
    _path.write_text('{"id":3,"sources": [this is bad]')
    return str(_path)


@pytest.fixture
def bad_details5(tmp_path):
    """Fixture for a "bad" details report file."""
    _path = tmp_path / "bad_details_invalid_report_type.json"
    _path.write_text('{"report_type": "durham"}')
    return str(_path)


@pytest.fixture
def gooddetails(tmp_path):
    """Fixture for a "good" details report file."""
    _path = tmp_path / "good_details_report.json"
    report = {
        "report_type": "details",
        "report_version": "1.2.3+outer_version",
        "report_id": 38,
        "sources": [
            {
                "facts": ["A"],
                "server_id": "42",
                "report_version": "1.2.3+inner_version",
            }
        ],
    }
    _path.write_text(json.dumps(report))
    return str(_path)


@pytest.mark.usefixtures("server_config")
class TestReportMergeTests:
    """Class for testing the scan show commands for qpc."""

    @classmethod
    def setup_class(cls):
        """Set up test case."""
        argument_parser = ArgumentParser()
        subparser = argument_parser.add_subparsers(dest="subcommand")
        cls.command = ReportMergeCommand(subparser)

    def test_detail_merge_job_ids(self, capsys, requests_mock):
        """Testing report merge command with scan job ids."""
        requests_mock.get(
            get_server_location() + SCAN_JOB_URI + "1/",
            status_code=200,
            json={"report_id": 1},
        )
        requests_mock.get(
            get_server_location() + SCAN_JOB_URI + "2/",
            status_code=200,
            json={"report_id": 2},
        )
        requests_mock.put(
            get_server_location() + ASYNC_MERGE_URI,
            status_code=201,
            json={"id": 1},
        )

        args = Namespace(
            scan_job_ids=[1, 2], json_files=None, report_ids=None, json_dir=None
        )
        self.command.main(args)
        expected_msg = messages.REPORT_SUCCESSFULLY_MERGED % {
            "id": "1",
            "prog_name": QPC_VAR_PROGRAM_NAME,
        }
        assert expected_msg in capsys.readouterr().out

    def test_detail_merge_error_job_ids(self, requests_mock, caplog):
        """Testing report merge error with scan job ids."""
        requests_mock.get(
            get_server_location() + SCAN_JOB_URI + "1/",
            status_code=200,
            json={"report_id": 1},
        )
        requests_mock.get(
            get_server_location() + SCAN_JOB_URI + "2/",
            status_code=200,
            json={"report_id": 2},
        )
        requests_mock.put(
            get_server_location() + ASYNC_MERGE_URI,
            status_code=400,
            json={"reports": ["SOME SERVER ERROR."]},
        )

        args = Namespace(
            scan_job_ids=[1, 2], json_files=None, report_ids=None, json_dir=None
        )
        caplog.set_level(logging.ERROR)
        with pytest.raises(SystemExit):
            self.command.main(args)
        assert caplog.messages[-1] == "SOME SERVER ERROR."

    def test_detail_merge_report_ids(self, requests_mock, capsys):
        """Testing report merge command with report ids."""
        requests_mock.put(
            get_server_location() + ASYNC_MERGE_URI, status_code=201, json={"id": 1}
        )
        args = Namespace(
            scan_job_ids=None, json_files=None, report_ids=[1, 2], json_dir=None
        )
        self.command.main(args)
        expected_msg = messages.REPORT_SUCCESSFULLY_MERGED % {
            "id": "1",
            "prog_name": QPC_VAR_PROGRAM_NAME,
        }
        assert expected_msg in capsys.readouterr().out

    def test_detail_merge_error_report_ids(self, requests_mock, caplog):
        """Testing report merge error with report ids."""
        requests_mock.put(
            get_server_location() + ASYNC_MERGE_URI,
            status_code=400,
            json={"reports": ["SOME SERVER ERROR."]},
        )
        args = Namespace(
            scan_job_ids=None, json_files=None, report_ids=[1, 2], json_dir=None
        )
        caplog.set_level(logging.ERROR)
        with pytest.raises(SystemExit):
            self.command.main(args)
        assert requests_mock.last_request.json() == {"reports": [1, 2]}
        assert caplog.messages[-1] == "SOME SERVER ERROR."

    def test_detail_merge_json_files(
        self, capsys, requests_mock, details1, gooddetails
    ):
        """Testing report merge command with json files."""
        requests_mock.post(
            get_server_location() + ASYNC_MERGE_URI, status_code=201, json={"id": 1}
        )

        args = Namespace(
            scan_job_ids=None,
            json_files=[details1, gooddetails],
            report_ids=None,
        )
        self.command.main(args)
        expected_msg = messages.REPORT_SUCCESSFULLY_MERGED % {
            "id": "1",
            "prog_name": QPC_VAR_PROGRAM_NAME,
        }
        assert expected_msg in capsys.readouterr().out

    @pytest.mark.xfail(reason="This is failing likely due to bug")
    def test_detail_merge_json_files_not_exist(
        self, details1, caplog, tmp_path, mocker
    ):
        """Testing report merge file not found error with json files."""
        non_exist_file = str(tmp_path / str(uuid4()))
        args = Namespace(
            scan_job_ids=None,
            json_files=[details1, non_exist_file],
            report_ids=None,
            json_dir=None,
        )
        caplog.set_level(logging.ERROR)
        with pytest.raises(SystemExit):
            self.command.main(args)
        # TODO: the following assertion is not being matched because the actual last
        # logging line is an error when attempting to connect to quipucords. This is
        # likely a bug because if qpc knows 'non_exist_file' doesn't exist, there's
        # no report to merge
        assert caplog.messages[-1] == messages.FILE_NOT_FOUND % non_exist_file

    def test_detail_merge_error_json_files(
        self, details1, not_json_file, caplog, requests_mock
    ):
        """Testing report merge error with json files."""
        requests_mock.post(
            get_server_location() + ASYNC_MERGE_URI,
            status_code=400,
            json={"reports": ["some error."]},
        )
        args = Namespace(
            scan_job_ids=None,
            json_files=[details1, not_json_file],
            report_ids=None,
            json_dir=None,
        )
        caplog.set_level(logging.ERROR)
        with pytest.raises(SystemExit):
            self.command.main(args)
        assert caplog.messages[-2:] == [
            f"Failed: {not_json_file} is not a JSON details report.",
            "some error.",
        ]

    def test_detail_merge_error_all_json_files(
        self, bad_details1, bad_details2, caplog
    ):
        """Testing report merge error with all bad json files."""
        args = Namespace(
            scan_job_ids=None,
            json_files=[bad_details1, bad_details2],
            report_ids=None,
            json_dir=None,
        )
        caplog.set_level(logging.ERROR)
        with pytest.raises(SystemExit):
            self.command.main(args)
        assert caplog.messages[-1] == messages.REPORT_JSON_DIR_ALL_FAIL

    def test_detail_merge_only_one_json_file(self, bad_details1, caplog):
        """Testing report merge error with only 1 json file."""
        args = Namespace(
            scan_job_ids=None,
            json_files=[bad_details1],
            report_ids=None,
            json_dir=None,
        )
        caplog.set_level(logging.ERROR)
        with pytest.raises(SystemExit):
            self.command.main(args)
        assert caplog.messages[-1] == messages.REPORT_JSON_FILES_HELP

    def test_detail_merge_error_no_args(self, mocker, capsys):
        """Testing report merge error with no arguments."""
        # using Namespace directly skips argparse builtin validations, requiring
        # us to patch sys.argv
        mocker.patch.object(sys, "argv", "qpc report merge".split())
        with pytest.raises(SystemExit):
            CLI().main()
        assert (
            "qpc report merge: error: one of the arguments --job-ids --report-ids "
            "--json-files --json-directory is required" in capsys.readouterr().err
        )

    @pytest.mark.xfail(reason="passing, but highlights a design flaw.")
    def test_detail_merge_error_too_few_args(self, caplog, requests_mock, capsys):
        """Testing report merge error with only 1 job id."""
        requests_mock.get(
            get_server_location() + SCAN_JOB_URI + "1/",
            status_code=200,
            json={"report_id": 42},
        )
        requests_mock.put(
            get_server_location() + ASYNC_MERGE_URI,
            status_code=400,
            json={"report": ["some error."]},
        )

        args = Namespace(
            scan_job_ids=[1], json_files=None, report_ids=None, json_dir=None
        )
        caplog.set_level(logging.ERROR)
        with pytest.raises(SystemExit):
            self.command.main(args)
        assert requests_mock.last_request.json() == {"reports": [42]}
        # qpc sent a request only with report 42 to quipucords - but should it?
        # in order to trigger a merge job at least 2 reports are required, which is
        # clearly not the case here. OTOH, this is a request that will fail on server
        # side, so it's not the worst design flaw here. But it is at least inconsistent
        # with other parameters like "json_dir", which will only make requests to the
        # server when at least 2 files are present.

    def test_detail_merge_json_directory(
        self,
        details1,
        details2,
        bad_details1,
        bad_details2,
        bad_details3,
        bad_details4,
        bad_details5,
        gooddetails,
        not_json_file,
        capsys,
        requests_mock,
        caplog,
    ):
        """Testing report merge command with json directory."""
        args = Namespace(
            scan_job_ids=None,
            json_files=None,
            report_ids=None,
            json_dir=[str(Path(details1).parent)],
        )
        requests_mock.post(
            get_server_location() + ASYNC_MERGE_URI, status_code=201, json={"id": 1}
        )

        self.command.main(args)
        expected_msg = messages.REPORT_SUCCESSFULLY_MERGED % {
            "id": "1",
            "prog_name": QPC_VAR_PROGRAM_NAME,
        }
        assert expected_msg in capsys.readouterr().out
        # ensure only good reports were pushed to server
        assert requests_mock.last_request.json() == {
            "report_type": "details",
            "sources": [
                {
                    "facts": ["A"],
                    "report_type": "details",
                    "report_version": "1.2.3+outer_version",
                    "server_id": "42",
                },
                {
                    "facts": ["B"],
                    "report_type": "details",
                    "report_version": "0.0.44.legacy",
                    "server_id": "8",
                },
            ],
        }
        # ensure bad reports were detected
        assert (
            f"Failed: {details2} is not a details report. Missing facts. "
            "Excluding from merge." in caplog.text
        )
        assert (
            f"Failed: {bad_details1} is not a details report. Missing sources. "
            "Excluding from merge." in caplog.text
        )
        assert (
            f"Failed: {bad_details2} is not a details report. Missing facts. "
            "Excluding from merge." in caplog.text
        )
        assert (
            f"Failed: {bad_details3} is not a details report. Missing facts. "
            "Excluding from merge." in caplog.text
        )
        assert f"Failed: {bad_details4} is not a JSON details report." in caplog.text
        assert (
            f"The file {bad_details5} contains invalid report type durham."
            in caplog.text
        )
        # ensure the non json file wan't detected
        assert not_json_file not in caplog.text

    def test_detail_merge_json_directory_error_dir_not_found(self, tmp_path, caplog):
        """Testing report merge command with json_dir parameter (notdir)."""
        doesnt_exist_path = tmp_path / "does-not-exist"

        args = Namespace(
            scan_job_ids=None,
            json_files=None,
            report_ids=None,
            json_dir=str(doesnt_exist_path),
        )
        with pytest.raises(SystemExit):
            self.command.main(args)
        assert (
            caplog.messages[-1]
            == messages.REPORT_JSON_DIR_NOT_FOUND % doesnt_exist_path
        )

    def test_detail_merge_json_directory_error_path_passed(self, bad_details1, caplog):
        """Testing report merge command with json_dir parameter (file)."""
        args = Namespace(
            scan_job_ids=None,
            json_files=None,
            report_ids=None,
            json_dir=bad_details1,
        )
        with pytest.raises(SystemExit):
            self.command.main(args)
        assert caplog.messages[-1] == messages.REPORT_JSON_DIR_NOT_FOUND % bad_details1

    def test_detail_merge_json_invalid_report_type_passed(self, caplog, bad_details5):
        """Testing report merge command bad report_type."""
        args = Namespace(
            scan_job_ids=None,
            json_files=None,
            report_ids=None,
            json_dir=bad_details5,
        )
        with pytest.raises(SystemExit):
            self.command.main(args)
        assert caplog.messages[-1] == messages.REPORT_JSON_DIR_NOT_FOUND % bad_details5

    def test_detail_merge_json_directory_no_detail_reports(self, tmp_path, caplog):
        """Testing report merge command with json_dir (no details)."""
        args = Namespace(
            scan_job_ids=None, json_files=None, report_ids=None, json_dir=str(tmp_path)
        )

        with pytest.raises(SystemExit):
            self.command.main(args)
        assert caplog.messages[-1] == messages.REPORT_JSON_DIR_ALL_FAIL
