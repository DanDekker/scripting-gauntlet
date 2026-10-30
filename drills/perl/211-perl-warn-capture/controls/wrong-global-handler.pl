#!/usr/bin/env perl
# Plausible bug: installs the warning handler globally, so it survives the watched
# phase and captures the final warning as well.
use strict;
use warnings;

my $IN  = $ENV{IN}  or die "IN not set\n";
my $OUT = $ENV{OUT} or die "OUT not set\n";

open my $fh, '<', "$IN/warnings.txt" or die "cannot read warnings.txt: $!\n";
my @messages;
while (my $line = <$fh>) {
    chomp $line;
    push @messages, $line;
}
close $fh;

my @captured;
# BUG: a global assignment; the handler outlives the watched phase.
$SIG{__WARN__} = sub { push @captured, $_[0] };
for my $message (@messages) {
    warn "$message\n";
}

my $captured_before_final = scalar @captured;
warn "rotation complete\n";
my $final_captured = (scalar(@captured) > $captured_before_final) ? 'true' : 'false';

open my $out, '>', "$OUT/warnings.csv" or die "cannot write warnings.csv: $!\n";
print {$out} "index,message\n";
my $index = 0;
for my $message (@captured) {
    $index++;
    $message =~ s/\n\z//;
    print {$out} $index, ',', $message, "\n";
}
close $out;

open my $sum, '>', "$OUT/summary.json" or die "cannot write summary.json: $!\n";
printf {$sum} "{\"emitted\":%d,\"captured\":%d,\"final_captured\":\"%s\"}\n",
    scalar(@messages) + 1, scalar(@captured), $final_captured;
close $sum;
