#!/usr/bin/perl5.10.1
print "Content-type: text/html\n\n";
print "<html><body><h1>Test</h1>\n";
use Cwd qw(getcwd abs_path);
print "<p>cwd: " . getcwd() . "</p>\n";
print "<p>abs_path: " . abs_path('.') . "</p>\n";
print "<p>ENV:<pre>";
print $_ . ':' . $ENV{$_} . "\n" foreach keys %ENV;
print "</pre></p>";
print "</body></html>\n";
