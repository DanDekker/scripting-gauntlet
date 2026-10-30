#!/usr/bin/env perl
# 227-perl-env-override — scope each override with local $ENV{...}.
use strict;
use warnings;

my $IN  = $ENV{IN}  or die "IN not set\n";
my $OUT = $ENV{OUT} or die "OUT not set\n";

my $CHILD = 'print exists $ENV{$ARGV[0]} ? "=$ENV{$ARGV[0]}" : "unset"';

my @steps;
{
    open my $fh, '<', "$IN/steps.csv" or die "cannot read steps.csv: $!\n";
    my $header = <$fh>;
    while (my $line = <$fh>) {
        chomp $line;
        next if $line eq '';
        push @steps, [ split /,/, $line, -1 ];
    }
    close $fh;
}

sub child_sees {
    my ($var) = @_;
    open my $fh, '-|', 'perl', '-e', $CHILD, $var
        or die "cannot run child: $!\n";
    my $out = do { local $/; <$fh> };
    close $fh;
    return defined $out ? $out : 'unset';
}

my (@rows, $seen_set, $leaked);
$seen_set = 0;
$leaked   = 0;

# The contract says these names start out absent; make that true even if the
# environment we inherited already had them.
for my $step (@steps) {
    delete $ENV{ $step->[1] };
}

for my $step (@steps) {
    my ($id, $set_var, $value, $watch) = @$step;
    my $seen;

    {
        # local scopes the override to this block and restores the old state on exit.
        local $ENV{$set_var} = $value;
        $seen = child_sees($watch);
    }

    my $after = exists $ENV{$set_var} ? "=$ENV{$set_var}" : 'unset';
    $seen_set++ if $seen ne 'unset';
    $leaked++   if $after ne 'unset';

    push @rows, [ $id, $set_var, $value, $watch, $seen, $after ];
}

open my $out, '>', "$OUT/steps.csv" or die "cannot write steps.csv: $!\n";
print {$out} "id,set_var,value,watch_var,seen,after\n";
for my $row (@rows) {
    print {$out} join(',', @$row), "\n";
}
close $out;

open my $sum, '>', "$OUT/summary.json" or die "cannot write summary.json: $!\n";
printf {$sum} "{\"steps\":%d,\"seen_set\":%d,\"leaked\":%d}\n",
    scalar(@rows), $seen_set, $leaked;
close $sum;
