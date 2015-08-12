require '_h2ph_pre.ph';

no warnings 'redefine';

unless(defined(&_SYS_UIO_H)) {
    eval 'sub _SYS_UIO_H () {1;}' unless defined(&_SYS_UIO_H);
    require 'features.ph';
    require 'sys/types.ph';
    require 'bits/uio.ph';
}
1;
