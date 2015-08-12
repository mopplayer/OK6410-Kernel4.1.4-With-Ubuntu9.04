

use strict;
use utf8;


package Debconf::FrontEnd::Kde::WizardUi;
use Qt;
use Qt::isa qw(Qt::Widget);
use Qt::attributes qw(
    title
    line1
    mainFrame
    bHelp
    bBack
    bNext
    bCancel
);



sub NEW
{
    shift->SUPER::NEW(@_[0..2]);

    if ( name() eq "unnamed" )
    {
        setName("DebconfWizard" );
    }

    my $DebconfWizardLayout = Qt::VBoxLayout(this, 11, 6, '$DebconfWizardLayout');

    title = Qt::Label(this, "title");
    title->setSizePolicy( Qt::SizePolicy(5, 0, 0, 0, title->sizePolicy()->hasHeightForWidth()) );
    $DebconfWizardLayout->addWidget(title);

    line1 = Qt::Frame(this, "line1");
    line1->setSizePolicy( Qt::SizePolicy(5, 0, 0, 0, line1->sizePolicy()->hasHeightForWidth()) );
    line1->setFrameShape( &Qt::Frame::HLine() );
    line1->setFrameShadow( &Qt::Frame::Sunken() );
    line1->setFrameShape( &Qt::Frame::VLine );
    $DebconfWizardLayout->addWidget(line1);

    mainFrame = Qt::Frame(this, "mainFrame");
    mainFrame->setFrameShape( &Qt::Frame::NoFrame() );
    mainFrame->setFrameShadow( &Qt::Frame::Raised() );
    $DebconfWizardLayout->addWidget(mainFrame);

    my $layout1 = Qt::HBoxLayout(undef, 0, 6, '$layout1');

    bHelp = Qt::PushButton(this, "bHelp");
    $layout1->addWidget(bHelp);
    my $spacer = Qt::SpacerItem(161, 20, &Qt::SizePolicy::Expanding, &Qt::SizePolicy::Minimum);
    $layout1->addItem($spacer);

    bBack = Qt::PushButton(this, "bBack");
    $layout1->addWidget(bBack);

    bNext = Qt::PushButton(this, "bNext");
    $layout1->addWidget(bNext);

    bCancel = Qt::PushButton(this, "bCancel");
    $layout1->addWidget(bCancel);
    $DebconfWizardLayout->addLayout($layout1);
    languageChange();
    my $resize = Qt::Size(660, 460);
    $resize = $resize->expandedTo(minimumSizeHint());
    resize( $resize );
    clearWState( &Qt::WState_Polished );
}



sub languageChange
{
    setCaption(trUtf8("Debconf Wizard for KDE") );
    title->setText( trUtf8("title") );
    bHelp->setText( trUtf8("Help") );
    bBack->setText( trUtf8("< Back") );
    bNext->setText( trUtf8("Next >") );
    bCancel->setText( trUtf8("Cancel") );
}


1;
