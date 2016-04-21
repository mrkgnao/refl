So I decided that chunking would be good.
It took me the better part of 21/4 to implement this, but eventually I could send strings in chunks.
The problem was that speed had decreased. A lot. It was now about 0.12 MB/s. Not good, of course.

I realised that the problem was the chunk size. 8 KiB isn't a lot. I had to rewrite some code to increase it to 512 KiB (since I was sending the size as a packed C unsigned short, and 1024 * 512 > 65536 obviously), but that immediately pushed speeds to a sort of consistent 10.9 MB/s. Good, but still too slow by about an order of magnitude. I mean, I'm talking to localhost here. There might be some IP resolving nonsense, but it can't take that long!

It was around this time that I first thought of opening multiple connections to the client and transferring data over each of them simultaneously. (That is, of course, one of the main ideas behind the BitTorrent protocol.)

Enter cProfile. cProfile is the standard/recommended profiler for Python (the native `profile` module apparently adds too much overhead, according to the official Python docs).
