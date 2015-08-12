#!/usr/bin/perl -w
# This file was preprocessed, do not edit!


package Debconf::Element::Kde::Password;
use strict;
use Qt;
use base qw(Debconf::Element::Kde);


sub create {
	my $this=shift;
	
	$this->SUPER::create(@_);
	$this->startsect;
	$this->widget(Qt::LineEdit($this->cur->top));
	$this->widget->show;
	$this->widget->setEchoMode(2);
	$this->addhelp;
	my $b = $this->addhbox;
	$b->addWidget($this->description);
	$b->addWidget($this->widget);
	$this->endsect;
}


sub value {
	my $this=shift;
	
	my $text = $this->widget->text();
	$text = $this->question->value if $text eq '';
	return $text;
}


1
