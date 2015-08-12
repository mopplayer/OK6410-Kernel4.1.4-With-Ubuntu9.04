require '_h2ph_pre.ph';

no warnings 'redefine';

unless(defined(&_BITS_SIGTHREAD_H)) {
    eval 'sub _BITS_SIGTHREAD_H () {1;}' unless defined(&_BITS_SIGTHREAD_H);
    if(!defined (defined(&_SIGNAL_H) ? &_SIGNAL_H : undef)  && !defined (defined(&_PTHREAD_H) ? &_PTHREAD_H : undef)) {
	die("Never include this file directly.  Use <pthread.h> instead");
    }
}
1;
