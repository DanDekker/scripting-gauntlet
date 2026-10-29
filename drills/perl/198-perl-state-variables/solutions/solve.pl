#!/usr/bin/env perl
# 198-perl-state-variables — persistent lexical subroutine state with `state`
use strict;
use warnings;
use feature 'state';

my $IN  = $ENV{IN}  or die "IN not set\n";
my $OUT = $ENV{OUT} or die "OUT not set\n";

sub record_check {
    my ($service, $status) = @_;
    state %streaks;

    if ($status eq 'FAIL') {
        $streaks{$service} = ($streaks{$service} || 0) + 1;
    } else {
        $streaks{$service} = 0;
    }

    my $streak = $streaks{$service};
    my $alert = ($streak >= 3) ? 'true' : 'false';
    return ($streak, $alert);
}

my @rows;
my $step = 0;
my $alerts_count = 0;
my $max_streak = 0;

open my $fh, '<', "$IN/checks.log" or die "cannot read checks.log: $!\n";
while (my $line = <$fh>) {
    chomp $line;
    $line =~ s/^\s+//;
    $line =~ s/\s+$//;
    next if $line eq '' || $line =~ /^#/;

    $step++;
    my ($ts, $svc, $status) = split /\s+/, $line;
    my ($streak, $alert) = record_check($svc, $status);

    if ($alert eq 'true') { $alerts_count++; }
    if ($streak > $max_streak) { $max_streak = $streak; }

    push @rows, [ $step, $ts, $svc, $status, $streak, $alert ];
}
close $fh;

open my $out, '>', "$OUT/streaks.csv" or die "cannot write streaks.csv: $!\n";
print {$out} "step,timestamp,service,status,streak,alert\n";
for my $r (@rows) {
    print {$out} join(',', @$r), "\n";
}
close $out;

open my $sum, '>', "$OUT/summary.json" or die "cannot write summary.json: $!\n";
printf {$sum} "{\"checks\":%d,\"alerts\":%d,\"max_streak\":%d}\n",
    scalar(@rows), $alerts_count, $max_streak;
close $sum;
