%global pesign_vre 0.106-1
%global openssl_vre 1.0.2j

%global efidir %(eval echo $(grep ^ID= /etc/os-release | sed -e 's/^ID=//' -e 's/rhel/rocky/'))
%global certmulerootdir %{_datadir}/certmule/
%global certmuleversiondir %{certmulerootdir}/%{version}-%{release}
%global efiarch x64
%global certmuledir %{certmuleversiondir}/%{efiarch}
%global certmuleinstalldir %{_datadir}/certmule-1

%global debug_package %{nil}
%global __debug_package 1
%global _binaries_in_noarch_packages_terminate_build 0

Name:                 certmule-unsigned-%{efiarch}
Version:              0.1
Release:              2%{?dist}
Summary:              UEFI cert loading EFI
ExclusiveArch:        x86_64
License:              BSD
URL:                  https://github.com/rhboot/certmule
Source0:              https://github.com/rhboot/certmule/releases/download/%{version}/certmule-%{version}.tar.bz2
Source1:              db.rocky.esl
Source2:              sbat.rocky.csv

BuildRequires:        gcc make
BuildRequires:        elfutils-libelf-devel
BuildRequires:        git openssl-devel openssl
BuildRequires:        pesign >= %{pesign_vre}
BuildRequires:        dos2unix findutils

# We need a newer "objcopy" from binutils if building on Rocky 8:
%if 0%{?rhel} == 8
BuildRequires:       gcc-toolset-11-binutils
%endif


Provides:             bundled(openssl) = %{openssl_vre}

%global desc \
UEFI cert loading EFI

%global debug_desc \
This package provides debug information for package %{expand:%%{name}} \
Debug information is useful when developing applications that \
use this package or when debugging this package.

%description
%desc

%package debuginfo
Summary:              Debug information for %{name}
Group:                Development/Debug
AutoReqProv:          0
BuildArch:            noarch

%description debuginfo
%debug_desc

%package debugsource
Summary:              Debug Source for %{name}
Group:                Development/Debug
AutoReqProv:          0
BuildArch:            noarch

%description debugsource
%debug_desc

%prep
%setup -q
mkdir build-%{efiarch}
cp %{SOURCE1} data/
cp %{SOURCE2} data/
cp %{SOURCE2} build-%{efiarch}/

%build
# enable gcc-toolset-11 binutils on RHEL/Rocky 8
%if 0%{?rhel} == 8
source /opt/rh/gcc-toolset-11/enable
%endif

MAKEFLAGS="TOPDIR=.. -f ../Makefile "
MAKEFLAGS+="EFIDIR=%{efidir} PKGNAME=certmule RELEASE=%{release} "
MAKEFLAGS+="%{_smp_mflags} "
MAKEFLAGS+="VENDOR_DB_FILE=%{SOURCE1}"

cd build-%{efiarch}
make ${MAKEFLAGS} \
	all
cd ..

%install
MAKEFLAGS="TOPDIR=.. -f ../Makefile "
MAKEFLAGS+="EFIDIR=%{efidir} PKGNAME=certmule RELEASE=%{release}"

cd build-%{efiarch}
make ${MAKEFLAGS} \
	DESTDIR=${RPM_BUILD_ROOT} \
	install
cd ..

%files
%dir %{certmuleinstalldir}
%{certmuleinstalldir}/*.efi

%changelog
* Tue Mar 21 2023 Skip Grube <sgrube@ciq.co> - 0.1-2
- Fixed build for RHEL/Rocky 8
- Fixed SBAT entry - need 6 columns

* Thu Mar 16 2023 Sherif Nagy <sherif@rockylinux.org> - 0.1-1
- Init certmule
