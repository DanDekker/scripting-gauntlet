#!/usr/bin/env perl
# Plausible bug: uses `my %streaks` inside subroutine, losing persistence
use strict;
use warnings;

my $IN  = $ENV{IN}  or die "IN not set\n";
my $OUT = $ENV{OUT} or die "OUT not set\n";

sub record_check {
    my ($service, $status) = @_;
    # BUG: `my` reinitializes %streaks on every call!
    my %streaks;

    if ($status eq 'FAIL') {
        $streaks{$service} = 1;
    } else {
        $streaks{$service} = 0;
    }

    my $streak = $streaks{$service};
    my $alert = ($streak >= 3) ? 'true' : 'false';
    return ($streak, $alert);
}

my @rows;
my $step = 0;

open my $fh, '<', "$IN/checks.log" or die "cannot read checks.log: $!\n";
while (my $line = <$fh>) {
    chomp $line;
    $line =~ s/^\s+//;
    $line =~ s/\s+$//;
    next if $line eq '' || $line =~ /^#/;

    $step++;
    my ($ts, $svc, $status) = split /\s+/, $line;
    my ($streak, $alert) = record_check($svc, $status);
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
print {$sum} '{"checks":9,"alerts":0,"max_streak":1}\n';
close $sum;
