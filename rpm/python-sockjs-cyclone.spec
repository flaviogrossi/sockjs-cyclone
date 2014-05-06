%if ! (0%{?fedora} > 12 || 0%{?rhel} > 5)
%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
%endif

Name:           python-sockjs-cyclone
Version:        1.0.2
Release:        1%{?dist}
Summary:        SockJS server support for the Cyclone web server
Group:          Development/Libraries
License:        MIT
URL:            https://github.com/flaviogrossi/sockjs-cyclone
Source0:        %{name}-%{version}.tar.gz

BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:      noarch
BuildRequires:  python-devel
BuildRequires:  python-setuptools

Requires:       python
Requires:       python-simplejson
Requires:       python-twisted-cyclone

%description
SockJS-Cyclone is a pure Python server implementation for the SockJS protocol
running on the Cyclone web server.

%prep
%setup

%build
%{__python} setup.py build

%install
rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install --skip-build --root $RPM_BUILD_ROOT 

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
%dir %{python_sitelib}/sockjs/
%{python_sitelib}/sockjs/*
%{python_sitelib}/sockjs*egg-info

%changelog
* Sun Nov 24 2013 Flavio Grossi <flaviogrossi@gmail.com> 
- Version 1.0.2

* Sun Nov 3 2013 Flavio Grossi <flaviogrossi@gmail.com> 
- Version 1.0.1

* Fri Nov 1 2013 Flavio Grossi <flaviogrossi@gmail.com> 
- First stable release, 1.0.0

* Wed Jun 6 2012 Flavio Grossi <flaviogrossi@gmail.com> 
- First rpm release
