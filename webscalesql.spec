# TODO
# - fix openssl detect: -DWITH_SSL=%{?with_ssl:system}%{!?with_ssl:no}
# - system zlib -DWITH_ZLIB=system
#
# Conditional build:
%bcond_without	ssl		# OpenSSL support

%define		gitrev	004b6b3
%define		basever	5.6.23
# git log %{gitrev}..webscalesql-5.6 | grep -c ^commit
%define		revs	14
Summary:	WebScaleSQL, based upon the MySQL community releases
Name:		webscalesql
Version:	%{basever}.%{revs}
Release:	0.1
License:	GPL + MySQL FLOSS Exception
Group:		Applications/Databases
Source0:	https://github.com/webscalesql/webscalesql-5.6/archive/%{gitrev}/%{name}-5.6-%{gitrev}.tar.gz
# Source0-md5:	5ee76824913ff96ba70b68d8aeb50e49
Patch0:		%{name}-5.6-build.patch
URL:		http://webscalesql.org/
BuildRequires:	cmake >= 2.6
BuildRequires:	libaio-devel
BuildRequires:	libstdc++-devel
%{?with_ssl:BuildRequires:	openssl-devel >= 0.9.7d}
BuildRequires:	readline-devel >= 6.2
BuildRequires:	rpmbuild(macros) >= 1.597
BuildRequires:	zlib-devel
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
WebScaleSQL is an open source database management system (DBMS)
created as a software branch of WebScaleSQL 5.6.

%package libs
Summary:	Shared libraries for WebScaleSQL
Summary(pl.UTF-8):	Biblioteki współdzielone WebScaleSQL
Group:		Libraries

%description libs
Shared libraries for WebScaleSQL.

%description libs -l pl.UTF-8
Biblioteki współdzielone WebScaleSQL.

%package devel
Summary:	WebScaleSQL - development header files and other files
Group:		Development/Libraries
Requires:	%{name}-libs = %{version}-%{release}
%{?with_ssl:Requires: openssl-devel}
Requires:	zlib-devel
Conflicts:	mysql-devel

%description devel
This package contains the development header files and other files
necessary to develop WebScaleSQL client applications.

%package static
Summary:	WebScaleSQL static libraries
Group:		Development/Libraries
Requires:	%{name}-devel = %{version}-%{release}
Conflicts:	mysql-devel

%description static
WebScaleSQL static libraries.

%prep
%setup -qc
mv webscalesql-5.6-*/* .
%patch0 -p1

# to get these files rebuilt
[ -f sql/sql_yacc.cc ] && %{__rm} sql/sql_yacc.cc
[ -f sql/sql_yacc.h ] && %{__rm} sql/sql_yacc.h

%build
. ./VERSION
version=$MYSQL_VERSION_MAJOR.$MYSQL_VERSION_MINOR.$MYSQL_VERSION_PATCH${MYSQL_VERSION_EXTRA+$MYSQL_VERSION_EXTRA}
test "$version" = "%{basever}"

install -d build
cd build

  # XXX: MYSQL_UNIX_ADDR should be in cmake/* but webscalesql_version is included before
  # XXX: install_layout so we can't just set it based on INSTALL_LAYOUT=RPM

%cmake .. \
	%{?debug:-DWITH_DEBUG=ON} \
	-DINSTALL_LAYOUT=RPM \
	-DCOMPILATION_COMMENT="WebScaleSQL Server (GPL)" \
	-DFEATURE_SET="community" \
	-DMYSQL_SERVER_SUFFIX="" \
	-DMYSQL_UNIX_ADDR=/var/lib/mysql/mysql.sock \
	-DWITH_INNODB_MEMCACHED=ON \
	-DENABLE_MEMCACHED_SASL=OFF \
	-DWITH_SSL=bundled \
	-DWITH_UNIT_TESTS=OFF \
	-DWITHOUT_SERVER=ON \
	%{nil}

%{__make}

%install
rm -rf $RPM_BUILD_ROOT
%{__make} -C build install \
	DESTDIR=$RPM_BUILD_ROOT

# remove all non-client stuff
mv $RPM_BUILD_ROOT%{_bindir}/{,.}mysql_config
%{__rm} -r $RPM_BUILD_ROOT%{_bindir}/*
%{__rm} -r $RPM_BUILD_ROOT%{_datadir}
%{__rm} $RPM_BUILD_ROOT%{_libdir}/libmysqlservices.so
mv $RPM_BUILD_ROOT%{_bindir}/{.,}mysql_config

%clean
rm -rf $RPM_BUILD_ROOT

%post   libs -p /sbin/ldconfig
%postun libs -p /sbin/ldconfig

%files libs
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libwebscalesqlclient.so.*.*.*
%ghost %{_libdir}/libwebscalesqlclient.so.18
%attr(755,root,root) %{_libdir}/libwebscalesqlclient_r.so.*.*.*
%ghost %{_libdir}/libwebscalesqlclient_r.so.18

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/mysql_config
%{_includedir}/mysql
%{_libdir}/libwebscalesqlclient.so
%{_libdir}/libwebscalesqlclient_r.so

%files static
%defattr(644,root,root,755)
%{_libdir}/libwebscalesqlclient.a
%{_libdir}/libwebscalesqlclient_r.a
