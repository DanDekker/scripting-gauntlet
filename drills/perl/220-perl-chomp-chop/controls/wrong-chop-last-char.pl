#!/usr/bin/env perl
# Plausible bug: strips the terminator with chop, which removes the last character
# whatever it is, so the last line loses its final character.
use strict;
use warnings;

my $IN  = $ENV{IN}  or die "IN not set\n";
my $OUT = $ENV{OUT} or die "OUT not set\n";

open my $fh, '<', "$IN/notes.txt" or die "cannot read notes.txt: $!\n";
my @notes;
while (my $line = <$fh>) {
    # BUG: chop removes the last character, whatever it is.
    chop $line;
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
