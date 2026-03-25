#!/usr/bin/perl

my $include = qr{<!-- #include .+? end include -->}s;
my $doctype = qr{<!DOCTYPE[^>]+>}s;

foreach $file (@ARGV) {
    my $text;
    { local $/ = undef; local *FILE; open FILE, "<", $file; $text = <FILE>; close FILE; }

    $text =~ s/$include//gs;    # BBEdit include
    $text =~ s/$doctype//gs;
    $text =~ s{</?body[^>]*>}{}gi;
    $text =~ s{</?html[^>]*>}{}gi;
    $text =~ s{^\s*$}{}gm;       # blank lines
    $text =~ s{^\s+}{}gm;         # unindent

    $file =~ s{\.html$}{};
    
    open FILE, '>', $file;
    print FILE $text;
    close FILE;
    # print $text . "\n";
}

