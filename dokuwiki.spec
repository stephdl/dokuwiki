%define realversion 2017-02-19e 
%define version %(echo %{realversion} | sed -e 's/-//g')
%define releasenum 2

%if 0%{?fedora} >= 11 || 0%{?rhel} >= 5
%global useselinux 1
%else 
%global useselinux 0
%endif

Name:        dokuwiki
Version:     %{version}
Release:     %{releasenum}%{?dist}
Summary:     Standards compliant simple to use wiki
Group:       Applications/Internet
License:     GPLv2
URL:         http://www.dokuwiki.org/dokuwiki
Source:      http://download.dokuwiki.org/src/dokuwiki/%{name}-%{realversion}.tgz

BuildRoot:   %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:   noarch
Requires:    php
Requires:    php-gd
Requires:    php-imap
Requires:    php-ldap
Requires:    httpd

%description
DokuWiki is a standards compliant, simple to use Wiki, mainly aimed at creating 
documentation of any kind. It has a simple but powerful syntax which makes sure 
the data files remain readable outside the Wiki and eases the creation of 
structured texts. 

All data is stored in plain text files no database is required. 


%prep
%setup -q -n %{name}-%{realversion}

chmod a-x inc/lang/az/*.{txt,html}

mv -f conf/mysql.conf.php.example .

sed -i "s:'./data':'%{_localstatedir}/lib/%{name}/data':" conf/%{name}.php
sed -i "s:ALL        8:ALL        1:" conf/acl.auth.php.dist

# Use admin as default superuser
echo "\$conf['superuser'] = 'admin';" >> conf/local.php.dist

cat <<EOF >%{name}.httpd
# %{name}
# %{summary}
# %{version}
#

Alias /%{name} %{_datadir}/%{name}

<Directory %{_datadir}/%{name}>
    Options +FollowSymLinks
    <IfModule !mod_authz_core.c>
      Order Allow,Deny
      Allow from 127.0.0.1 ::1
    </IfModule>
    <IfModule mod_authz_core.c>
      Require ip 127.0.0.1 ::1
    </IfModule>
</Directory>

<Directory %{_datadir}/%{name}/inc>
    <IfModule !mod_authz_core.c>
      Order Deny,Allow
      Deny from all
    </IfModule>
    <IfModule mod_authz_core.c>
      Require all denied
    </IfModule>
</Directory>

<Directory %{_datadir}/%{name}/inc/lang>
    <IfModule !mod_authz_core.c>
      Order Deny,Allow
      Deny from all
    </IfModule>
    <IfModule mod_authz_core.c>
      Require all denied
    </IfModule>
</Directory>

<Directory %{_datadir}/%{name}/lib/_fla>
    <IfModule !mod_authz_core.c>
      Order allow,deny
      Deny from all
    </IfModule>
    <IfModule mod_authz_core.c>
      Require all denied
    </IfModule>
</Directory>

<Directory %{_sysconfdir}/%{name}>
    <IfModule !mod_authz_core.c>
      Order Deny,Allow
      Deny from all
    </IfModule>
    <IfModule mod_authz_core.c>
      Require all denied
    </IfModule>
</Directory>
<Directory %{_datadir}/%{name}/conf>
    <IfModule !mod_authz_core.c>
      Order allow,deny
      Deny from all
    </IfModule>
    <IfModule mod_authz_core.c>
      Require all denied
    </IfModule>
</Directory>

<Directory %{_localstatedir}/lib/%{name}/>
    <IfModule !mod_authz_core.c>
      Order Deny,Allow
      Deny from all
    </IfModule>
    <IfModule mod_authz_core.c>
      Require all denied
    </IfModule>
</Directory>
<Directory %{_datadir}/%{name}/data>
    <IfModule !mod_authz_core.c>
      Order allow,deny
      Deny from all
    </IfModule>
    <IfModule mod_authz_core.c>
      Require all denied
    </IfModule>
</Directory>

EOF

cat <<EOF >DOKUWIKI-SELINUX.README
%{name}-selinux
====================

This package configures dokuwiki to run in
SELinux enabled environments

EOF

%build
# nothing to do here

%install
rm -rf $RPM_BUILD_ROOT
install -d -p $RPM_BUILD_ROOT%{_sysconfdir}/%{name}
install -d -p $RPM_BUILD_ROOT%{_sysconfdir}/httpd/conf.d
install -d -p $RPM_BUILD_ROOT%{_datadir}/%{name}
install -d -p $RPM_BUILD_ROOT%{_datadir}/%{name}/bin
install -d -p $RPM_BUILD_ROOT%{_localstatedir}/lib/%{name}
mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/lib/%{name}/data/{index,tmp,media,attic,pages,cache,meta,locks,media_attic,media_meta}
rm -f install.php
rm -f inc/.htaccess
rm -f inc/lang/.htaccess
rm -f lib/_fla/{.htaccess,README}
rm -f lib/plugins/revert/lang/sk/intro.txt
cp -rp data/pages/* $RPM_BUILD_ROOT%{_localstatedir}/lib/%{name}/data/pages/
cp -rp conf/* $RPM_BUILD_ROOT%{_sysconfdir}/%{name}
cp -rp bin/*  $RPM_BUILD_ROOT%{_datadir}/%{name}/bin
cp -rp lib  $RPM_BUILD_ROOT%{_datadir}/%{name}/
cp -rp inc  $RPM_BUILD_ROOT%{_datadir}/%{name}/
cp -rp vendor $RPM_BUILD_ROOT%{_datadir}/%{name}/
install -p -m0644 VERSION $RPM_BUILD_ROOT%{_datadir}/%{name}
install -p -m0644 *.php $RPM_BUILD_ROOT%{_datadir}/%{name}
install -p -m0644 %{name}.httpd $RPM_BUILD_ROOT%{_sysconfdir}/httpd/conf.d/%{name}.conf

pushd $RPM_BUILD_ROOT%{_sysconfdir}/%{name}
for d in *.dist; do
    d0=`basename $d .dist`
    if [ ! -f "$d0" ]; then
        mv -f $d $d0
    fi
done
popd

pushd $RPM_BUILD_ROOT%{_datadir}/%{name}
    ln -sf ../../../etc/%name conf
    ln -sf ../../../%{_localstatedir}/lib/%{name}/data/ data
popd

%clean
rm -rf $RPM_BUILD_ROOT

%post
%if %{useselinux}
(
semanage fcontext -a -t httpd_sys_content_t '%{_sysconfdir}/%{name}(/.*)?'
semanage fcontext -a -t httpd_sys_content_t '%{_datadir}/%{name}(/.*)?'
semanage fcontext -a -t httpd_sys_content_t '%{_datadir}/%{name}/lib/plugins(/.*)?'
restorecon -R '%{_sysconfdir}/%{name}'
restorecon -R '%{_datadir}/%{name}'
restorecon -R '%{_datadir}/%{name}/lib/plugins'
) &> /dev/null || :
%endif


%postun
%if %{useselinux}
(
if [ $1 -eq 0 ] ; then
semanage fcontext -d -t httpd_sys_content_t '%{_sysconfdir}/%{name}(/.*)?'
semanage fcontext -d -t httpd_sys_content_t '%{_datadir}/%{name}(/.*)?'
semanage fcontext -d -t httpd_sys_content_t '%{_datadir}/%{name}/lib/plugins(/.*)?'
fi
) &> /dev/null || :
%endif

%files
%defattr(-,root,root,-)
%doc COPYING README mysql.conf.php.example DOKUWIKI-SELINUX.README
%config(noreplace) %{_sysconfdir}/httpd/conf.d/%{name}.conf
%config(noreplace) %attr(0644,apache,apache) %{_sysconfdir}/%{name}/*
%dir %attr(0755,apache,apache) %{_sysconfdir}/%{name}
%attr(0755,apache,apache) %{_datadir}/%{name}/bin/*.php
%dir %{_datadir}/%{name}
%{_datadir}/%{name}/conf
%{_datadir}/%{name}/data
%{_datadir}/%{name}/*.php
%{_datadir}/%{name}/VERSION
%dir %{_datadir}/%{name}/lib
%{_datadir}/%{name}/lib/exe
%{_datadir}/%{name}/lib/images
%{_datadir}/%{name}/lib/index.html
%{_datadir}/%{name}/lib/scripts
%{_datadir}/%{name}/lib/styles
%{_datadir}/%{name}/lib/tpl
#%{_datadir}/%{name}/lib/_fla
%attr(0755,apache,apache) %dir %{_datadir}/%{name}/lib/plugins
%{_datadir}/%{name}/lib/plugins/*
%{_datadir}/%{name}/inc
%{_datadir}/%{name}/vendor
%dir %{_localstatedir}/lib/%{name}
%attr(0750,apache,apache) %dir %{_localstatedir}/lib/%{name}/data
%attr(0755,apache,apache) %dir %{_localstatedir}/lib/%{name}/data/media
%attr(0755,apache,apache) %dir %{_localstatedir}/lib/%{name}/data/media_attic
%attr(0755,apache,apache) %dir %{_localstatedir}/lib/%{name}/data/media_meta
%attr(0755,apache,apache) %dir %{_localstatedir}/lib/%{name}/data/attic
%attr(0755,apache,apache) %dir %{_localstatedir}/lib/%{name}/data/cache
%attr(0755,apache,apache) %dir %{_localstatedir}/lib/%{name}/data/meta
%attr(0755,apache,apache) %dir %{_localstatedir}/lib/%{name}/data/locks
%attr(0755,apache,apache) %dir %{_localstatedir}/lib/%{name}/data/tmp
%attr(0755,apache,apache) %dir %{_localstatedir}/lib/%{name}/data/index
%attr(0755,apache,apache) %dir %{_localstatedir}/lib/%{name}/data/pages
%attr(0755,apache,apache) %dir %{_localstatedir}/lib/%{name}/data/pages/playground
%attr(0755,apache,apache) %dir %{_localstatedir}/lib/%{name}/data/pages/wiki
%attr(0644,apache,apache) %{_localstatedir}/lib/%{name}/data/pages/*/*

%changelog
* Sat Sep 02 2017 Stephane de Labrusse <stephdl@de-labrusse.fr> 2017-02-19e-1
- Update to 2017-02-19e "Frusterick Manners"

* Mon Jul 03 2017 Stephane de Labrusse <stephdl@de-labrusse.fr> 2017-02-19b-2
- add apache permission on /data/pages/playground

* Sat Mar 11 2017 Stephane de Labrusse <stephdl@de-labrusse.fr> 2017-02-19b-1
- Update to 2017-02-19b "Frusterick Manners"

* Tue Feb 21 2017 Stephane de Labrusse <stephdl@de-labrusse.fr> 2017-02-19a-1
- Update to 2017-02-19a "Frusterick Manners"
 
* Thu Oct 20 2016 Stephane de Labrusse <stephdl@de-labrusse.fr> 2016-06-26a-1
- Update to 2016-06-26a "Elenor of Tsort"

* Thu Oct 22 2015 Daniel Berteaud <daniel@firewall-services.com> - 20150810a-3
- Fix SELinux labels

* Mon Oct 19 2015 Daniel Berteaud <daniel@firewall-services.com> - 20150810a-2
- Adapt default conf for apache 2.4

* Tue Sep 1 2015 Daniel Berteaud <daniel@firewall-services.com> - 20150810a-1
- Update to 2015-08-10a

* Fri Mar 20 2015 Daniel Berteaud <daniel@firewall-services.com> - 20140929d-1
- Update to 2014-09-29d

* Thu Feb 26 2015 Daniel Berteaud <daniel@firewall-services.com> - 20140929c-1
- Update to 2014-09-29c

* Thu Dec 4 2014 Daniel Berteaud <daniel@firewall-services.com> - 20140929b-1
- Update to 2014-09-29b

* Fri Oct 17 2014 Daniel Berteaud <daniel@firewall-services.com> - 20140929a-2
- Put the VERSION file in the doc root

* Tue Oct 14 2014 Daniel Berteaud <daniel@firewall-services.com> - 20140929a-1
- Update to 2014-09-29a

* Fri Jun 27 2014 Daniel Berteaud <daniel@firewall-services.com> - 20140505a-1
- update to 2014-05-05a (security fix)

* Tue May 6 2014 Daniel Berteaud <daniel@firewall-services.com> - 20140505-1
- update to 2014-05-05

* Mon Dec 9 2013 Daniel Berteaud <daniel@firewall-services.com> - 20131208-1
- update to 2013-12-08

* Fri Nov 15 2013 Daniel Berteaud <daniel@firewall-services.com> - 20130510a-4
- Cleanup the spec file

* Tue Sep 3 2013 Daniel Berteaud <daniel@firewall-services.com> - 20130510a-3
- Add a dependency on php

* Wed Aug 28 2013 Daniel Berteaud <daniel@firewall-services.com> - 20130510a-2
- Fix permission on data dir and playground page

* Wed Aug 21 2013 Daniel Berteaud <daniel@firewall-services.com> - 20130510a-1
- update to 2013-05-10a

* Wed May 15 2013 Daniel Berteaud <daniel@firewall-services.com> - 20130510-1
- update to 2013-05-10

* Mon Oct 15 2012 Daniel Berteaud <daniel@firewall-services.com> - 20121013-1
- update to 2012-10-13

* Tue Sep 11 2012 Daniel Berteaud <daniel@firewall-services.com> - 20120910-1
- update to 2012-09-10

* Sun Jul 15 2012 Daniel Berteaud <daniel@firewall-services.com> - 20120125b-1
- update to 2012-01-25b

* Mon Apr 23 2012 Daniel Berteaud <daniel@firewall-services.com> - 20120125a-4
- upstream upgrade to 2012-01-25a

* Fri Jan 27 2012  Daniel Berteaud <daniel@firewall-services.com> - 20120125-4
- Upstream upgrade to 2012-01-25

* Mon Dec 19 2011 Daniel Berteaud <daniel@firewall-services.com> - 20110525a-3
- Link data dir to the real path

* Thu Sep 29 2011 Daniel Berteaud <daniel@firewall-services.com> - 20110525a-2
- Don't exit with error if SELinux is disabled

* Fri Jul 08 2011 Daniel Berteaud <daniel@firewall-services.com> - 20110525a-1
- Upstream upgrade to 2011-05-25a (based on EPEL RPM from Andrew Colin Kissa)

