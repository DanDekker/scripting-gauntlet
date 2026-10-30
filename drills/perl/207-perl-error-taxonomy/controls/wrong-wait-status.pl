#!/usr/bin/env perl
# Plausible bug: reports the raw wait status from system() as the exit code,
# so a child that exited 3 is reported as 768.
use strict;
use warnings;

my $IN  = $ENV{IN}  or die "IN not set\n";
my $OUT = $ENV{OUT} or die "OUT not set\n";

open my $pfh, '<', "$IN/probes.csv" or die "cannot read probes.csv: $!\n";
my $header = <$pfh>;
my @probes;
while (my $line = <$pfh>) {
    chomp $line;
    next if $line eq '';
    push @probes, [ split /,/, $line, -1 ];
}
close $pfh;

my @rows;
my $failed = 0;

for my $probe (@probes) {
    my ($id, $kind, $arg) = @$probe;
    my ($status, $detail);

    if ($kind eq 'exit') {
        my $wait_status = system('python3', '-c', 'import sys; sys.exit(int(sys.argv[1]))', $arg);
        # BUG: this is the wait status, not the exit code.
        $detail = $wait_status;
        $status = ($wait_status == 0) ? 'ok' : 'failed';
    }
    elsif ($kind eq 'die') {
        eval { die "$arg\n" };
        my $message = $@;
        $message = '' unless defined $message;
        $message =~ s/\n\z//;
        $status = 'failed';
        $detail = $message;
    }
    elsif ($kind eq 'open') {
        if (open my $fh, '<', "$IN/$arg") {
            close $fh;
            $status = 'ok';
            $detail = 0;
        }
        else {
            my $errno = $! + 0;
            $status = 'failed';
            $detail = $errno;
        }
    }
    else {
        die "unknown probe kind: $kind\n";
    }

    $failed++ if $status eq 'failed';
    push @rows, [ $id, $kind, $status, $detail ];
}

open my $out, '>', "$OUT/results.csv" or die "cannot write results.csv: $!\n";
print {$out} "id,kind,status,detail\n";
for my $r (@rows) {
    print {$out} join(',', @$r), "\n";
}
close $out;

open my $sum, '>', "$OUT/summary.json" or die "cannot write summary.json: $!\n";
printf {$sum} "{\"probes\":%d,\"failed\":%d,\"ok\":%d}\n",
    scalar(@rows), $failed, scalar(@rows) - $failed;
close $sum;
