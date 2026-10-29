#!/usr/bin/env perl
# Plausible bug: the tie-break compares users descending, so the tied top row comes out
use strict;
use warnings;

my $IN  = $ENV{IN}  or die "IN not set\n";
my $OUT = $ENV{OUT} or die "OUT not set\n";

my %count;
my $events  = 0;
my $invalid = 0;

open my $fh, '<', "$IN/events.log" or die "cannot read events.log: $!\n";
while (my $line = <$fh>) {
    chomp $line;
    $line =~ s/^\s+//;
    $line =~ s/\s+$//;
    next if $line eq '' or $line =~ /^#/;
    my @field = split ' ', $line;    # awk-style: runs of whitespace
    if (@field < 2) {
        $invalid++;
        next;
    }
    $count{$field[0]}++;
    $events++;
}
close $fh;

# count descending, then user ascending: without the second key the order is hash order
my @user = sort { $count{$b} <=> $count{$a} or $b cmp $a } keys %count;

open my $out, '>', "$OUT/counts.csv" or die "cannot write counts.csv: $!\n";
print {$out} "user,events\n";
for my $user (@user) {
    print {$out} "$user,$count{$user}\n";
}
close $out;

open my $sum, '>', "$OUT/summary.json" or die "cannot write summary.json: $!\n";
printf {$sum} "{\"users\":%d,\"events\":%d,\"invalid\":%d,\"top\":\"%s\"}\n",
    scalar(@user), $events, $invalid, (@user ? $user[0] : '');
close $sum;
