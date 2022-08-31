# Generate Network Upgrade Schedule

The [Generate Network Upgrade Schedule Plug-in](generate_upgrade_schedule.py) queries a given network and generates a network update schedule for the nodes.  The output can be formatted and used with the indy-cli `ledger pool-upgrade` command

## How To Use
`./run.sh --net sbn --seed <seed> --raw --upgrade-schedule --upgrade-start "2022-08-13T05:00:00-0700"`

`--raw`:
- Outputs the result as raw unformatted json with no whitespace.

`--upgrade-schedule`:
- enables the plug-in.

`--upgrade-start`:
- defines the start day and time for the upgrade.  The time must be specified in the form yyyy-mm-ddTHH:MM:SSz; for example 2022-08-13T05:00:00-0700 to schedule the first upgrade for August 13, 2022 @ 05:00 PDT (12:00 UTC)

`--upgrade-interval`:
- Optional.  The time in minutes between each node's upgrade schedule.  Default is 5 minutes.

## Example Print Out
```
{"GrHM6eSURUvJAGAuAKDrmRod74KeTpqtqUJCctajWsWr"2022-08-13T05:00:00-0700","D1z9xZXntfphcCP3wjQTjw869ZuEhtucdSFojogb328E"2022-08-13T05:05:00-0700","7cC4Uo4UxfddPndhx5Qs76PUc999m1de3EEtb9QSFvhA"2022-08-13T05:10:00-0700","3xRW7MtVMHRKcrTPyJwAFCrynoKH7JbV5B7sTZzmq7mD"2022-08-13T05:15:00-0700","GVvdyd7Y6hsBEy5yDDHjqkXgH8zW34K74RsxUiUCZDCE"2022-08-13T05:20:00-0700","5aNBs6DToRDNuXamiswdvPhvoGxoLbdEL5XTLdZrv6Xf"2022-08-13T05:25:00-0700","t2LeEE7c4BkdwpzqT1z3sBssrzSrFVKhe13v3Mtuirw"2022-08-13T05:30:00-0700","8kwxd1DwUFr2v27nSiEC7gexa1bjkUuAm7JsfJ49bzTE"2022-08-13T05:35:00-0700","3f37va9HbQVxBGqt6U7227Cnh4WezkNGKqYZrbLEWpUp"2022-08-13T05:40:00-0700","52muwfE7EjTGDKxiQCYWr58D8BcrgyKVjhHgRQdaLiMw"2022-08-13T05:45:00-0700","CLMKi7oBYH2HzTosvdTPGiM8UXBAE2PQQuC2y97LZWgf"2022-08-13T05:50:00-0700","GnuKuvbdcY9ZU3GwvUYzEo3z5nmh1BhJ8BrrsASQM1Fi"2022-08-13T05:55:00-0700","FCLZXHPFAbARuu1vSp26bhFaNQz9sveL1QWvo2KDZjwb"2022-08-13T06:00:00-0700","5QDFnybgDHeQyBuaiKBsJ1o1Pxf83FNanaUPfRQp7N2d"2022-08-13T06:05:00-0700","5YwvqQySsNSPPM2RRQWGJeuiGgcCG5uD9NvQRR7ASJac"2022-08-13T06:10:00-0700","DXn8PUYKZZkq8gC7CZ2PqwECzUs2bpxYiA5TWgoYARa7"2022-08-13T06:15:00-0700"}
```