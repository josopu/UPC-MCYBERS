# Unit 2 - NetFlow Exercice

## Exercise 1

1. Install nfdump and softflowd
   > sudo apt install nfdump softflowd

1. Set up NetFlow collector using '`nfcapd`'. The collector should listen to NetFlow data at `127.0.0.1:9995`
   > `nfcapd` is installed with `nfdump` installation so it's already on our system. With `man nfcapd` we can notice that the option `-p` let's you select the port number and, the option `-l` specifies the listening address: <br>
   '`nfcapd -p 9995 -l 127.0.0.1`' is the desired command but it says that there is no source configurations found.