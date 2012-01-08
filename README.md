# overview

this is a project i did for my cs308s computer security course at university of texas.  the goal was to explore the security of the [square credit card reader][square].  i believe the project was a success because i found a few different attack vectors, one of which seemed particularly relevant.  the attack vectors and implementation details are available in the report.

### tl;dr

as far as i can tell, there's nothing stopping another app from listening to a credit card swipe in the background.  that means you could process a payment in the square app, and a malicious app could be skimming your credit card number in the background with no visible indication.

is it possible for this to happen in the wild?  certainly.  likely?  probably not.  the important thing is that it doesn't look like there are easy means of preventing the exploit.  it would be extremely difficult to produce an unpowered encrypted card reader, so square would have to hope for an update to the ios api.

# project details

### shortcomings

the biggest shortcoming of the project is that i did not have an apple developer account, so all of my results are based on the ios simulator.  i would love to hear about others' experiences reproducing these results on actual hardware.

another significant shortcoming of the project is the error handling.  like most school projects, the focus was not on writing robust software, so ymmv with the analog-to-digital conversion code.

### running the implementation

the project has several non-insignificant requirements:

- xcode 4
- python 2.7 (though 2.6 _may_ work…)
- [scipy]
- a square credit card reader (free from [the website][square])
- an [audio adapter][adapter] if, like me, you're too cheap to get the apple developer account

once your system has the pre-requisites, you can decode card numbers yourself by connecting the card reader to your laptop via the adapter, firing up the server from the project directory by running:

    $ ./server.py

and then compiling and running the 'Crooked' ios app in xcode.  it's pretty rough, but if you start recording, swipe the card, and then stop recording, it sends the audio to the server, and recieves and displays the decoded number.

### the report title

the report title is a nod to some [fascinating work by Hovav Shacham][geometry], which gets its title from a [bob dylan tune][dylan].

[square]: https://squareup.com/
[SciPy]: http://www.scipy.org/
[adapter]: http://www.amazon.com/gp/product/B00332DPDG/ref=oh_o00_s00_i00_details
[geometry]: https://encrypted.google.com/url?sa=t&rct=j&q=the%20geometry%20of%20innocent%20flesh%20on%20the%20bone&source=web&cd=1&ved=0CBwQFjAA&url=http%3A%2F%2Fcseweb.ucsd.edu%2F~hovav%2Fdist%2Fgeometry.pdf&ei=qe4JT5LiOsvjsQK695GRCg&usg=AFQjCNGm9EU0vgkdW5Ew1ejOUj4JYdsrxw&sig2=VtMbBVmWZ9gXj6ZIY0c9Mw
[dylan]: http://en.wikipedia.org/wiki/Tombstone_Blues