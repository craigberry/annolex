use strict;

my $file = shift @ARGV;

open my $fh, '<:utf8', $file or die "Could not open $file: $!";

my $line = <$fh>;
chomp $line;
my @fields = split /\t/, $line;
my (@field_lengths, @all_digits);

for (1..scalar(@fields)) {
    push @field_lengths, 0;
    push @all_digits, 1;
}



while ($line = <$fh>) {
    chomp $line;
    my @f = split /\t/, $line;
    for (my $i = 0; $i < scalar(@f); $i++) {
        my $len = length($f[$i]);
        $field_lengths[$i] = $len if $len > $field_lengths[$i];
        $all_digits[$i] = 0 if $all_digits[$i] && $f[$i] =~ m/[^\d]/;
    }
}

for (my $i = 0; $i < scalar(@fields); $i++) {
    if ($all_digits[$i]) {
        print '    ' . $fields[$i] . ' = models.IntegerField()'. "\n";
    }
    else {
        print '    ' . $fields[$i] . ' = models.CharField(max_length=' . $field_lengths[$i] . ")\n";
    }
}
