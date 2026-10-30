#!/usr/bin/env perl
# 211-perl-warn-capture — a handler that is local, and messages that end in a newline.
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
{
    # local restores the previous handler when this block ends.
    local $SIG{__WARN__} = sub { push @captured, $_[0] };
    for my $message (@messages) {
        warn "$message\n";     # trailing newline: no " at FILE line N." suffix
    }
}

my $captured_before_final = scalar @captured;
warn "rotation complete\n";    # the handler is gone: this goes to stderr
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
