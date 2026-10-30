#!/usr/bin/env perl
# Plausible bug: passes the template as the format string, so the percent sign in
# the data becomes a conversion specifier and eats the text after it.
use strict;
use warnings;

my $IN  = $ENV{IN}  or die "IN not set\n";
my $OUT = $ENV{OUT} or die "OUT not set\n";

open my $fh, '<', "$IN/templates.txt" or die "cannot read templates.txt: $!\n";
my @templates;
while (my $line = <$fh>) {
    chomp $line;
    push @templates, $line;
}
close $fh;

open my $out, '>', "$OUT/report.txt" or die "cannot write report.txt: $!\n";
for my $template (@templates) {
    # BUG: the template becomes the format string.
    printf {$out} "$template\n";
}
close $out;

my $percent = 0;
my $chars = 0;
for my $template (@templates) {
    $percent++ if index($template, '%') >= 0;
    $chars += length($template);
}

open my $sum, '>', "$OUT/summary.json" or die "cannot write summary.json: $!\n";
printf {$sum} "{\"templates\":%d,\"percent_templates\":%d,\"chars\":%d}\n",
    scalar(@templates), $percent, $chars;
close $sum;
