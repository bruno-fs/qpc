%{!?python3_sitelib: %define python3_sitelib %(%{__python3} -c "import site; print(site.getsitepackages()[0])")}

Name: qpc
Version: 1.0.0
Release: 1%{?dist}
Summary: A tool for discovery and inspection of an IT environment.

Group: Applications/Internet
License: GPLv3
URL: http://github.com/quipucords/qpc
Source0: http://github.com/quipucords/qpc/archive/refs/heads/master.zip
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildArch: noarch

%if 0%{?el7}
%global pyver 36
%else
%global pyver 3
%endif

BuildRequires: make
BuildRequires: pandoc
BuildRequires: python%{pyver}-devel
BuildRequires: python%{pyver}-setuptools
Requires: python%{pyver}
Requires: python%{pyver}-requests
Requires: python%{pyver}-cryptography


%description
QPC is tool for discovery and inspection of an IT environment.

%prep
%setup -q

%build
%{__python3} setup.py build

%install
rm -rf $RPM_BUILD_ROOT
%{__python3} setup.py install --skip-build --root $RPM_BUILD_ROOT

# Manpage
make manpage
install -D -p -m 644 docs/qpc.1 $RPM_BUILD_ROOT%{_mandir}/man1/qpc.1

%files
%defattr(-,root,root,-)
%doc README.md AUTHORS.md
%{python3_sitelib}/*
%{_mandir}/man1/qpc.1.gz

%changelog
* Wed Jul 27 2022 Nicole Aragao <naragao@redhat.com> 1.0.0
- Add Insights config, add_login and publish subcommands
- Deprecate insights upload command
* Thu Mar 17 2022 Nicole Aragao <naragao@redhat.com> 0.10.0
- Drop support for Python < 3.6
- Update libraries
- Extends supported Python versions from 3.6 to 3.9
* Fri Dec 13 2019 Kevan Holdaway <kholdawa@redhat.com> 0.9.4-1
- Change master branch version to 0.9.4. <kholdawa@redhat.com>
* Wed Dec 11 2019 Kevan Holdaway <kholdawa@redhat.com> 0.9.3-1
- Bump version to 0.9.3 for master branch. <kholdawa@redhat.com>
- Added password arg to server login. <cmyers@redhat.com>
- Expose endpoint to upload a details report. <kholdawa@redhat.com>
- Added --mask flag to mask sensitive data in reports. <aaiken@redhat.com>
* Thu Nov 14 2019 Ashley Aiken <aaiken@redhat.com> 0.9.2-1
- Bump version to 0.9.2 for master branch
- Dependency version updates
- Improve error handling when server is not configured
- Improve error handling http connection errors
* Mon Aug 19 2019 Kevan Holdaway <kholdawa@redhat.com> 0.9.1-1
- Added RHEL 8 support. <cmyers@redhat.com>
- Fixed help text for satellite source command. <aaiken@redhat.com>
* Thu Jun 6 2019 Kevan Holdaway <kholdawa@redhat.com> 0.9.0-1
- Add qpc report insights command to qpc. <kholdawa@redhat.com>
- Update qpc insights upload command to use new QPC Insights report format. <kholdawa@redhat.com>
- Remove deprecated CLI summary/detail commands. <cmyers@redhat.com>
- Remove max concurrent defaults for scanning. <cmyers@redhat.com>
- Add CLI flag to disable authentication. <kholdawa@redhat.com>
- Modify spec file for RHEL 7 python36. <kholdawa@redhat.com>
- Added extension check for file download commands.<kholdawa@redhat.com>
* Wed Jan 23 2019 Ashley Aiken <aaiken@redhat.com> 0.0.46-1
- Add deployment report verification to qpc insights upload command. <aaiken@redhat.com>
- Add qpc insights commands. <cmyers@redhat.com>
- Change qpc server default port to 9443. <cmyers@redhat.com>
- Add qpc report download command. <cmyers@redhat.com>
* Fri Nov 2 2018 Cody Myers <cmyers@redhat.com> 0.0.45-1
- Deprecate summary and detail report commands. <kholdawa@redhat.com>
- Add server status command to QPC. <aaiken@redhat.com>
- Add async report merge and merge status commands. <cmyers@redhat.com>
* Fri Sep 7 2018 Cecilia Carter <cecarter@redhat.com> 0.0.44-1
- Add JBoss Web Server detection to QPC
* Wed Jul 18 2018 Cecilia Carter <cecarter@redhat.com> 0.0.43-1
- Added ability to exlude ip addresses from network scan via CLI
* Fri May 4 2018 Kevan Holdaway <kholdawa@redhat.com> 0.0.42-1
- Enable merging reports from scan job ids, report ids, and json details report files.<aaiken@redhat.com>
- Clean up the CLI tests for credential. <aaiken@redhat.com>
- Enable editing the disable-ssl option for a source. <aaiken@redhat.com>
- Allow true/false for boolean values in source options. <kholdawa@redhat.com>
- Update man page to indicate ssl options cannot be used with network sources. <kholdawa@redhat.com>
* Wed Mar 14 2018 Ashley Aiken <aaiken@redhat.com> 0.0.41-1
- Fix scan list pagination support
* Thu Mar 8 2018 Ashley Aiken <aaiken@redhat.com> 0.0.40-1
- Flip disable-optional-products defaults. <aaiken@redhat.com>
- Remove satellite version from source options. <chambrid@redhat.com>
* Mon Mar 5 2018 Ashley Aiken <aaiken@redhat.com> 0.0.39-1
- Fix partial update for scan. <aaiken@redhat.com>
- Improve error handling for 500 response codes. <aaiken@redhat.com>
- Add report identifier as a lookup option for reports. <kholdawa@redhat.com>
* Fri Mar 2 2018 Ashley Aiken <aaiken@redhat.com> 0.0.38-1
- Remove scan status subcommand. <aaiken@redhat.com>
- Add scan support for exteneded product search. <aaiken@redhat.com>
- Enable ability to merge results of scan jobs. <kholdawa@redhat.com>
* Thu Mar 1 2018 Kevan Holdaway <kholdawa@redhat.com> 0.0.37-1
- Make scan options optional.
* Wed Feb 28 2018 Ashley Aiken <aaiken@redhat.com> 0.0.36-1
- Improve logging to capture command arguments. <aaiken@redhat.com>
- Improve logging to capture request method and endpoint. <aaiken@redhat.com>
- Fix report commands after scan job updates. <chambrid@redhat.com>
* Tue Feb 27 2018 Ashley Aiken <aaiken@redhat.com> 0.0.35-1
- Fix max-concurrency default for editing a scan.
* Fri Feb 23 2018 Ashley Aiken <aaiken@redhat.com> 0.0.34-1
- View all scan jobs for a scan by scan name.
- View scan job by identifier.
- Add feedback message to server config command.
* Thu Feb 22 2018 Ashley Aiken <aaiken@redhat.com> 0.0.33-1
- Add scan job support to command line for listing and clearing.
* Wed Feb 21 2018 Ashley Aiken <aaiken@redhat.com> 0.0.32-1
- Add scan edit support to command line and man documentation.
* Tue Feb 20 2018 Ashley Aiken <aaiken@redhat.com> 0.0.31-1
- Add scan creation, listing, showing, and start support to command line.
* Fri Feb 16 2018 Chris Hambridge <chambrid@redhat.com> 0.0.30-1
- Added logout subcommand to log out of server and remove token.
* Thu Feb 15 2018 Chris Hambridge <chambrid@redhat.com> 0.0.29-1
- Enable token expiration support in command line.
* Wed Feb 14 2018 Chris Hambridge <chambrid@redhat.com> 0.0.28-1
- Fix login issue required before command usage.
* Tue Feb 13 2018 Kevan Holdaway <kholdawa@redhat.com> 0.0.27-1
- Ensure ordering is preserved for source credentials from the command line.
- Require server configuration before other commands are executed.
* Wed Feb 7 2018 Chris Hambridge <chambrid@redhat.com> 0.0.26-1
- Added pagination support for credentials.
- Added pagination support for sources.
- Added pagination support for scans.
* Mon Feb 5 2018 Kevan Holdaway <kholdawa@redhat.com> 0.0.25-1
- Added detail report command with JSON or CSV output. <kholdawa@redhat.com>
- Add SSL options for vcenter sources. <chambrid@redhat.com>
- Add SSL options for satellite sources. <chambrid@redhat.com>
* Sun Feb 4 2018 Kevan Holdaway <kholdawa@redhat.com> 0.0.24-1
- Add report subcommand to provide summary report with JSON or CSV output.
* Fri Feb 2 2018 Chris Hambridge <chambrid@redhat.com> 0.0.23-1
- Check for client token before executing other subcommands.
* Wed Jan 31 2018 Chris Hambridge <chambrid@redhat.com> 0.0.22-1
- Enable HTTPS commnication support for the command line.
* Tue Jan 30 2018 Ashley Aiken <aaiken@redhat.com> 0.0.21-1
- Enhance scans with optional product support for JBoss EAP, Fuse, and BRMS.
* Thu Jan 25 2018 Chris Hambridge <chambrid@redhat.com> 0.0.20-1
- Removed dependency on pyxdg to support RHEL6 installation.
* Mon Jan 22 2018 Ashley Aiken <aaiken@redhat.com> 0.0.19-1
- Added become-method, become-user, and become-password support to credentials.
* Wed Jan 17 2018 Chris Hambridge <chambrid@redhat.com> 0.0.18-1
- Added support for satellite sources and options.
* Tue Jan 16 2018 Chris Hambridge <chambrid@redhat.com> 0.0.17-1
- Added support for satellite credentials.
* Mon Jan 15 2018 Chris Hambridge <chambrid@redhat.com> 0.0.16-1
- Enhanced command line with token authentication support.
* Thu Jan 11 2018 Ashley Aiken <aaiken@redhat.com> 0.0.15-1
- Incorporates partial update to allow for editing credentials.
* Sat Dec 16 2017 Chris Hambridge <chambrid@redhat.com> 0.0.14-1
- Add subcommand to display scan results
* Fri Dec 15 2017 Chris Hambridge <chambrid@redhat.com> 0.0.13-1
- Support scanning with multiple sources via scan start <chambrid@redhat.com>
- List scans by type and status <kholdawa@redhat.com>
* Thu Dec 7 2017 Kevan Holdaway <kholdawa@redhat.com> 0.0.12-1
- Enhance sources to support vcenter type along with existing network type.
- List sources by source type
- List credentials by credential type
* Wed Dec 6 2017 Kevan Holdaway <kholdawa@redhat.com> 0.0.11-1
- Enhance credentials to support vcenter type along with existing network type.
* Mon Dec 4 2017 Kevan Holdaway <kholdawa@redhat.com> 0.0.10-1
- Update subcommand from auth to cred
- Added error handling support for various Django Rest Framework outputs
* Fri Dec 1 2017 Kevan Holdaway <kholdawa@redhat.com> 0.0.9-1
- Update subcommand from profile to source
- Altered endpoint to sources and preparing multiple types.
* Thu Nov 30 2017 Kevan Holdaway <kholdawa@redhat.com> 0.0.8-1
- Update credentials endpoint to prepare multiple types.
* Wed Nov 29 2017 Kevan Holdaway <kholdawa@redhat.com> 0.0.7-1
- Enhancement to support Python 3.4, 3.5, and 3.6.
* Tue Nov 21 2017 Kevan Holdaway <kholdawa@redhat.com> 0.0.6-1
- Add server configuration command.
* Thu Nov 9 2017 Chris Hambridge <chambrid@redhat.com> 0.0.5-1
- Add capability to pause, cancel, and restart scans.
* Thu Nov 2 2017 Chris Hambridge <chambrid@redhat.com> 0.0.4-1
- Add handling for sshkeys with passphrase.
- Improve linting and code documentation.
* Wed Nov 1 2017 Chris Hambridge <chambrid@redhat.com> 0.0.3-1
- Add max_concurrency flag to the scan start command.
* Tue Oct 31 2017 Chris Hambridge <chambrid@redhat.com> 0.0.2-1
- Consolidate messages for content review.
* Tue Oct 17 2017 Chris Hambridge <chambrid@redhat.com> 0.0.1-1
- Initial release of quipucords command line.
- Allows credential management for hosts.
- Enables source management.
- Start, list and show scan operations.
