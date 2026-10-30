#!/usr/bin/env perl
# 207-perl-error-taxonomy — one error variable per kind of failure.
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
        system('python3', '-c', 'import sys; sys.exit(int(sys.argv[1]))', $arg);
        my $exit_code = $? >> 8;          # $? is the wait status
        $status  = ($exit_code == 0) ? 'ok' : 'failed';
        $detail  = $exit_code;
    }
    elsif ($kind eq 'die') {
        eval { die "$arg\n" };
        my $message = $@;                 # capture before the next eval
        $message = '' unless defined $message;
        $message =~ s/\n\z//;
        $status = 'failed';
        $detail = $message;
    }
    elsif ($kind eq 'open') {
        if (open my $fh, '<', "$IN/$arg") {
            close $fh;
            $status = 'ok';
            $detail = 0;                  # no errno: nothing failed
        }
        else {
            my $errno = $! + 0;           # $! right after the failed open
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
