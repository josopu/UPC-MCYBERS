# Unit 2 - NetFlow Exercice

## Exercise 1

1. Install nfdump and softflowd
   > sudo apt install nfdump softflowd

1. Set up NetFlow collector using '`nfcapd`'. The collector should listen to NetFlow data at `127.0.0.1:9995`
   > `nfcapd` is installed with `nfdump` installation so it's already on our system. With `man nfcapd` we can notice that the option `-p` let's you select the port number, the option `-b` specifies the listening address and the option `-w` sets the output directory to store the flows: <br>
   '`nfcapd -p 9995 -l 127.0.0.1 -w nfcapd-data`' is the desired command, where 'nfcapd-data' is a folder in the cwd

1. Set up NetFlow exporter using '`softflowd`'
   > `sudo softflowd -d -D -v 5 -n 127.0.0.1:9995 -i eth0` <br>
   Flags: <br>
         &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`-n`: host:port <br>
         &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`-i`: interface <br>
         &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`-D`: debug mode (this implies `-d`) <br>
         &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`-d`: do not fork and deamonise (redundant cause of `-D`) <br>
         &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`-v`: NetFlow version for exporting the data <br>

1. Use '`nfdump`' to inspect the flows collected and show top 20 IPaddr by bytes.
   > `nfdump -R nfcapd-data -s ip/bytes -n 20` <br>
   Flags: <br>
         &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`-R`: filelist <br>
         &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`-s`: statistic options <br>
         &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`-n`: number to be printed <br>

      ![nfdump](ex1.4.png "nfdump and other command")

1. Configure nfcapd/softflowd to use a sampling rate of 1/10
   > To use '`nfcapd`' at a sampling rate of 1/10 just add `-s 10`: <br>
   `nfcapd -p 9995 -l 127.0.0.1 -w nfcapd-data -s 10` <br>
   To set '`softflowd`' at the same sampling rate, add the same flag and samplign rate: <br>
   `sudo softflowd -d -D -v 5 -n 127.0.0.1:9995 -i eth0 -s 10`

1. Install NfSen and use it to display NetFlow data graphically 


## Exercice 2

1. Repeat exercise 1 but now using nprobe as flow collector (instead of ncapd) and ntopng as (a graphical) flow analyzer (instead of nfdump/nfsen)
   > Opted to install it via docker: <br>
   First we start nprobe, as ntopng depends on it.
   `docker run -it --net=host ntop/nprobe.dev --ntopng "tcp://*:5556" -i eth0 -n none -T "@NTOPNG@"` <br>
   Docker flags: <br>
         &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`-it`: Run interactively and attached to the TTY <br>
         &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`--net=host`: Tells docker to use host's network inside the container <br>
   Container flags: <br>
         &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`--ntopng "tcp://*:5556"`: Opens communication with ntopng at this TCP port <br>
         &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`-i eth0`: Network interface for nprobe to capture traffic from <br>
         &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`-n none`: Capture moded, none indicates nprobe to act only as a collector <br>
         &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;` -T "@NTOPNG@"`: Tells nprobe the minimum fields it has to expord in order to ensure interoperability with ntopng <br>
   Then, we can run ntopng. <br>
   `docker run -it --net=host ntop/ntopng.dev -i "tcp://127.0.0.1:5556"` <br>
   Container flags: <br>
         &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`-i "tcp://127.0.0.1:5556"`: Sets input for ntopng <br>

   ![ntopng](ex2.1.png "ntopng and docker commands")

1. Repeat Exercise 2 but now reading the data directly from the NIC in promiscuous mode
   > Now we just need `ntopng` in promiscuous mode
   `docker run -it --net=host ntop/ntopng.dev -i eth0`
   It will use `pcap` to read packets from `eth0`

   ![ntopng2](ex2.2.png "ntopng as promiscuous mode")