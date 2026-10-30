#!/usr/bin/env perl
# 232-perl-process-triage — parse ps table and flag runaway processes.
use strict;
use warnings;

my $IN  = $ENV{IN}  or die "IN not set\n";
my $OUT = $ENV{OUT} or die "OUT not set\n";

my %thresholds;
open my $tfh, '<', "$IN/thresholds.ini" or die "cannot read thresholds.ini: $!\n";
while (my $line = <$tfh>) {
    chomp $line;
    $line =~ s/\s*#.*//;
    if ($line =~ /^\s*(\w+)\s*=\s*(\S+)\s*$/) {
        $thresholds{$1} = $2 + 0;
    }
}
close $tfh;

my $cpu_thresh = $thresholds{cpu_pct};
my $rss_thresh = $thresholds{rss_kb};

my @flagged;
my %counts = (cpu_only => 0, mem_only => 0, both => 0);
my $total = 0;

open my $pfh, '<', "$IN/processes.txt" or die "cannot read processes.txt: $!\n";
my $header = <$pfh>;
while (my $line = <$pfh>) {
    chomp $line;
    $line =~ s/^\s+//;
    $line =~ s/\s+$//;
    next unless length $line;
    next if $line =~ /^#/;

    $total++;

    # Limit 11 to keep command (field 11) whole with all its arguments
    my @parts = split /\s+/, $line, 11;
    my ($user, $pid, $cpu, $mem, $vsz, $rss, $tty, $stat, $start, $time, $cmd) = @parts;

    $pid = $pid + 0;
    $cpu = $cpu + 0.0;
    $rss = $rss + 0;

    my $is_cpu = ($cpu >= $cpu_thresh);
    my $is_mem = ($rss >= $rss_thresh);

    my $flag;
    if ($is_cpu && $is_mem) {
        $flag = 'both';
        $counts{both}++;
    }
    elsif ($is_cpu) {
        $flag = 'cpu';
        $counts{cpu_only}++;
    }
    elsif ($is_mem) {
        $flag = 'memory';
        $counts{mem_only}++;
    }
    else {
        next;
    }

    push @flagged, {
        pid     => $pid,
        user    => $user,
        cpu     => $cpu,
        rss     => $rss,
        flag    => $flag,
        command => $cmd,
    };
}
close $pfh;

# Sort: CPU desc, RSS desc, PID asc
my @sorted = sort {
    $b->{cpu} <=> $a->{cpu}
    or $b->{rss} <=> $a->{rss}
    or $a->{pid} <=> $b->{pid}
} @flagged;

open my $out, '>', "$OUT/runaways.csv" or die "cannot write runaways.csv: $!\n";
print {$out} "pid,user,cpu,rss,flag,command\n";
for my $p (@sorted) {
    printf {$out} "%d,%s,%.1f,%d,%s,%s\n",
        $p->{pid}, $p->{user}, $p->{cpu}, $p->{rss}, $p->{flag}, $p->{command};
}
close $out;

open my $sum, '>', "$OUT/summary.json" or die "cannot write summary.json: $!\n";
printf {$sum} "{\"total_processes\":%d,\"flagged\":%d,\"cpu_only\":%d,\"mem_only\":%d,\"both\":%d}\n",
    $total, scalar(@sorted), $counts{cpu_only}, $counts{mem_only}, $counts{both};
close $sum;
