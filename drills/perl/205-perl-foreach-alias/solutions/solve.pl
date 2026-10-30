#!/usr/bin/env perl
# 205-perl-foreach-alias — normalize a copy so the source list survives.
use strict;
use warnings;

my $IN  = $ENV{IN}  or die "IN not set\n";
my $OUT = $ENV{OUT} or die "OUT not set\n";

open my $fh, '<', "$IN/names.txt" or die "cannot read names.txt: $!\n";
my @names;
while (my $line = <$fh>) {
    chomp $line;
    push @names, $line;
}
close $fh;

# foreach aliases the list elements, so work on a copy.
my @work = @names;
foreach my $name (@work) {
    my $trimmed = $name;
    $trimmed =~ s/^\s+//;
    $trimmed =~ s/\s+$//;
    $name = ucfirst $trimmed;
}

my $changed = 0;
for my $i (0 .. $#names) {
    $changed++ if $work[$i] ne $names[$i];
}

open my $out, '>', "$OUT/normalized.csv" or die "cannot write normalized.csv: $!\n";
print {$out} "index,name\n";
for my $i (0 .. $#work) {
    print {$out} ($i + 1), ',', $work[$i], "\n";
}
close $out;

open my $orig, '>', "$OUT/original.csv" or die "cannot write original.csv: $!\n";
print {$orig} "index,name\n";
for my $i (0 .. $#names) {
    print {$orig} ($i + 1), ',', $names[$i], "\n";
}
close $orig;

open my $sum, '>', "$OUT/summary.json" or die "cannot write summary.json: $!\n";
printf {$sum} "{\"names\":%d,\"changed\":%d}\n", scalar(@names), $changed;
close $sum;
