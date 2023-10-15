# DPROT - Lab 1 - RC4 attack

## Paper and pencil work
TODO:

## Comment your code
So first of all, we create a function to read the `*.dat` files and store it's values in two vectors, one for the IV and the other for the cyphertext. We could have just created a vector with pairs but it doesn't really matter as they will go hand-by-hand all the time.

At the main function we will iterate of the contents of those files, one by one, and simulate the attack while storing the keys and the message guessed.

For the attack phase, we check if the IV array has the form
<pre>iv=<b>01</b>FFx</pre> where X is the value of the last byte. If that's the case, then we do `c[0] XOR (x+2)`.

## Execution traces


## Message and key guess
