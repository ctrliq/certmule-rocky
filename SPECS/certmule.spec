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

Name:                 certmule-rocky
Version:              0.1
Release:              3%{?dist}
Summary:              UEFI cert-loading EFI file for trusting Rocky Linux components
ExclusiveArch:        x86_64
License:              BSD
URL:                  https://github.com/rhboot/certmule
#Source0:              https://github.com/rhboot/certmule/releases/download/%{version}/certmule-%{version}.tar.bz2
Source0:              certmule-20230310.git.tar.gz
Source1:              db.rocky.esl
Source2:              sbat.rocky.csv

Source1000:           ciq_sb_certmule.crt

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


%define pesign_name_0 ciq_sb_certmule
%define pesign_cert_0 %{SOURCE1000}


%global debug_desc \
This package provides debug information for package %{expand:%%{name}} \
Debug information is useful when developing applications that \
use this package or when debugging this package.

%description
CA bundled in a simple UEFI binary, designed for loading by shim. This will make a secure boot enabled system trust this bundled CA in addition to the one in shim.
This package is specific to the Rocky Linux CA, it produces a certmule .efi file that contains the Rocky secure boot CA, for trusting Rocky secure boot components.

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
%setup -q -n certmule-20230310.git 
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

mv build-%{efiarch}/certmule.efi build-%{efiarch}/certmule-unsigned.efi

# If we have a "for real" signing macro installed, let's go ahead and sign the artifcact
# Otherwise, the unsigned artifact and signed should be equivalent:
%if %{?pe_signing_cert:1}%{!?pe_signing_cert:0}
%pesign -s -i build-%{efiarch}/certmule-unsigned.efi -o build-%{efiarch}/certmule.efi  -c %{pesign_cert_0} -n %{pesign_name_0}
%else
cp -p build-%{efiarch}/certmule-unsigned.efi  build-%{efiarch}/certmule.efi
%endif

cd build-%{efiarch}
make ${MAKEFLAGS} \
	DESTDIR=${RPM_BUILD_ROOT} \
	install
cd ..

cp -p build-%{efiarch}/certmule-unsigned.efi ${RPM_BUILD_ROOT}/%{certmuleinstalldir}/



# Installing to 
install -D -d -m 0755 ${RPM_BUILD_ROOT}/boot/
install -D -d -m 0700 ${RPM_BUILD_ROOT}%{efi_esp_root}/
install -D -d -m 0700 ${RPM_BUILD_ROOT}%{efi_esp_efi}/
install -D -d -m 0700 ${RPM_BUILD_ROOT}%{efi_esp_dir}/

# Install official "shim_certificate.efi" binary - the one shim actually looks for:
install -p -m 0700 build-%{efiarch}/certmule.efi  ${RPM_BUILD_ROOT}%{efi_esp_dir}/shim_certificate.efi




%files
%dir %{certmuleinstalldir}
%{certmuleinstalldir}/*.efi
%{efi_esp_dir}/shim_certificate.efi




%changelog
* Mon Mar 27 2023 Skip Grube <sgrube@ciq.co> - 0.1-3
- Naming adjustment, minor specfile adjustments
- Added the ability to sign binary automatically

* Tue Mar 21 2023 Skip Grube <sgrube@ciq.co> - 0.1-2
- Fixed build for RHEL/Rocky 8
- Fixed SBAT entry - need 6 columns

* Thu Mar 16 2023 Sherif Nagy <sherif@rockylinux.org> - 0.1-1
- Init certmule
