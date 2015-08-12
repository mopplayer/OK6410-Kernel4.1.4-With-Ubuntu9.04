#!/usr/bin/perl -w
# This file was preprocessed, do not edit!


package Debconf::Element::Kde::ElementWidget;
use Qt;
use Qt::isa @ISA = qw(Qt::Widget);
use Qt::attributes qw(layout mytop toplayout);


sub NEW {
	shift->SUPER::NEW (@_[0..2]);
	mytop = undef;
}


sub settop {
    mytop = shift;
}


sub init {
	setSizePolicy(Qt::SizePolicy(1, &Qt::SizePolicy::Preferred, 0, 
	                             0, sizePolicy()->hasHeightForWidth()));
	toplayout = layout = Qt::VBoxLayout(this, 0, 10, "TopVBox");
	if (mytop) {
		toplayout->addWidget (mytop);
		layout = Qt::VBoxLayout(mytop, 15, 5, "TopVBox");
	}
	else {
		mytop = this;
	}
}


sub destroy {
	toplayout -> remove (mytop);
	undef mytop;
}


sub top {
    return mytop;
}


sub addwidget {
    layout->addWidget(@_);
}


sub addlayout {
    layout->addLayout (@_);
}


sub additem {
    my $item=shift;
    layout->addItem($item);
}





package Debconf::Element::Kde;
use strict;
use Qt;
use Debconf::Gettext;
use base qw(Debconf::Element);
use Debconf::Element::Kde::ElementWidget;
use Debconf::Encoding qw(to_Unicode);


sub create {
	my $this=shift;
	$this->parent(shift);
	$this->top(Debconf::Element::Kde::ElementWidget($this->parent, undef,
	                                                undef, undef));
	$this->top->init;
	$this->top->show;
}


sub destroy {
	my $this=shift;
	$this->top->destroy;
	$this->top->reparent(undef, 0, Qt::Point(0, 0), 0);
	$this->top->DESTROY;
	$this->top(undef);
}


sub addhbox {
	my $this=shift;
	my $hbox = Qt::HBoxLayout(undef, 0, 8, "SubHBox");
	$this->cur->addlayout($hbox);
	return $hbox;
}


sub addwidget {
	my $this=shift;
	my $widget=shift;
	$this->cur->addwidget($widget);
}


sub description {
	my $this=shift;
	my $label=Qt::Label($this->cur->top);
	$label->setText(to_Unicode($this->question->description));
	$label->setSizePolicy(Qt::SizePolicy(1, 1, 0, 0, $label->sizePolicy()->hasHeightForWidth()));
	$label->show;
	return $label;
}


sub startsect {
	my $this = shift;
	my $ew = Debconf::Element::Kde::ElementWidget($this->top);
	my $mytop = Qt::GroupBox($ew);
	$ew->settop($mytop);
	$ew->init;
	$this->cur($ew);
	$this->top->addwidget($ew);
	$ew->show;
}


sub endsect {
	my $this = shift;
	$this->cur($this->top);
}


sub adddescription {
	my $this=shift;
	my $label=$this->description;
	$this->addwidget($label);
}


sub addhelp {
	my $this=shift;
    
	my $help=to_Unicode($this->question->extended_description);
	return unless length $help;
	my $label=Qt::Label($this->cur->top);
	$label->setText($help);
	$label->setTextFormat(&Qt::AutoText);
	$label->setAlignment(&Qt::WordBreak | &Qt::AlignJustify);
	$label->setSizePolicy(Qt::SizePolicy(&Qt::SizePolicy::Minimum,
	                                     &Qt::SizePolicy::Fixed,
	                                     0, 0, $label->sizePolicy()->hasHeightForWidth()));
	$this->addwidget($label); # line1
	$label->show;
}


sub value {
	my $this=shift;
	return '';
}


1
