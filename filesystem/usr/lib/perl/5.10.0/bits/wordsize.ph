require '_h2ph_pre.ph';

no warnings 'redefine';

unless(defined(&__WORDSIZE)) {
    sub __WORDSIZE () {	32;}
}
1;
