#!/usr/bin/perl -w
# This file was preprocessed, do not edit!


package Debconf::FrontEnd::Kde::Wizard;
use strict;
use utf8;
use Debconf::Log ':all';
use Qt;
use Qt::isa qw(Debconf::FrontEnd::Kde::WizardUi);
use Qt::slots 'goNext' => [], 'goBack' => [], 'goBye' => [];
use Qt::attributes qw(frontend);
use Debconf::FrontEnd::Kde::WizardUi;


sub NEW {
	shift->SUPER::NEW(@_[0..2]);
	frontend = $_[2];
	this->connect(bNext, SIGNAL 'clicked ()', SLOT 'goNext ()');
	this->connect(bBack, SIGNAL 'clicked ()', SLOT 'goBack ()');
	this->connect(bCancel, SIGNAL 'clicked ()', SLOT 'goBye ()');
	this->title->show;
}


sub setTitle {
	this->title->setText($_[0]);
}


sub setNextEnabled {
	bNext->setEnabled(shift);
}


sub setBackEnabled {
	bBack->setEnabled(shift);
}


sub goNext {
	debug frontend => "QTF: -- LEAVE EVENTLOOP --------";
	frontend->goback(0);
	Qt::app->exit(0);
}


sub goBack {
	debug frontend => "QTF: -- LEAVE EVENTLOOP --------";
	frontend->goback(1);
	Qt::app->exit(0);
}


sub goBye {
	debug developer => "QTF: -- LEAVE EVENTLOOP --------";
	frontend->cancelled(1);
	Qt::app->exit (0);
}


1;
