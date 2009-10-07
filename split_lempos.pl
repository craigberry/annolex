use strict;

my $file = shift @ARGV;
my $outfile = $file;
$outfile =~ s/.txt/_split.txt/;

open my $fh, '<:utf8', $file or die "Could not open $file: $!";
open my $outfh, '>:utf8', $outfile or die "Could not open $outfile $!";

while (my $line = <$fh>) {
    chomp $line;
    my @f = split /\t/, $line;
    my ($lemma, $pos) = split /_/, $f[3];
    my $outline = join("\t", @f[0..2], $lemma, $pos, @f[4..5]);
    printf $outfh "$outline\n";
}

