Summary: Simple service discovery for Apache Mesos clusters
Name: surok
Version: 0.7.4.1
Release: 1
License: BSD
Group: admin
URL: https://github.com/Difrex/surok
Source0: surok.tar.gz
BuildArch: noarch
Requires: python34
# BuildRoot: %{_tmppath}/%{name}-%{release}-root

%description
Simple service discovery for Apache Mesos clusters

%prep
%setup -q

%build

%install
mkdir -p %{buildroot}/opt/surok/surok
install -p -m 644 /root/rpmbuild/BUILD/surok-%{version}/surok/__init__.py %{buildroot}/opt/surok/surok
install -p -m 644 /root/rpmbuild/BUILD/surok-%{version}/surok/logger.py %{buildroot}/opt/surok/surok
install -p -m 644 /root/rpmbuild/BUILD/surok-%{version}/surok/system.py %{buildroot}/opt/surok/surok
install -p -m 644 /root/rpmbuild/BUILD/surok-%{version}/surok/discovery.py %{buildroot}/opt/surok/surok
install -p -m 644 /root/rpmbuild/BUILD/surok-%{version}/surok/templates.py %{buildroot}/opt/surok/surok
install -p -m 644 /root/rpmbuild/BUILD/surok-%{version}/surok.py %{buildroot}/opt/surok
mkdir -p %{buildroot}/etc/surok/{conf,conf.d,templates}
install -p -m 644 /root/rpmbuild/BUILD/surok-%{version}/conf/surok.json %{buildroot}/etc/surok/conf
install -p -m 644 /root/rpmbuild/BUILD/surok-%{version}/conf.d/selfcheck.json %{buildroot}/etc/surok/conf.d
install -p -m 644 /root/rpmbuild/BUILD/surok-%{version}/templates/selfcheck.jj2 %{buildroot}/etc/surok/templates
install -p -m 644 /root/rpmbuild/BUILD/surok-%{version}/requriments.txt %{buildroot}/opt/surok


%clean
rm -rf $RPM_BUILD_ROOT

%post
cd /opt/surok && pip3 install -r requriments.txt

%files
/opt/surok/surok/__init__.py
/opt/surok/surok/__init__.pyc
/opt/surok/surok/__init__.pyo
/opt/surok/surok/logger.py
/opt/surok/surok/logger.pyc
/opt/surok/surok/logger.pyo
/etc/surok/conf/surok.json
/opt/surok/surok.py
/opt/surok/surok.pyc
/opt/surok/surok.pyo
/opt/surok/surok/discovery.py
/opt/surok/surok/discovery.pyc
/opt/surok/surok/discovery.pyo
/opt/surok/surok/system.py
/opt/surok/surok/system.pyc
/opt/surok/surok/system.pyo
/opt/surok/surok/templates.py
/opt/surok/surok/templates.pyc
/opt/surok/surok/templates.pyo
/etc/surok/conf.d/selfcheck.json
/etc/surok/templates/selfcheck.jj2
/opt/surok/requriments.txt
%defattr(-,root,root,-)
%doc


%changelog
* Mon Nov 14 2016 Denis Zheleztsov <difrex.punk@gmail.com> - 
- Initial build.

