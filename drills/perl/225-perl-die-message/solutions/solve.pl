#!/usr/bin/env perl
# 225-perl-die-message — die with a trailing newline so no location is appended.
use strict;
use warnings;

my $IN  = $ENV{IN}  or die "IN not set\n";
my $OUT = $ENV{OUT} or die "OUT not set\n";

my @checks;
{
    open my $fh, '<', "$IN/checks.txt" or die "cannot read checks.txt: $!\n";
    while (my $line = <$fh>) {
        chomp $line;
        next if $line eq '';
        my ($name, $message) = split / /, $line, 2;
        push @checks, [ $name, $message ];
    }
    close $fh;
}

my (@rows, $longest, $first);
my $index = 0;
for my $check (@checks) {
    $index++;
    my ($name, $text) = @$check;
    eval { die "$text\n" };        # a trailing newline: no " at FILE line N."
    my $caught = $@;
    $caught = '' unless defined $caught;
    $caught =~ s/\n\z//;
    $longest = length($caught) if length($caught) > $longest;
    $first = $caught if $index == 1;
    push @rows, [ $index, $name, $caught ];
}

open my $out, '>', "$OUT/checks.csv" or die "cannot write checks.csv: $!\n";
print {$out} "index,name,message\n";
for my $row (@rows) {
    print {$out} join(',', @$row), "\n";
}
close $out;

open my $sum, '>', "$OUT/summary.json" or die "cannot write summary.json: $!\n";
printf {$sum} "{\"checks\":%d,\"longest\":%d,\"first\":\"%s\"}\n",
    scalar(@rows), $longest, $first;
close $sum;
