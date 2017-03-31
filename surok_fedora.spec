Summary: Simple service discovery for Apache Mesos clusters
Name: surok
Version: 0.8.1
Release: 1.fc24
License: BSD
Group: admin
URL: https://github.com/Surkoveds/surok
Source0: surok.tar.gz
BuildArch: noarch
Requires: python3-requests, python3-dns, python3-memcached, python3-jinja2
# BuildRoot: %{_tmppath}/%{name}-%{release}-root

%description
Simple service discovery for Apache Mesos clusters

%prep
%setup -q

%build

%install
mkdir -p %{buildroot}/opt/surok/surok
install -p -m 644 /root/rpmbuild/BUILD/surok-%{version}/surok/__init__.py %{buildroot}/opt/surok/surok
install -p -m 644 /root/rpmbuild/BUILD/surok-%{version}/surok/apps.py %{buildroot}/opt/surok/surok
install -p -m 644 /root/rpmbuild/BUILD/surok-%{version}/surok/config.py %{buildroot}/opt/surok/surok
install -p -m 644 /root/rpmbuild/BUILD/surok-%{version}/surok/discovery.py %{buildroot}/opt/surok/surok
install -p -m 644 /root/rpmbuild/BUILD/surok-%{version}/surok/logger.py %{buildroot}/opt/surok/surok
install -p -m 644 /root/rpmbuild/BUILD/surok-%{version}/surok/store.py %{buildroot}/opt/surok/surok
install -p -m 644 /root/rpmbuild/BUILD/surok-%{version}/surok/system.py %{buildroot}/opt/surok/surok
install -p -m 644 /root/rpmbuild/BUILD/surok-%{version}/surok/templates.py %{buildroot}/opt/surok/surok
install -p -m 644 /root/rpmbuild/BUILD/surok-%{version}/surok.py %{buildroot}/opt/surok
mkdir -p %{buildroot}/etc/surok/{conf,conf.d,templates}
install -p -m 644 /root/rpmbuild/BUILD/surok-%{version}/conf/surok.json %{buildroot}/etc/surok/conf
mkdir -p %{buildroot}/usr/share/surok/{conf,conf.d,templates}
install -p -m 644 /root/rpmbuild/BUILD/surok-%{version}/conf/surok_07.json %{buildroot}/usr/share/surok/conf
install -p -m 644 /root/rpmbuild/BUILD/surok-%{version}/conf/surok_08.json %{buildroot}/usr/share/surok/conf
install -p -m 644 /root/rpmbuild/BUILD/surok-%{version}/conf/surok_check.json %{buildroot}/usr/share/surok/conf
install -p -m 644 /root/rpmbuild/BUILD/surok-%{version}/conf.d/self_check.json %{buildroot}/usr/share/surok/conf.d
install -p -m 644 /root/rpmbuild/BUILD/surok-%{version}/conf.d/marathon_check.json %{buildroot}/usr/share/surok/conf.d
install -p -m 644 /root/rpmbuild/BUILD/surok-%{version}/templates/selfcheck.jj2 %{buildroot}/usr/share/surok/templates
install -p -m 644 /root/rpmbuild/BUILD/surok-%{version}/requriments.txt %{buildroot}/opt/surok

%clean
rm -rf $RPM_BUILD_ROOT

%files
/etc/surok/conf/surok.json
/opt/surok/surok.py
/opt/surok/surok/__init__.py
/opt/surok/surok/apps.py
/opt/surok/surok/config.py
/opt/surok/surok/discovery.py
/opt/surok/surok/logger.py
/opt/surok/surok/store.py
/opt/surok/surok/system.py
/opt/surok/surok/templates.py
/usr/share/surok/conf/surok_07.json
/usr/share/surok/conf/surok_08.json
/usr/share/surok/conf/surok_check.json
/usr/share/surok/conf.d/self_check.json
/usr/share/surok/conf.d/marathon_check.json
/usr/share/surok/templates/selfcheck.jj2
%defattr(-,root,root,-)
%doc


%changelog
* Tue Feb  7 2017 Denis Zheleztsov <difrex.punk@gmail.com>
- New major release
- Discovery over marathon api
* Mon Nov 14 2016 Denis Zheleztsov <difrex.punk@gmail.com> - 
- Initial build.

