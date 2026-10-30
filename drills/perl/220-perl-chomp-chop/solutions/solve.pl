#!/usr/bin/env perl
# 220-perl-chomp-chop — chomp the terminator; the last line keeps every character.
use strict;
use warnings;

my $IN  = $ENV{IN}  or die "IN not set\n";
my $OUT = $ENV{OUT} or die "OUT not set\n";

open my $fh, '<', "$IN/notes.txt" or die "cannot read notes.txt: $!\n";
my @notes;
while (my $line = <$fh>) {
    chomp $line;    # removes the terminator; removes nothing on the last line
    push @notes, $line;
}
close $fh;

my $chars = 0;

open my $out, '>', "$OUT/notes.csv" or die "cannot write notes.csv: $!\n";
print {$out} "index,text,length\n";
my $index = 0;
for my $note (@notes) {
    $index++;
    my $length = length($note);
    $chars += $length;
    print {$out} $index, ',', $note, ',', $length, "\n";
}
close $out;

my $last = @notes ? $notes[-1] : '';

open my $sum, '>', "$OUT/summary.json" or die "cannot write summary.json: $!\n";
printf {$sum} "{\"notes\":%d,\"chars\":%d,\"last\":\"%s\"}\n",
    scalar(@notes), $chars, $last;
close $sum;
