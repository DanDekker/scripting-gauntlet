#!/usr/bin/env perl
# 226-perl-child-status — decode the wait status, not just the exit code.
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

# Classify one child from what system() left behind.
# $? holds the wait status: exit code in the high bits, signal in the low 7 bits.
sub classify {
    my ($rc) = @_;
    my $wait = $?;

    return ('notfound', -1) if $rc == -1 || $wait == -1;    # never executed
    my $signal = $wait & 127;
    return ('signalled', $signal) if $signal;               # killed by a signal
    my $code = $wait >> 8;
    return ($code == 0 ? 'ok' : 'failed', $code);
}

my (@rows, $ok, $failed, $signalled, $notfound);
$ok = $failed = $signalled = $notfound = 0;

for my $probe (@probes) {
    my ($id, $kind, $arg) = @$probe;
    my ($status, $detail);

    if ($kind eq 'exit') {
        system('python3', '-c', 'import sys; sys.exit(int(sys.argv[1]))', $arg);
        ($status, $detail) = classify($?);
    }
    elsif ($kind eq 'signal') {
        system('python3', '-c', 'import os, signal, sys; os.kill(os.getpid(), int(sys.argv[1]))', $arg);
        ($status, $detail) = classify($?);
    }
    elsif ($kind eq 'missing') {
        my $rc;
        {
            no warnings 'exec';
            $rc = system($arg);                             # no shell: a direct exec
        }
        ($status, $detail) = classify($rc);
    }
    else {
        die "unknown probe kind: $kind\n";
    }

    if    ($status eq 'ok')        { $ok++ }
    elsif ($status eq 'failed')     { $failed++ }
    elsif ($status eq 'signalled')  { $signalled++ }
    else                            { $notfound++ }

    push @rows, [ $id, $kind, $status, $detail ];
}

open my $out, '>', "$OUT/results.csv" or die "cannot write results.csv: $!\n";
print {$out} "id,kind,status,detail\n";
for my $row (@rows) {
    print {$out} join(',', @$row), "\n";
}
close $out;

open my $sum, '>', "$OUT/summary.json" or die "cannot write summary.json: $!\n";
printf {$sum} "{\"probes\":%d,\"ok\":%d,\"failed\":%d,\"signalled\":%d,\"notfound\":%d}\n",
    scalar(@rows), $ok, $failed, $signalled, $notfound;
close $sum;
