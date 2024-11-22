#!/usr/bin/perl5.10.1
use warnings;
use strict;
use Text::Markdown 'markdown';

# @dirs is available for the Header file to make a navigation map
our ( @regexs, %reg_to_file_path, @dirs );

# Make sure this works both locally and remotely
my ($MAIN_DIR);
my $os = `uname`;
my $host = `uname -n`;
chomp($os);
chomp($host);

if ( $os eq 'SunOS' ) {
    $MAIN_DIR = '/home/friedman/public_html/WebDisplay';
}
elsif ( $host =~ m/sonic.net/ ) {
    $MAIN_DIR = '.';
}
else {
    $MAIN_DIR = '/Users/friedman/localprojects/WebDisplay';
}

print "Content-type: text/html\n\n";

sub get_file_list {
    my ($word) = @_;
    $word =~ s{.+/}{};    # remove dir from word

    # get top-level files
    opendir( DIR, $MAIN_DIR ) || die "can't opendir $MAIN_DIR: $!";
    my @top_dir_files = grep { !/^\./ } readdir(DIR);
    closedir DIR;

    # get files one level deeper too
    my (@files);
    foreach my $item (@top_dir_files) {
        if ( -d "$MAIN_DIR/$item" ) {
            push @dirs, $item;

            # have to add dirs to the regex list too, but with their index
            # file as the file path
            $reg_to_file_path{ lc($item) } = "$item/index";  
            opendir( DIR, "$MAIN_DIR/$item" )
                || die "can't opendir $MAIN_DIR/$item: $!";
            my @low_dir_files = grep { !/^\./ } readdir(DIR);
            closedir DIR;
            push @files, @low_dir_files;
            map { $reg_to_file_path{ lc($_) } = "$item/$_" } @low_dir_files;
        }
        else {
            push @files, $item;
            $reg_to_file_path{ lc($item) } = $item;
        }
    }

    @files = grep { $_ ne $word } @files;  # remove current page
    @regexs = map {qr{\b$_\b}i} @files;    # make them into whole-word regexes
}

sub process {
    my ($file, $use_markdown) = @_;
    my $path = $MAIN_DIR . '/' . $file;

    # slurp in file
    local $/ = undef;
    local *FILE;
    open FILE, '<', $path;
    my $text = <FILE>;
    close FILE;

    # turn on Markdown processing for main pages (not headers or footers)
    $text = markdown($text) if defined $use_markdown;

    # Eval ActiveWikiPage perl code in file
    $file =~ s{\s+}{_}g;
    do {
        $text =~ m{\G<%(.*?)%>}cgs;
        if ( defined $1 ) {
            eval( "package " . $file . ";$1" );
            $@ and print $@;
        }
        print $1 if $text =~ m{\G(<a [^>]+>[^<>]+</a>)}cgsi;    # links
        print $1 if $text =~ m{\G(<[^>]+>)}cgs;    # html tags themselves
        foreach (@regexs) {
            print "<a class=\"wdlink\" href=\"?$reg_to_file_path{lc($1)}\">$1</a>"
                if $text =~ m{\G($_)}cgs;
        }
        print $1 if $text =~ m{\G([^< ]+)}cgs;     # a word
        print $1 if $text =~ m{\G(\s+)}cgs;        # a space
    } until ( $text =~ m{\G\Z} );
}

my $in = $ENV{QUERY_STRING};

my $word = 'Home';
if ( defined $in && $in ) {
    $in =~ s/%(..)/pack('c',hex($1))/ge;           # take care of decoding
    $in =~ s{^/}{};    # remove initial slash, it could be accidental
    my $path = $MAIN_DIR . '/' . $in;
    if ( $in =~ m/\.\./ ) {

        # someone is trying to break out of this dir
        $word = 'Home';
    }
    elsif ( -f $path ) {
        $word = $in;
    }
}
$ENV{THIS_FILE} = $word;    # make it available to templates

get_file_list($word);

process('Header');

process($word, 1);

process('Footer');

print "\n";

# TODO: searching (grep) - probably another CGI?
