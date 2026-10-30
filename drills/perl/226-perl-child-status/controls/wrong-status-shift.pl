#!/usr/bin/env perl
# Plausible bug: reads only the exit code with a shift and never looks at the signal
# bits or the "never executed" case.
use strict;
use warnings;

my $IN  = $ENV{IN}  or die "IN not set\n";
my $OUT = $ENV{OUT} or die "OUT not set\n";

my @probes;
{
    open my $fh, '<', "$IN/probes.csv" or die "cannot read probes.csv: $!\n";
    my $header = <$fh>;
    while (my $line = <$fh>) {
        chomp $line;
        next if $line eq '';
        push @probes, [ split /,/, $line, -1 ];
    }
    close $fh;
}

my (@rows, $ok, $failed);
$ok = $failed = 0;

for my $probe (@probes) {
    my ($id, $kind, $arg) = @$probe;

    if ($kind eq 'exit') {
        system('python3', '-c', 'import sys; sys.exit(int(sys.argv[1]))', $arg);
    }
    elsif ($kind eq 'signal') {
        system('python3', '-c', 'import os, signal, sys; os.kill(os.getpid(), int(sys.argv[1]))', $arg);
    }
    elsif ($kind eq 'missing') {
        no warnings 'exec';
        system($arg);
    }
    else {
        die "unknown probe kind: $kind\n";
    }

    # BUG: only the exit code is read. A signalled child has exit code 0, and a
    # program that never ran leaves $? at -1, which shifts to a huge number.
    my $code = $? >> 8;
    my $status = ($code == 0) ? 'ok' : 'failed';

    if ($status eq 'ok') { $ok++ } else { $failed++ }
    push @rows, [ $id, $kind, $status, $code ];
}

open my $out, '>', "$OUT/results.csv" or die "cannot write results.csv: $!\n";
print {$out} "id,kind,status,detail\n";
for my $row (@rows) {
    print {$out} join(',', @$row), "\n";
}
close $out;

open my $sum, '>', "$OUT/summary.json" or die "cannot write summary.json: $!\n";
printf {$sum} "{\"probes\":%d,\"ok\":%d,\"failed\":%d,\"signalled\":0,\"notfound\":0}\n",
    scalar(@rows), $ok, $failed;
close $sum;
