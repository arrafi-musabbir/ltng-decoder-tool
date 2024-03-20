package TestTools;

use strict;
use warnings;
use Exporter;
use Cwd 'realpath';
use File::Basename;
use File::Spec;

use constant EXIT_CODE_OK => 0;
use constant EXIT_CODE_NO_JAVA_FOUND => 101;
use constant EXIT_CODE_NO_INSTALLATION_DIRECTORY_FOUND => 102;
use constant EXIT_CODE_NO_VALID_DEBUG_PORT => 103;

our @ISA = qw(Exporter);

# these CAN be exported.
our @EXPORT_OK = qw(startup);

# these are exported by default.
our @EXPORT = qw(startup);

our $isCygwin = (`uname` =~ m/cyg/i);
our $install_directory;
our $app;
our $product;
our $debug = 0;
our $suspend = "n";

sub startup {
    our $product = shift;
    our $app = shift;
    get_installation_directory();

    my $java_binary = get_java_binary();
    my @jarnames = get_jarnames();
    my $classpath = get_classpath(@jarnames);

    my @cmd = ($java_binary, "-cp", $classpath);
    my @args = process_args();
    if ($debug) {
        push(@cmd, "-agentlib:jdwp=transport=dt_socket,server=y,suspend=" . $suspend . ",address=" . $debug);
    }
    push(@cmd, $app);

    #    print join(" ", map qq("$_"), @cmd, @args) . "\n";
    exec(@cmd, @args);

    exit EXIT_CODE_OK;
}

sub process_args {
    my @args;
    my $pathpattern = "^/";
    my $isdebugarg = 0;

    foreach my $arg (@ARGV) {
        if ($arg eq "--debug") {
            $isdebugarg = 1;
        }
        elsif ($arg eq "--suspend") {
            $suspend = "y";
        }
        elsif ($isdebugarg) {
            if (!($arg =~ m/^[0-9]*$/) || ($arg < 0) || ($arg > 65535)) {
                print "$arg is not a valid debug port!\n";
                exit EXIT_CODE_NO_VALID_DEBUG_PORT;
            }
            $debug = $arg;
            $isdebugarg = 0;
        }
        elsif ($isCygwin && ($arg =~ m/$pathpattern/)) {
            my $path = `cygpath -wp -- "$arg"`;
            chomp($path);
            push(@args, $path);
        }
        else {
            push(@args, $arg);
        }
    }
    return @args;
}

sub get_jarnames {
    open(FILE, $install_directory . "/etc/" . $product . ".classpath");
    my @jarnames = (<FILE>);
    close(FILE);
    @jarnames = split(':', $jarnames[0]);
    return @jarnames;
}
sub check_installation_directory {
    return (-e $install_directory . "/etc/" . $product . ".classpath");
}

sub get_installation_directory {
    our $install_directory = dirname(dirname(realpath($0)));
    if (check_installation_directory()) {
        return;
    }
    $install_directory = dirname(realpath($0)) . "/tools/" . $product;
    if (check_installation_directory()) {
        return;
    }
    print "\nERROR: Unable to locate installation directory\n";
    exit EXIT_CODE_NO_INSTALLATION_DIRECTORY_FOUND;
}
# Check current Java version
sub get_java_binary {
    my $min_version = 11;
    my $java_binary = `which java 2> /dev/null`;

    chomp($java_binary);

    if (-e $java_binary) {
        my $cmd = "\"" . $java_binary . "\" -version 2>&1";
        my $output = `$cmd`;
        if ($output =~ /version "(\d+)/) {
            my $java_version = $1;
            if ($java_version >= $min_version) {
                return $java_binary;
            }
        }
    }

    # Check AFS
    my $java_afs_path = "/app/vbuild/RHEL7-x86_64/jdk/11.0.1-1/bin/java";

    if (-e $java_afs_path) {
        return $java_afs_path;
    }

    # Check TWH
    my $os = "RHE64-7";

    if ((exists $ENV{'vulcanOSbase'}) && ($ENV{'vulcanOSbase'} ne "")) {
        $os = $ENV{'vulcanOSbase'};
    }

    my $java_twh_path = "/opt/tools/wh/dtd/" . $os . "/jdk/11.0.11/bin/java";

    if (-e $java_twh_path) {
        return $java_twh_path;
    }

    # No valid Java found
    print "\nERROR: Unable to locate valid Java version (minimum version $min_version required)\n";
    exit EXIT_CODE_NO_JAVA_FOUND;
}

sub get_classpath {
    my @jarnames = @_;
    my @jarfiles;

    foreach my $jarname (@jarnames) {
        push(@jarfiles, File::Spec->catdir($install_directory, $jarname));
    }

    my $classpath = join(":", @jarfiles);
    if ($isCygwin) {
        $classpath = `cygpath -mp -- "$classpath"`;
        chomp($classpath);
    }
    return $classpath;
}

1;
