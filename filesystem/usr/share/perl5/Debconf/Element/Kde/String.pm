#!/usr/bin/perl -w
# This file was preprocessed, do not edit!


package Debconf::Element::Kde::String;
use strict;
use Qt;
use base qw(Debconf::Element::Kde);
use Debconf::Encoding qw(to_Unicode);


sub create {
	my $this=shift;
	
	$this->SUPER::create(@_);
	$this->startsect;
	$this->widget(Qt::LineEdit($this->cur->top));
	$this->widget->show;
	my $default='';
	$default=$this->question->value if defined $this->question->value;
	$this->widget->setText(to_Unicode($default));
	$this->widget->setSizePolicy(Qt::SizePolicy(1, 0, 0, 0));
	$this->addhelp;
	my $b = $this->addhbox;
	$b->addWidget ($this->description);
	$b->addWidget ($this->widget);
	$this->endsect;
}


sub value {
	my $this=shift;
	return $this->widget->text();
}


1
