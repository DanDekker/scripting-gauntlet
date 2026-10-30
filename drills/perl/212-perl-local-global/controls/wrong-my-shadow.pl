#!/usr/bin/env perl
# Plausible bug: overrides the separator with a `my` lexical inside the helper, so
# the helper — which reads the package global — never sees the override.
use strict;
use warnings;

my $IN  = $ENV{IN}  or die "IN not set\n";
my $OUT = $ENV{OUT} or die "OUT not set\n";

our $SEP = ',';

sub render {
    my ($kind, $value) = @_;
    return join($SEP, $kind, $value);
}

open my $fh, '<', "$IN/records.txt" or die "cannot read records.txt: $!\n";
my @records;
while (my $line = <$fh>) {
    chomp $line;
    next if $line =~ /^\s*$/;
    next if $line =~ /^\s*#/;
    my ($kind, $value) = split /\s+/, $line, 2;
    push @records, [ $kind, $value ];
}
close $fh;

my @rendered;
my $wide = 0;
for my $record (@records) {
    if ($record->[0] eq 'wide') {
        $wide++;
        # BUG: a new lexical in this block. The helper reads the package global,
        # so the override never reaches it and the wide row keeps the comma.
        my $SEP = ';';
        push @rendered, render(@$record);
    }
    else {
        push @rendered, render(@$record);
    }
}

open my $out, '>', "$OUT/report.txt" or die "cannot write report.txt: $!\n";
print {$out} "$_\n" for @rendered;
close $out;

open my $sum, '>', "$OUT/summary.json" or die "cannot write summary.json: $!\n";
printf {$sum} "{\"records\":%d,\"wide\":%d,\"sep_after\":\"%s\"}\n",
    scalar(@records), $wide, $SEP;
close $sum;
